"""One-time email verification delivery and code hashing."""

from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import hashlib
import secrets
import smtplib

from fastapi import HTTPException

from app.core.config import settings


def new_verification_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_verification_code(code: str) -> str:
    return hashlib.sha256(code.encode("ascii")).hexdigest()


def code_expiry() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=10)


def send_verification_email(recipient: str, code: str) -> None:
    if not all((settings.mail_server, settings.mail_username, settings.mail_password, settings.mail_from)):
        raise HTTPException(status_code=503, detail="Chức năng gửi mã chưa được cấu hình. Vui lòng liên hệ cửa hàng.")

    message = EmailMessage()
    message["Subject"] = "Mã xác minh tài khoản ECO-LOOP"
    message["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
    message["To"] = recipient
    message.set_content(
        f"Xin chào,\n\nMã xác minh ECO-LOOP của bạn là: {code}\n"
        "Mã có hiệu lực trong 10 phút và chỉ sử dụng một lần. Nếu bạn không yêu cầu, hãy bỏ qua email này.\n\nECO-LOOP"
    )
    try:
        smtp_password = "".join(settings.mail_password.get_secret_value().split())
        if settings.mail_use_ssl or settings.mail_port == 465:
            smtp_client = smtplib.SMTP_SSL(settings.mail_server, settings.mail_port, timeout=15)
        else:
            smtp_client = smtplib.SMTP(settings.mail_server, settings.mail_port, timeout=15)
        with smtp_client as smtp:
            if not settings.mail_use_ssl and settings.mail_port != 465:
                smtp.starttls()
            smtp.login(settings.mail_username, smtp_password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise HTTPException(status_code=502, detail="Không gửi được email xác minh. Hãy thử gửi lại sau.") from exc
