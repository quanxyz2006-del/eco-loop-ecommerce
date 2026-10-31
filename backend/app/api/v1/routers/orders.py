"""Cart checkout and order tracking endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.responses import success
from app.models import OrderStatus, User
from app.schemas.commerce import OrderInput, OrderStatusInput
from app.services import storefront

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/coupon")
def check_coupon(code: str, db: Session = Depends(get_db)):
    return success(storefront.validate_coupon(db, code), "Mã ưu đãi hợp lệ.")


@router.post("", status_code=status.HTTP_201_CREATED)
def place_order(
    payload: OrderInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return success(storefront.create_order(db, payload, user), "Đặt hàng thành công.")


@router.get("")
def orders(
    _: User = Depends(require_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return success(storefront.admin_orders(db, page, limit, status_filter))


@router.get("/mine")
def my_orders(
    user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return success(storefront.customer_orders(db, user, page, limit))


@router.get("/{order_code}")
def order_status(order_code: str, db: Session = Depends(get_db)):
    return success(storefront.lookup_order(db, order_code))


@router.patch("/{order_id}/status")
def set_order_status(
    order_id: int,
    payload: OrderStatusInput,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return success(storefront.update_order_status(db, order_id, payload), "Cập nhật trạng thái đơn hàng thành công.")
