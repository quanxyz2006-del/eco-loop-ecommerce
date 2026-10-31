"""Product and category endpoints."""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.responses import success
from app.models import Product, ProductReview, User
from app.schemas.commerce import CategoryInput, ProductInput, ProductReviewInput, ProductUpdate
from app.services import storefront

router = APIRouter(tags=["Catalog"])


@router.get("/products/{product_id}/reviews")
def product_reviews(product_id: int, db: Session = Depends(get_db)):
    if not db.get(Product, product_id):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    rows = db.execute(select(ProductReview, User.full_name).join(User).where(
        ProductReview.product_id == product_id).order_by(ProductReview.created_at.desc())).all()
    total = len(rows)
    average = round(sum(row.ProductReview.rating for row in rows) / total, 1) if total else 0
    return success({"average": average, "count": total, "items": [
        {"rating": review.rating, "content": review.content, "created_at": review.created_at, "full_name": name}
        for review, name in rows
    ]})


@router.post("/products/{product_id}/reviews")
def save_product_review(product_id: int, payload: ProductReviewInput,
                        user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from fastapi import HTTPException
    if not db.get(Product, product_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    review = db.scalar(select(ProductReview).where(
        ProductReview.product_id == product_id, ProductReview.user_id == user.id))
    if review is None:
        review = ProductReview(product_id=product_id, user_id=user.id, rating=payload.rating, content=payload.content)
        db.add(review)
    else:
        review.rating = payload.rating
        review.content = payload.content
    db.commit()
    return success({"rating": review.rating, "content": review.content}, "Đã lưu đánh giá của bạn.")


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return success(storefront.list_categories(db))


@router.post("/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryInput, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.create_category(db, payload), "Tạo danh mục thành công.")


@router.get("/products")
def products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=12, ge=1, le=100),
    category_id: int | None = Query(default=None, gt=0),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    material_eco_type: str | None = Query(default=None, max_length=100),
    search: str | None = Query(default=None, max_length=150),
    db: Session = Depends(get_db),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Giá thấp nhất không được lớn hơn giá cao nhất.")
    return success(storefront.list_products(db, page, limit, category_id, min_price, max_price, material_eco_type, search))


@router.get("/products/admin/all")
def all_products(
    _: User = Depends(require_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return success(storefront.list_products(db, page, limit, include_inactive=True))


@router.get("/products/{identifier}")
def product_detail(identifier: str, db: Session = Depends(get_db)):
    return success(storefront.get_product(db, identifier))


@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductInput, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.create_product(db, payload), "Tạo sản phẩm thành công.")


@router.put("/products/{product_id}")
def update_product(product_id: int, payload: ProductUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.update_product(db, product_id, payload), "Cập nhật sản phẩm thành công.")


@router.patch("/products/{product_id}/toggle-status")
def toggle_product(product_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.toggle_product(db, product_id), "Đã đổi trạng thái sản phẩm.")


@router.delete("/products/{product_id}")
def delete_product(product_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.delete_product(db, product_id), "Đã ẩn sản phẩm.")
