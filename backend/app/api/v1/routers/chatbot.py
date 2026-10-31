"""Grounded ECO-LOOP customer support assistant powered by Gemini."""

from collections import defaultdict, deque
import logging
import threading
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from google import genai
from google.genai import types
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.responses import success
from app.models import Product
from app.schemas.commerce import ChatMessageInput

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chatbot", tags=["Customer support"])

SYSTEM_INSTRUCTION = """Bạn là trợ lý chăm sóc khách hàng của ECO-LOOP, một cửa hàng demo thời trang tuần hoàn ở Việt Nam.
Chỉ trả lời bằng tiếng Việt, lịch sự, súc tích, dễ hiểu. Dùng phần DỮ LIỆU CỬA HÀNG trong yêu cầu làm nguồn sự thật; không tự bịa chính sách, phí giao hàng, thời gian giao, địa chỉ cửa hàng, hướng dẫn chuyển khoản, tồn kho, chứng nhận hoặc kết quả môi trường.
Nếu thông tin chưa có, hãy nói rõ chưa có dữ liệu và hướng dẫn khách liên hệ Zalo 0966618840 hoặc email quanxyz2006@gmail.com. Không yêu cầu khách gửi mật khẩu, mã OTP, số thẻ hoặc thông tin thanh toán nhạy cảm.
Thông tin sản phẩm, giá, tồn kho và chỉ số CO₂ của catalog là dữ liệu mẫu minh họa, chưa được kiểm định LCA. Thu cũ đổi mới cần cửa hàng duyệt; chỉ sau khi duyệt mới cấp voucher giảm 10%, dùng một lần. Website hỗ trợ COD và lựa chọn chuyển khoản; không khẳng định đã tích hợp cổng thanh toán trực tuyến.
Khách cần đăng ký/đăng nhập để đặt hàng; có thể tạo tài khoản tại /account.html. Đơn đã đặt tra cứu bằng mã đơn; chatbot không xem được dữ liệu riêng tư hoặc trạng thái đơn của từng khách.
Chỉ hỗ trợ câu hỏi về ECO-LOOP, sản phẩm, mua hàng, tài khoản, thu cũ đổi mới, bài viết và liên hệ. Với câu hỏi ngoài phạm vi, lịch sự giới hạn phạm vi và đề xuất liên hệ cửa hàng."""

_requests_by_ip: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = threading.Lock()
_RATE_LIMIT = 10
_RATE_WINDOW_SECONDS = 60


def _enforce_rate_limit(client_ip: str) -> None:
    now = time.monotonic()
    with _rate_lock:
        requests = _requests_by_ip[client_ip]
        while requests and now - requests[0] >= _RATE_WINDOW_SECONDS:
            requests.popleft()
        if len(requests) >= _RATE_LIMIT:
            raise HTTPException(status_code=429, detail="Bạn gửi hơi nhanh. Vui lòng thử lại sau một phút.")
        requests.append(now)


def _store_context(db: Session) -> str:
    products = db.scalars(
        select(Product).where(Product.is_active.is_(True)).order_by(Product.name).limit(40)
    ).all()
    product_lines = []
    for product in products:
        price = product.discount_price or product.price
        product_lines.append(
            f"- {product.name} | danh mục: {product.category.name} | giá hiện tại: {price:,.0f} VND"
            f" | còn: {product.stock_quantity} | chất liệu demo: {product.material_eco_type or 'chưa cập nhật'}"
        )
    catalog = "\n".join(product_lines) if product_lines else "Catalog hiện chưa có sản phẩm đang bán."
    return (
        "Cửa hàng: ECO-LOOP, website demo bán thời trang và tiếp nhận đăng ký thu cũ đổi mới.\n"
        "Liên hệ: Zalo 0966618840; email quanxyz2006@gmail.com.\n"
        "Đăng ký/đăng nhập: /account.html. Thanh toán khi nhận hàng (COD) hoặc chọn chuyển khoản;"
        " website chưa tích hợp cổng thanh toán trực tuyến. Phí và thời gian giao hàng do cửa hàng xác nhận.\n"
        "Thu cũ: khách gửi yêu cầu trên trang /trade-in.html, cửa hàng kiểm tra và duyệt;"
        " yêu cầu được duyệt nhận voucher REWEAR10 giảm 10%, chỉ dùng một lần.\n"
        "Chỉ số CO2 và tuyên bố vật liệu trong sản phẩm mẫu không phải kết quả LCA hay chứng nhận.\n"
        f"SẢN PHẨM ĐANG BÁN:\n{catalog}"
    )


def _local_fallback(message: str, context: str) -> str:
    normalized = message.casefold()
    if any(term in normalized for term in ("zalo", "liên hệ", "email", "số điện thoại", "hotline")):
        return "Bạn có thể liên hệ ECO-LOOP qua Zalo 0966618840 hoặc email quanxyz2006@gmail.com."
    if any(term in normalized for term in ("tài khoản", "đăng ký", "đăng nhập", "thanh toán", "đặt hàng")):
        return "Bạn cần đăng ký hoặc đăng nhập tại /account.html trước khi thanh toán. Website hỗ trợ COD và lựa chọn chuyển khoản, chưa tích hợp cổng thanh toán trực tuyến."
    if any(term in normalized for term in ("thu cũ", "đổi mới", "voucher", "quần áo cũ", "thu gom")):
        return "Bạn có thể gửi yêu cầu tại /trade-in.html. Sau khi cửa hàng duyệt, bạn sẽ nhận voucher giảm 10%, dùng một lần."
    if any(term in normalized for term in ("giá", "sản phẩm", "còn hàng", "tồn kho", "chất liệu", "áo", "quần", "túi")):
        return f"Mình có thể tra cứu catalog hiện tại. {context.split('SẢN PHẨM ĐANG BÁN:', 1)[-1].strip()}"
    return "Mình chưa đủ thông tin để trả lời chính xác. Bạn vui lòng liên hệ Zalo 0966618840 hoặc email quanxyz2006@gmail.com để được hỗ trợ nhé."


@router.get("/status")
def chatbot_status():
    """Expose whether Gemini is configured without disclosing credentials."""
    return success({"configured": bool(settings.gemini_api_key), "model": settings.gemini_model})


@router.post("/message")
def send_message(
    payload: ChatMessageInput,
    request: Request,
    db: Session = Depends(get_db),
):
    """Answer a short customer-support question using live catalog facts and FAQ grounding."""
    _enforce_rate_limit(request.client.host if request.client else "unknown")
    context = _store_context(db)
    if not settings.gemini_api_key:
        return success({"reply": _local_fallback(payload.message, context), "provider": "faq"})

    history = "\n".join(
        f"{'Khách' if turn.role == 'user' else 'Trợ lý'}: {turn.content}"
        for turn in payload.history[-8:]
    )
    prompt = (
        f"DỮ LIỆU CỬA HÀNG (chỉ dùng trong cuộc hội thoại này):\n{context}\n\n"
        f"LỊCH SỬ GẦN ĐÂY:\n{history or '(chưa có)'}\n\n"
        f"CÂU HỎI MỚI CỦA KHÁCH:\n{payload.message}"
    )
    try:
        client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=500,
            ),
        )
        reply = (response.text or "").strip()
        if reply:
            return success({"reply": reply, "provider": "gemini"})
        logger.warning("Gemini chatbot returned an empty response")
    except Exception as exc:
        # Log only the exception class so prompts and credentials never enter application logs.
        logger.warning("Gemini chatbot request failed (%s)", type(exc).__name__)
    return success({"reply": _local_fallback(payload.message, context), "provider": "faq"})
