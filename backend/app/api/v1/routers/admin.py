"""Admin dashboard endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin, require_superadmin
from app.core.responses import success
from app.models import User, UserRole
from app.schemas.commerce import UserRoleInput
from app.services.serializers import user_data
from app.services.storefront import admin_summary

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/summary")
def summary(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(admin_summary(db))


@router.get("/users")
def users(_: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    accounts = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return success({"items": [user_data(account) for account in accounts]})


@router.patch("/users/{user_id}/role")
def update_user_role(user_id: int, payload: UserRoleInput,
                     owner: User = Depends(require_superadmin), db: Session = Depends(get_db)):
    account = db.get(User, user_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    if account.id == owner.id or account.email.casefold() == owner.email.casefold():
        raise HTTPException(status_code=400, detail="Không thể thay đổi quyền của tài khoản chủ sở hữu.")
    account.role = UserRole(payload.role)
    db.commit()
    db.refresh(account)
    return success(user_data(account), "Đã cập nhật quyền tài khoản.")
