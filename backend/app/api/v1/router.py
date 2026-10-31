"""Compose all version-one feature routers."""

from fastapi import APIRouter

from app.api.v1.routers import admin, auth, catalog, chatbot, content, orders, trade_ins

router = APIRouter()
router.include_router(auth.router)
router.include_router(chatbot.router)
router.include_router(catalog.router)
router.include_router(orders.router)
router.include_router(trade_ins.router)
router.include_router(content.articles_router)
router.include_router(content.contacts_router)
router.include_router(admin.router)
