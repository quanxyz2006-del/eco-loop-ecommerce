"""Validated request schemas for the storefront and admin API."""

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

from app.models.domain import ArticleCategory, OrderStatus, PaymentMethod, TradeInCondition

class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class RegisterInput(InputModel):
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=72)]
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=1000)

    @field_validator("password")
    @classmethod
    def bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được vượt quá 72 byte.")
        return value


class LoginInput(InputModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=1, max_length=72)]

    @field_validator("password")
    @classmethod
    def bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Mật khẩu không được vượt quá 72 byte.")
        return value


class VerifyEmailInput(InputModel):
    email: EmailStr
    code: Annotated[str, StringConstraints(pattern=r"^\d{6}$")]


class ResendVerificationInput(InputModel):
    email: EmailStr


class ProductReviewInput(InputModel):
    rating: int = Field(ge=1, le=5)
    content: str | None = Field(default=None, max_length=1200)


class UserRoleInput(InputModel):
    role: Literal["admin", "customer"]


class CategoryInput(InputModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    slug: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    parent_id: int | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=5000)
    is_active: bool = True


class ProductInput(InputModel):
    category_id: int = Field(gt=0)
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
    code: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=50)]
    slug: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=255)]
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    material_eco_type: str | None = Field(default=None, max_length=100)
    co2_saved_kg: float = Field(default=0, ge=0, le=100000)
    stock_quantity: int = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=5000)
    content_detail: str | None = Field(default=None, max_length=20000)
    is_active: bool = True
    images: list[str] = Field(default_factory=list, max_length=12)


class ProductUpdate(InputModel):
    category_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=2, max_length=255)
    code: str | None = Field(default=None, min_length=2, max_length=50)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    material_eco_type: str | None = Field(default=None, max_length=100)
    co2_saved_kg: float | None = Field(default=None, ge=0, le=100000)
    stock_quantity: int | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, max_length=5000)
    content_detail: str | None = Field(default=None, max_length=20000)
    is_active: bool | None = None
    images: list[str] | None = Field(default=None, max_length=12)


class OrderItemInput(InputModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50)


class OrderInput(InputModel):
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    phone: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=20)]
    shipping_address: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=1000)]
    payment_method: PaymentMethod = PaymentMethod.COD
    note: str | None = Field(default=None, max_length=1000)
    coupon_code: str | None = Field(default=None, max_length=50)
    items: list[OrderItemInput] = Field(min_length=1, max_length=30)


class OrderStatusInput(InputModel):
    status: OrderStatus


class TradeInInput(InputModel):
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    phone: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=20)]
    item_description: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=3000)]
    condition_grade: TradeInCondition
    pickup_address: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=1000)]


class TradeInStatusInput(InputModel):
    status: str = Field(pattern="^(collected|rejected)$")


class ArticleInput(InputModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=255)]
    slug: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=255)]
    category_type: ArticleCategory = ArticleCategory.NEWS
    short_summary: str | None = Field(default=None, max_length=500)
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=20, max_length=50000)]
    image_url: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)
    is_published: bool = True


class ArticleUpdate(InputModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    slug: str | None = Field(default=None, min_length=3, max_length=255)
    category_type: ArticleCategory | None = None
    short_summary: str | None = Field(default=None, max_length=500)
    content: str | None = Field(default=None, min_length=20, max_length=50000)
    image_url: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)
    is_published: bool | None = None


class ContactInput(InputModel):
    full_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=5000)]


class ContactStatusInput(InputModel):
    status: str = Field(pattern="^(new|read|replied)$")


class ChatTurn(InputModel):
    role: Literal["user", "assistant"]
    content: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1200)]


class ChatMessageInput(InputModel):
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1200)]
    history: list[ChatTurn] = Field(default_factory=list, max_length=8)
