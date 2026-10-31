"""Catalog, order, trade-in, article, and support business operations."""

from collections import Counter
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP
import secrets
import string

from fastapi import HTTPException
from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import (
    Article,
    ArticleCategory,
    Category,
    Contact,
    ContactStatus,
    Order,
    OrderItem,
    OrderStatus,
    Product,
    ProductImage,
    TradeIn,
    TradeInCondition,
    TradeInStatus,
    User,
)
from app.schemas.commerce import (
    ArticleInput,
    ArticleUpdate,
    CategoryInput,
    ContactInput,
    ContactStatusInput,
    OrderInput,
    OrderStatusInput,
    ProductInput,
    ProductUpdate,
    TradeInInput,
    TradeInStatusInput,
)
from app.services.serializers import (
    article_data,
    category_data,
    contact_data,
    order_data,
    product_data,
    trade_in_data,
)

CENT = Decimal("0.01")


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Dữ liệu bị trùng hoặc vi phạm ràng buộc.") from exc


def list_categories(db: Session) -> list[dict]:
    roots = db.scalars(
        select(Category)
        .where(Category.parent_id.is_(None), Category.is_active.is_(True))
        .options(selectinload(Category.children))
        .order_by(Category.name)
    ).all()
    return [category_data(category, include_children=True) for category in roots]


def create_category(db: Session, payload: CategoryInput) -> dict:
    if payload.parent_id:
        parent = db.get(Category, payload.parent_id)
        if parent is None or not parent.is_active:
            raise HTTPException(status_code=404, detail="Không tìm thấy danh mục cha.")
        if parent.parent_id is not None:
            raise HTTPException(status_code=422, detail="Danh mục chỉ hỗ trợ tối đa hai cấp.")
    category = Category(**payload.model_dump())
    db.add(category)
    _commit(db)
    db.refresh(category)
    return category_data(category)


def list_products(
    db: Session,
    page: int = 1,
    limit: int = 12,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    material_eco_type: str | None = None,
    search: str | None = None,
    include_inactive: bool = False,
) -> dict:
    statement = select(Product).options(
        joinedload(Product.category), selectinload(Product.images)
    )
    filters = []
    if not include_inactive:
        filters.append(Product.is_active.is_(True))
    if category_id is not None:
        category = db.get(Category, category_id)
        if category is not None and category.parent_id is None:
            child_ids = select(Category.id).where(Category.parent_id == category_id)
            filters.append(or_(Product.category_id == category_id, Product.category_id.in_(child_ids)))
        else:
            filters.append(Product.category_id == category_id)
    actual_price = func.coalesce(Product.discount_price, Product.price)
    if min_price is not None:
        filters.append(actual_price >= min_price)
    if max_price is not None:
        filters.append(actual_price <= max_price)
    if material_eco_type:
        filters.append(Product.material_eco_type.ilike(f"%{material_eco_type.strip()}%"))
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Product.name.ilike(term), Product.description.ilike(term), Product.code.ilike(term)))
    if filters:
        statement = statement.where(*filters)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    products = db.scalars(
        statement.order_by(Product.created_at.desc(), Product.id.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).unique().all()
    return {
        "items": [product_data(item) for item in products],
        "pagination": {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1) // limit},
    }


def get_product(db: Session, identifier: str) -> dict:
    statement = select(Product).options(
        joinedload(Product.category), selectinload(Product.images)
    ).where(Product.is_active.is_(True))
    if identifier.isdecimal():
        statement = statement.where(Product.id == int(identifier))
    else:
        statement = statement.where(Product.slug == identifier)
    product = db.scalar(statement)
    if product is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    return product_data(product)


def create_product(db: Session, payload: ProductInput) -> dict:
    category = db.get(Category, payload.category_id)
    if category is None:
        raise HTTPException(status_code=422, detail="Danh mục sản phẩm không tồn tại.")
    if payload.discount_price is not None and payload.discount_price >= payload.price:
        raise HTTPException(status_code=422, detail="Giá khuyến mãi phải nhỏ hơn giá niêm yết.")
    values = payload.model_dump(exclude={"images"})
    product = Product(**values)
    product.images = [ProductImage(image_url=url, is_thumbnail=index == 0) for index, url in enumerate(payload.images)]
    db.add(product)
    _commit(db)
    saved = db.scalar(
        select(Product).options(joinedload(Product.category), selectinload(Product.images)).where(Product.id == product.id)
    )
    return product_data(saved)


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> dict:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    values = payload.model_dump(exclude_unset=True)
    images = values.pop("images", None)
    for key, value in values.items():
        setattr(product, key, value)
    final_price = values.get("price", product.price)
    final_discount = values.get("discount_price", product.discount_price)
    if final_discount is not None and final_discount >= final_price:
        raise HTTPException(status_code=422, detail="Giá khuyến mãi phải nhỏ hơn giá niêm yết.")
    if images is not None:
        product.images = [ProductImage(image_url=url, is_thumbnail=index == 0) for index, url in enumerate(images)]
    _commit(db)
    return product_data(
        db.scalar(select(Product).options(joinedload(Product.category), selectinload(Product.images)).where(Product.id == product_id))
    )


def toggle_product(db: Session, product_id: int) -> dict:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    product.is_active = not product.is_active
    _commit(db)
    return {"id": product.id, "is_active": product.is_active}


def delete_product(db: Session, product_id: int) -> dict:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm.")
    product.is_active = False
    _commit(db)
    return {"id": product.id, "is_active": False}


def validate_coupon(db: Session, code: str) -> dict:
    voucher = db.scalar(select(TradeIn).where(func.lower(TradeIn.voucher_code) == code.strip().lower()))
    if voucher is None or voucher.status != TradeInStatus.APPROVED or voucher.voucher_used:
        raise HTTPException(status_code=400, detail="Mã ưu đãi không hợp lệ hoặc đã được sử dụng.")
    return {"code": voucher.voucher_code, "discount_percent": 10}


def create_order(db: Session, payload: OrderInput, user: User) -> dict:
    quantities = Counter()
    for item in payload.items:
        quantities[item.product_id] += item.quantity
    if any(quantity > 50 for quantity in quantities.values()):
        raise HTTPException(status_code=422, detail="Mỗi sản phẩm chỉ được đặt tối đa 50 sản phẩm.")
    products = db.scalars(
        select(Product).where(Product.id.in_(quantities)).with_for_update()
    ).all()
    by_id = {product.id: product for product in products}
    if len(by_id) != len(quantities):
        raise HTTPException(status_code=404, detail="Một hoặc nhiều sản phẩm không tồn tại.")
    for product_id, quantity in quantities.items():
        product = by_id[product_id]
        if not product.is_active:
            raise HTTPException(status_code=409, detail=f"Sản phẩm {product.name} hiện không bán.")
        if product.stock_quantity < quantity:
            raise HTTPException(status_code=409, detail=f"Sản phẩm {product.name} không đủ tồn kho.")
    subtotals = {
        product_id: (Decimal(str(by_id[product_id].discount_price or by_id[product_id].price)) * quantity).quantize(CENT)
        for product_id, quantity in quantities.items()
    }
    total = sum(subtotals.values(), Decimal("0.00"))
    discount = Decimal("0.00")
    coupon = None
    voucher = None
    if payload.coupon_code:
        voucher = db.scalar(
            select(TradeIn).where(func.lower(TradeIn.voucher_code) == payload.coupon_code.strip().lower()).with_for_update()
        )
        if voucher is None or voucher.status != TradeInStatus.APPROVED or voucher.voucher_used:
            raise HTTPException(status_code=400, detail="Mã ưu đãi không hợp lệ hoặc đã được sử dụng.")
        discount = (total * Decimal("0.10")).quantize(CENT, rounding=ROUND_HALF_UP)
        coupon = voucher.voucher_code
    order = Order(
        user_id=user.id,
        full_name=payload.full_name,
        phone=payload.phone,
        shipping_address=payload.shipping_address,
        payment_method=payload.payment_method,
        note=payload.note,
        coupon_code=coupon,
        total_amount=total,
        discount_amount=discount,
        final_amount=total - discount,
        status=OrderStatus.PENDING,
        order_code=f"ECO{datetime.now(UTC):%y%m%d}{secrets.token_hex(3).upper()}",
    )
    for product_id, quantity in quantities.items():
        product = by_id[product_id]
        unit_price = Decimal(str(product.discount_price or product.price))
        order.items.append(
            OrderItem(product=product, quantity=quantity, unit_price=unit_price, subtotal=subtotals[product_id])
        )
        product.stock_quantity -= quantity
    if voucher:
        voucher.voucher_used = True
    db.add(order)
    _commit(db)
    order = db.scalar(select(Order).options(selectinload(Order.items).joinedload(OrderItem.product)).where(Order.id == order.id))
    return order_data(order)


def lookup_order(db: Session, order_code: str) -> dict:
    order = db.scalar(
        select(Order).options(selectinload(Order.items).joinedload(OrderItem.product)).where(Order.order_code == order_code)
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")
    return order_data(order, private=False)


def admin_orders(db: Session, page: int, limit: int, status_filter: OrderStatus | None) -> dict:
    statement = select(Order).options(selectinload(Order.items).joinedload(OrderItem.product))
    if status_filter:
        statement = statement.where(Order.status == status_filter)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(statement.order_by(Order.created_at.desc()).offset((page - 1) * limit).limit(limit)).unique().all()
    return {"items": [order_data(order) for order in rows], "pagination": {"page": page, "limit": limit, "total": total}}


def customer_orders(db: Session, user: User, page: int, limit: int) -> dict:
    """Return only the signed-in customer's own orders."""
    statement = select(Order).options(selectinload(Order.items).joinedload(OrderItem.product)).where(Order.user_id == user.id)
    total = db.scalar(select(func.count()).select_from(Order).where(Order.user_id == user.id)) or 0
    rows = db.scalars(statement.order_by(Order.created_at.desc()).offset((page - 1) * limit).limit(limit)).unique().all()
    return {"items": [order_data(order, private=False) for order in rows], "pagination": {"page": page, "limit": limit, "total": total}}


def update_order_status(db: Session, order_id: int, payload: OrderStatusInput) -> dict:
    order = db.scalar(select(Order).options(selectinload(Order.items)).where(Order.id == order_id).with_for_update())
    if order is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng.")
    transitions = {
        OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.SHIPPING, OrderStatus.CANCELLED},
        OrderStatus.SHIPPING: {OrderStatus.COMPLETED},
        OrderStatus.COMPLETED: set(),
        OrderStatus.CANCELLED: set(),
    }
    if payload.status == order.status:
        return order_data(order)
    if payload.status not in transitions[order.status]:
        raise HTTPException(status_code=409, detail="Không thể chuyển đơn hàng sang trạng thái này.")
    if payload.status == OrderStatus.CANCELLED:
        for item in order.items:
            product = db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
            if product:
                product.stock_quantity += item.quantity
        if order.coupon_code:
            voucher = db.scalar(select(TradeIn).where(TradeIn.voucher_code == order.coupon_code))
            if voucher:
                voucher.voucher_used = False
    order.status = payload.status
    if payload.status == OrderStatus.COMPLETED and order.user_id:
        user = db.get(User, order.user_id)
        if user:
            user.green_points += int(order.final_amount // 100000)
    _commit(db)
    updated = db.scalar(
        select(Order).options(selectinload(Order.items).joinedload(OrderItem.product)).where(Order.id == order_id)
    )
    return order_data(updated)


def create_trade_in(db: Session, payload: TradeInInput, user: User | None) -> dict:
    trade_in = TradeIn(**payload.model_dump(), user_id=user.id if user else None)
    db.add(trade_in)
    _commit(db)
    db.refresh(trade_in)
    return trade_in_data(trade_in)


def list_trade_ins(db: Session, page: int, limit: int, status_filter: TradeInStatus | None) -> dict:
    statement = select(TradeIn)
    if status_filter:
        statement = statement.where(TradeIn.status == status_filter)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(statement.order_by(TradeIn.created_at.desc()).offset((page - 1) * limit).limit(limit)).all()
    return {"items": [trade_in_data(item) for item in rows], "pagination": {"page": page, "limit": limit, "total": total}}


def approve_trade_in(db: Session, trade_in_id: int) -> dict:
    trade_in = db.scalar(select(TradeIn).where(TradeIn.id == trade_in_id).with_for_update())
    if trade_in is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu thu gom.")
    if trade_in.status != TradeInStatus.PENDING:
        raise HTTPException(status_code=409, detail="Chỉ duyệt yêu cầu đang chờ xử lý.")
    alphabet = string.ascii_uppercase + string.digits
    trade_in.status = TradeInStatus.APPROVED
    trade_in.voucher_code = "REWEAR10-" + "".join(secrets.choice(alphabet) for _ in range(6))
    if trade_in.user_id:
        user = db.get(User, trade_in.user_id)
        if user:
            user.green_points += 50
    _commit(db)
    return trade_in_data(trade_in)


def update_trade_in_status(db: Session, trade_in_id: int, payload: TradeInStatusInput) -> dict:
    trade_in = db.get(TradeIn, trade_in_id)
    if trade_in is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu thu gom.")
    if trade_in.status not in {TradeInStatus.APPROVED, TradeInStatus.PENDING}:
        raise HTTPException(status_code=409, detail="Yêu cầu đã ở trạng thái kết thúc.")
    trade_in.status = TradeInStatus(payload.status)
    _commit(db)
    return trade_in_data(trade_in)


def list_articles(db: Session, page: int, limit: int, category_type: ArticleCategory | None, admin: bool = False) -> dict:
    statement = select(Article)
    if not admin:
        statement = statement.where(Article.is_published.is_(True))
    if category_type:
        statement = statement.where(Article.category_type == category_type)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(statement.order_by(Article.created_at.desc()).offset((page - 1) * limit).limit(limit)).all()
    return {"items": [article_data(item) for item in rows], "pagination": {"page": page, "limit": limit, "total": total}}


def get_article(db: Session, slug: str) -> dict:
    article = db.scalar(select(Article).where(Article.slug == slug, Article.is_published.is_(True)))
    if article is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    db.execute(update(Article).where(Article.id == article.id).values(views=Article.views + 1))
    db.commit()
    db.refresh(article)
    return article_data(article)


def create_article(db: Session, payload: ArticleInput) -> dict:
    article = Article(**payload.model_dump())
    db.add(article)
    _commit(db)
    db.refresh(article)
    return article_data(article)


def update_article(db: Session, article_id: int, payload: ArticleUpdate) -> dict:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, key, value)
    _commit(db)
    db.refresh(article)
    return article_data(article)


def delete_article(db: Session, article_id: int) -> dict:
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài viết.")
    article.is_published = False
    _commit(db)
    return {"id": article.id, "is_published": False}


def create_contact(db: Session, payload: ContactInput) -> dict:
    contact = Contact(**payload.model_dump())
    db.add(contact)
    _commit(db)
    db.refresh(contact)
    return contact_data(contact)


def list_contacts(db: Session, page: int, limit: int, status_filter: str | None) -> dict:
    statement = select(Contact)
    if status_filter:
        statement = statement.where(Contact.status == status_filter)
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = db.scalars(statement.order_by(Contact.created_at.desc()).offset((page - 1) * limit).limit(limit)).all()
    return {"items": [contact_data(item) for item in rows], "pagination": {"page": page, "limit": limit, "total": total}}


def update_contact_status(db: Session, contact_id: int, payload: ContactStatusInput) -> dict:
    contact = db.get(Contact, contact_id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy tin nhắn.")
    contact.status = ContactStatus(payload.status)
    _commit(db)
    return contact_data(contact)


def admin_summary(db: Session) -> dict:
    return {
        "products": db.scalar(select(func.count()).select_from(Product).where(Product.is_active.is_(True))) or 0,
        "orders_pending": db.scalar(select(func.count()).select_from(Order).where(Order.status == OrderStatus.PENDING)) or 0,
        "trade_ins_pending": db.scalar(select(func.count()).select_from(TradeIn).where(TradeIn.status == TradeInStatus.PENDING)) or 0,
        "unread_contacts": db.scalar(select(func.count()).select_from(Contact).where(Contact.status == ContactStatus.NEW)) or 0,
        "revenue_completed": float(db.scalar(select(func.coalesce(func.sum(Order.final_amount), 0)).where(Order.status == OrderStatus.COMPLETED)) or 0),
    }
