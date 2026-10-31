"""FastAPI dependencies for sessions and role-based access control."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.models import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a signed bearer token."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Vui lòng đăng nhập để tiếp tục.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise unauthorized
    try:
        user_id = int(payload["sub"])
    except ValueError:
        raise unauthorized
    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Resolve an optional bearer user for guest-capable checkout flows."""
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token đăng nhập không hợp lệ.")
    try:
        user_id = int(payload["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Token đăng nhập không hợp lệ.") from exc
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Tài khoản không còn tồn tại.")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require an authenticated administrator account."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Bạn không có quyền quản trị.")
    return user


def require_superadmin(user: User = Depends(get_current_user)) -> User:
    """Allow only the configured owner account to manage administrator grants."""
    if user.role != UserRole.ADMIN or user.email.casefold() != settings.superadmin_email.casefold():
        raise HTTPException(status_code=403, detail="Chỉ tài khoản chủ sở hữu mới được cấp hoặc thu hồi quyền quản trị.")
    return user
