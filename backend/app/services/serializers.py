"""Convert ORM objects into stable, JSON-friendly API representations."""

from typing import Any

from app.core.config import settings
from app.models import Article, Category, Contact, Order, Product, TradeIn, User


def user_data(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "is_superadmin": user.email.casefold() == settings.superadmin_email.casefold(),
        "phone": user.phone,
        "address": user.address,
        "green_points": user.green_points,
        "created_at": user.created_at,
    }


def category_data(category: Category, include_children: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "parent_id": category.parent_id,
        "description": category.description,
        "is_active": category.is_active,
    }
    if include_children:
        data["children"] = [category_data(child) for child in category.children if child.is_active]
    return data


def product_data(product: Product) -> dict[str, Any]:
    return {
        "id": product.id,
        "category_id": product.category_id,
        "category": product.category.name if product.category else None,
        "name": product.name,
        "code": product.code,
        "slug": product.slug,
        "price": float(product.price),
        "discount_price": float(product.discount_price) if product.discount_price is not None else None,
        "material_eco_type": product.material_eco_type,
        "co2_saved_kg": product.co2_saved_kg,
        "stock_quantity": product.stock_quantity,
        "description": product.description,
        "content_detail": product.content_detail,
        "is_active": product.is_active,
        "created_at": product.created_at,
        "images": [
            {"id": image.id, "image_url": image.image_url, "is_thumbnail": image.is_thumbnail}
            for image in product.images
        ],
    }


def order_data(order: Order, private: bool = True) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": order.id,
        "order_code": order.order_code,
        "total_amount": float(order.total_amount),
        "discount_amount": float(order.discount_amount),
        "final_amount": float(order.final_amount),
        "payment_method": order.payment_method.value,
        "status": order.status.value,
        "created_at": order.created_at,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
            }
            for item in order.items
        ],
    }
    if private:
        data.update(
            {
                "full_name": order.full_name,
                "user_id": order.user_id,
                "phone": order.phone,
                "shipping_address": order.shipping_address,
                "note": order.note,
                "coupon_code": order.coupon_code,
            }
        )
    return data


def trade_in_data(request: TradeIn) -> dict[str, Any]:
    return {
        "id": request.id,
        "full_name": request.full_name,
        "phone": request.phone,
        "item_description": request.item_description,
        "condition_grade": request.condition_grade.value,
        "pickup_address": request.pickup_address,
        "status": request.status.value,
        "voucher_code": request.voucher_code,
        "voucher_used": request.voucher_used,
        "created_at": request.created_at,
    }


def article_data(article: Article) -> dict[str, Any]:
    return {
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "category_type": article.category_type.value,
        "short_summary": article.short_summary,
        "content": article.content,
        "image_url": article.image_url,
        "source_url": article.source_url,
        "views": article.views,
        "is_published": article.is_published,
        "created_at": article.created_at,
    }


def contact_data(contact: Contact) -> dict[str, Any]:
    return {
        "id": contact.id,
        "full_name": contact.full_name,
        "email": contact.email,
        "phone": contact.phone,
        "content": contact.content,
        "status": contact.status,
        "created_at": contact.created_at,
    }
