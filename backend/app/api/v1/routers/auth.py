"""Registration, login, and account endpoints."""

from datetime import datetime, timezone
import hmac

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.core.responses import success
from app.core.security import create_access_token, hash_password, verify_password
from app.models import EmailVerification, User
from app.schemas.commerce import LoginInput, RegisterInput, ResendVerificationInput, VerifyEmailInput
from app.services.email_verification import (
    code_expiry,
    hash_verification_code,
    new_verification_code,
    send_verification_email,
)
from app.services.serializers import user_data

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterInput, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    verification = db.scalar(select(EmailVerification).join(User).where(func.lower(User.email) == email))
    if user and (verification is None or verification.is_verified):
        raise HTTPException(status_code=409, detail="Email này đã được đăng ký. Hãy đăng nhập hoặc dùng email khác.")
    if user is None:
        user = User(full_name=payload.full_name, email=email, password_hash=hash_password(payload.password),
                    phone=payload.phone, address=payload.address)
        db.add(user)
        db.flush()
        verification = EmailVerification(user_id=user.id, code_hash="", expires_at=code_expiry())
        db.add(verification)
    elif verification and verification.sent_at and (datetime.now(timezone.utc).replace(tzinfo=None) - verification.sent_at).total_seconds() < 60:
        raise HTTPException(status_code=429, detail="Vui lòng chờ 60 giây trước khi gửi mã khác.")
    code = new_verification_code()
    verification.code_hash = hash_verification_code(code)
    verification.expires_at = code_expiry()
    verification.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        send_verification_email(email, code)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return success({"email": email}, "Đã gửi mã xác minh 6 số đến email. Mã có hiệu lực trong 10 phút.")


@router.post("/verify-email")
def verify_email(payload: VerifyEmailInput, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    record = db.scalar(select(EmailVerification).join(User).where(func.lower(User.email) == email))
    if record is None:
        raise HTTPException(status_code=400, detail="Không tìm thấy yêu cầu xác minh. Hãy đăng ký lại.")
    if record.is_verified:
        return success({"verified": True}, "Email đã được xác minh. Bạn có thể đăng nhập.")
    if record.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Mã đã hết hạn. Hãy yêu cầu gửi mã mới.")
    if not hmac.compare_digest(record.code_hash, hash_verification_code(payload.code)):
        raise HTTPException(status_code=400, detail="Mã xác minh không đúng. Vui lòng kiểm tra lại.")
    record.is_verified = True
    record.code_hash = ""
    db.commit()
    return success({"verified": True}, "Xác minh email thành công. Bạn có thể đăng nhập.")


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationInput, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    record = db.scalar(select(EmailVerification).where(EmailVerification.user_id == user.id)) if user else None
    if user is None or record is None or record.is_verified:
        return success(None, "Nếu email có yêu cầu xác minh đang chờ, mã mới sẽ được gửi.")
    if (datetime.now(timezone.utc).replace(tzinfo=None) - record.sent_at).total_seconds() < 60:
        raise HTTPException(status_code=429, detail="Vui lòng chờ 60 giây trước khi gửi mã khác.")
    code = new_verification_code()
    send_verification_email(email, code)
    record.code_hash = hash_verification_code(code)
    record.expires_at = code_expiry()
    record.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    return success(None, "Đã gửi mã xác minh mới.")


@router.post("/login")
def login(payload: LoginInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(func.lower(User.email) == str(payload.email).lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác.")
    verification = db.scalar(select(EmailVerification).where(EmailVerification.user_id == user.id))
    if verification is not None and not verification.is_verified:
        raise HTTPException(status_code=403, detail="Email chưa được xác minh. Hãy nhập mã xác minh trước khi đăng nhập.")
    token = create_access_token(str(user.id), user.role.value)
    return success(
        {"access_token": token, "token_type": "bearer", "user": user_data(user)},
        "Đăng nhập thành công.",
    )


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return success(user_data(user))
