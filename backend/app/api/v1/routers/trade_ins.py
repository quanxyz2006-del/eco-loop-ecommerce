"""Garment collection and trade-in endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_user, require_admin
from app.core.responses import success
from app.models import TradeInStatus, User
from app.schemas.commerce import TradeInInput, TradeInStatusInput
from app.services import storefront

router = APIRouter(prefix="/trade-in", tags=["Trade-in"])


@router.post("", status_code=status.HTTP_201_CREATED)
def submit_trade_in(
    payload: TradeInInput,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    return success(storefront.create_trade_in(db, payload, user), "Đã tiếp nhận yêu cầu thu gom.")


@router.get("")
def trade_ins(
    _: User = Depends(require_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: TradeInStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return success(storefront.list_trade_ins(db, page, limit, status_filter))


@router.patch("/{trade_in_id}/approve")
def approve_trade_in(trade_in_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.approve_trade_in(db, trade_in_id), "Đã duyệt và tạo mã ưu đãi.")


@router.patch("/{trade_in_id}/status")
def set_trade_in_status(
    trade_in_id: int,
    payload: TradeInStatusInput,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return success(storefront.update_trade_in_status(db, trade_in_id, payload), "Đã cập nhật yêu cầu thu gom.")
