"""Editorial content and customer support endpoints."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.responses import success
from app.models import ArticleCategory, User
from app.schemas.commerce import (
    ArticleInput,
    ArticleUpdate,
    ContactInput,
    ContactStatusInput,
)
from app.services import storefront

articles_router = APIRouter(prefix="/articles", tags=["Articles"])
contacts_router = APIRouter(prefix="/contacts", tags=["Contacts"])


@articles_router.get("")
def articles(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=9, ge=1, le=50),
    category_type: ArticleCategory | None = None,
    db: Session = Depends(get_db),
):
    return success(storefront.list_articles(db, page, limit, category_type))


@articles_router.get("/admin/all")
def all_articles(
    _: User = Depends(require_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return success(storefront.list_articles(db, page, limit, None, admin=True))


@articles_router.get("/{slug}")
def article_detail(slug: str, db: Session = Depends(get_db)):
    return success(storefront.get_article(db, slug))


@articles_router.post("", status_code=status.HTTP_201_CREATED)
def create_article(payload: ArticleInput, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.create_article(db, payload), "Tạo bài viết thành công.")


@articles_router.put("/{article_id}")
def update_article(article_id: int, payload: ArticleUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.update_article(db, article_id, payload), "Cập nhật bài viết thành công.")


@articles_router.delete("/{article_id}")
def delete_article(article_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    return success(storefront.delete_article(db, article_id), "Đã ẩn bài viết.")


@contacts_router.post("", status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactInput, db: Session = Depends(get_db)):
    return success(storefront.create_contact(db, payload), "Cảm ơn bạn đã liên hệ ECO-LOOP.")


@contacts_router.get("")
def contacts(
    _: User = Depends(require_admin),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=30, ge=1, le=100),
    status_filter: str | None = Query(default=None, alias="status", pattern="^(new|read|replied)$"),
    db: Session = Depends(get_db),
):
    return success(storefront.list_contacts(db, page, limit, status_filter))


@contacts_router.patch("/{contact_id}/status")
def set_contact_status(
    contact_id: int,
    payload: ContactStatusInput,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    return success(storefront.update_contact_status(db, contact_id, payload), "Đã cập nhật tin nhắn.")
