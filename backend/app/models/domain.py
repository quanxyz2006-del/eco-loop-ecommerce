"""Database entities for the ECO-LOOP commerce platform."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SqlEnum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import LONGTEXT

from app.core.database import Base

LongText = Text().with_variant(LONGTEXT(), "mysql")

def enum_values(enum_type: type[Enum]) -> list[str]:
    """Persist lowercase wire values so ORM and the MySQL schema agree."""
    return [item.value for item in enum_type]


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class PaymentMethod(str, Enum):
    COD = "cod"
    BANK_TRANSFER = "bank_transfer"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPING = "shipping"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TradeInCondition(str, Enum):
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    WORN_OUT = "worn_out"


class TradeInStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    COLLECTED = "collected"
    REJECTED = "rejected"


class ArticleCategory(str, Enum):
    NEWS = "news"
    EVENT = "event"
    ECO_GUIDE = "eco_guide"


class ContactStatus(str, Enum):
    NEW = "new"
    READ = "read"
    REPLIED = "replied"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, values_callable=enum_values), default=UserRole.CUSTOMER)
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    green_points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["Order"]] = relationship(back_populates="user")
    trade_ins: Mapped[list["TradeIn"]] = relationship(back_populates="user")


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    sent_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)


class ProductReview(Base):
    __tablename__ = "product_reviews"
    __table_args__ = (UniqueConstraint("product_id", "user_id", name="uq_review_product_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    content: Mapped[str | None] = mapped_column(String(1200))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    parent: Mapped["Category | None"] = relationship(
        remote_side="Category.id", back_populates="children"
    )
    children: Mapped[list["Category"]] = relationship(back_populates="parent")
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("code", name="uq_products_code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    material_eco_type: Mapped[str | None] = mapped_column(String(100))
    co2_saved_kg: Mapped[float] = mapped_column(Float, default=0)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text)
    content_detail: Mapped[str | None] = mapped_column(LongText)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category: Mapped[Category] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    image_url: Mapped[str] = mapped_column(String(500))
    is_thumbnail: Mapped[bool] = mapped_column(Boolean, default=False)

    product: Mapped[Product] = relationship(back_populates="images")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    order_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    final_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_method: Mapped[PaymentMethod] = mapped_column(SqlEnum(PaymentMethod, values_callable=enum_values))
    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus, values_callable=enum_values), default=OrderStatus.PENDING, index=True
    )
    shipping_address: Mapped[str] = mapped_column(Text)
    phone: Mapped[str] = mapped_column(String(20))
    note: Mapped[str | None] = mapped_column(Text)
    coupon_code: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User | None"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="order_items")


class TradeIn(Base):
    __tablename__ = "trade_ins"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(150))
    phone: Mapped[str] = mapped_column(String(20))
    item_description: Mapped[str] = mapped_column(Text)
    condition_grade: Mapped[TradeInCondition] = mapped_column(SqlEnum(TradeInCondition, values_callable=enum_values))
    pickup_address: Mapped[str] = mapped_column(Text)
    status: Mapped[TradeInStatus] = mapped_column(
        SqlEnum(TradeInStatus, values_callable=enum_values), default=TradeInStatus.PENDING, index=True
    )
    voucher_code: Mapped[str | None] = mapped_column(String(50), unique=True)
    voucher_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User | None"] = relationship(back_populates="trade_ins")


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category_type: Mapped[ArticleCategory] = mapped_column(
        SqlEnum(ArticleCategory, values_callable=enum_values), default=ArticleCategory.NEWS, index=True
    )
    short_summary: Mapped[str | None] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(LongText)
    image_url: Mapped[str | None] = mapped_column(String(500))
    source_url: Mapped[str | None] = mapped_column(String(500))
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150))
    email: Mapped[str] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[ContactStatus] = mapped_column(
        SqlEnum(ContactStatus, values_callable=enum_values), default=ContactStatus.NEW, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
