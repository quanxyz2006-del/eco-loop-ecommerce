"""Password hashing and JWT helpers."""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hash a password with bcrypt, rejecting inputs beyond bcrypt's byte limit."""
    encoded = password.encode("utf-8")
    if len(encoded) > 72:
        raise ValueError("Mật khẩu không được vượt quá 72 byte.")
    return bcrypt.hashpw(encoded, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Compare a candidate password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, role: str) -> str:
    """Create a signed short-lived access token."""
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "role": role, "exp": expires}, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, str] | None:
    """Decode a token, returning None when it is invalid or expired."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not isinstance(subject, str):
            return None
        return {"sub": subject, "role": str(payload.get("role", "customer"))}
    except JWTError:
        return None
