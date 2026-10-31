"""Create tables and insert safe, clearly-labelled local demo content."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Article,
    ArticleCategory,
    Category,
    Product,
    ProductImage,
    User,
    UserRole,
)

PRODUCTS = [
    {
        "category": "ao-thun", "name": "Áo thun Sương Mai", "code": "ECO-TS-001", "slug": "ao-thun-suong-mai",
        "price": "329000", "discount_price": "289000", "material": "Cotton hữu cơ (demo)", "co2": 0.8, "stock": 32,
        "description": "Áo thun tối giản, mềm nhẹ, phối đồ hằng ngày.", "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "ao-thun", "name": "Áo thun Mầm Xanh", "code": "ECO-TS-002", "slug": "ao-thun-mam-xanh",
        "price": "359000", "discount_price": None, "material": "Sợi tre pha cotton (demo)", "co2": 0.6, "stock": 24,
        "description": "Phom relaxed thoáng mát, bảng màu lấy cảm hứng từ thiên nhiên.", "image": "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "ao-so-mi", "name": "Sơ mi Vệt Nắng", "code": "ECO-SH-003", "slug": "so-mi-vet-nang",
        "price": "549000", "discount_price": None, "material": "Cotton và polyester tái chế (demo)", "co2": 1.1, "stock": 18,
        "description": "Sơ mi dễ mặc cho ngày làm việc lẫn cuối tuần.", "image": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "ao-khoac", "name": "Áo khoác Gió Rừng", "code": "ECO-JK-004", "slug": "ao-khoac-gio-rung",
        "price": "890000", "discount_price": "790000", "material": "Polyester tái chế (demo)", "co2": 1.7, "stock": 12,
        "description": "Lớp khoác nhẹ gọn, phù hợp những chuyến đi ngắn.", "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "tui-tote", "name": "Túi tote Vòng Đời", "code": "ECO-BG-005", "slug": "tui-tote-vong-doi",
        "price": "219000", "discount_price": None, "material": "Vải canvas tái sử dụng (demo)", "co2": 0.4, "stock": 45,
        "description": "Túi nhiều không gian cho sách, bình nước và vật dụng hằng ngày.", "image": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "phu-kien", "name": "Mũ bucket Lá Non", "code": "ECO-AC-006", "slug": "mu-bucket-la-non",
        "price": "259000", "discount_price": None, "material": "Cotton dư thừa sản xuất (demo)", "co2": 0.3, "stock": 21,
        "description": "Phụ kiện gọn nhẹ với vành mềm, dễ gấp mang theo.", "image": "https://images.unsplash.com/photo-1521369909029-2afed882baee?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "quan-dai", "name": "Quần dài Đường Mòn", "code": "ECO-PT-007", "slug": "quan-dai-duong-mon",
        "price": "629000", "discount_price": None, "material": "Cotton pha sợi tái chế (demo)", "co2": 1.0, "stock": 15,
        "description": "Phom suông thoải mái, túi sâu tiện dụng.", "image": "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=1000&q=85",
    },
    {
        "category": "ao-khoac", "name": "Áo khoác denim Hồi Sinh", "code": "ECO-DN-008", "slug": "ao-khoac-denim-hoi-sinh",
        "price": "990000", "discount_price": "899000", "material": "Denim pha cotton tái chế (demo)", "co2": 1.4, "stock": 9,
        "description": "Phom denim cổ điển; sản phẩm minh họa cho lựa chọn mặc lâu và sửa chữa.", "image": "https://images.unsplash.com/photo-1543076447-215ad9ba6923?auto=format&fit=crop&w=1000&q=85",
    },
]

ARTICLES = [
    {
        "title": "Mặc lâu hơn, bắt đầu một vòng đời mới", "slug": "mac-lau-hon-vong-doi-moi",
        "category_type": ArticleCategory.ECO_GUIDE,
        "short_summary": "Sửa chữa, trao đổi và tái sử dụng là những lựa chọn thiết thực trước khi một món đồ trở thành rác thải.",
        "content": "Một chiếc áo được mặc lâu hơn thường không cần thay thế sớm. Hãy ưu tiên giặt đúng hướng dẫn, sửa chi tiết nhỏ và trao tặng hoặc bán lại khi bạn không còn sử dụng. Tái chế là một phần của kinh tế tuần hoàn, nhưng kéo dài thời gian sử dụng giúp giữ giá trị của sản phẩm lâu hơn. Bài viết minh họa, không phải tư vấn kiểm định vòng đời sản phẩm.",
        "image_url": "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=1400&q=85",
        "source_url": "https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy",
    },
    {
        "title": "Vải tái chế: đọc nhãn và truy xuất nguồn gốc", "slug": "vai-tai-che-doc-nhan-truy-xuat",
        "category_type": ArticleCategory.NEWS,
        "short_summary": "Tên gọi vật liệu chưa đủ để chứng minh tác động; hãy xem thành phần, tiêu chuẩn và thông tin chuỗi cung ứng.",
        "content": "Polyester tái chế và nylon tái chế được Textile Exchange xếp vào nhóm sợi tổng hợp ưu tiên trong khung thuật ngữ của tổ chức. Điều đó không tự động chứng minh mọi sản phẩm làm từ chúng đều bền vững. Người mua nên tìm tỷ lệ thành phần, tiêu chuẩn bên thứ ba phù hợp và khả năng truy xuất chuỗi cung ứng. ECO-LOOP dùng dữ liệu sản phẩm mẫu để minh họa cách hiển thị thông tin, không đại diện cho chứng nhận hàng hóa thật.",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=1400&q=85",
        "source_url": "https://textileexchange.org/glossary/preferred-synthetics/",
    },
    {
        "title": "Tái sử dụng hay tái chế? Chọn đúng bước tiếp theo", "slug": "tai-su-dung-hay-tai-che",
        "category_type": ArticleCategory.ECO_GUIDE,
        "short_summary": "Phân loại tình trạng món đồ trước khi gửi đi để tăng cơ hội tiếp tục sử dụng.",
        "content": "Nếu quần áo còn tốt, hãy cân nhắc sửa chữa, tặng lại hoặc bán lại trước. Nếu không thể mặc tiếp, hãy tìm chương trình thu gom có thông tin rõ về khâu phân loại và xử lý. Cơ quan Môi trường châu Âu lưu ý rằng hoạt động tái sử dụng và tái chế phụ thuộc vào năng lực phân loại, xử lý và thị trường đầu ra. ECO-LOOP tiếp nhận đăng ký thu gom để đội ngũ đánh giá tình trạng trước khi quyết định.",
        "image_url": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1400&q=85",
        "source_url": "https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy",
    },
    {
        "title": "Rác thải dệt may: nhìn vào dữ liệu trước khi hành động", "slug": "du-lieu-rac-thai-det-may-eu",
        "category_type": ArticleCategory.NEWS,
        "short_summary": "EEA ước tính EU tạo ra 6,95 triệu tấn rác thải dệt may năm 2020; phần lớn vẫn nằm trong rác sinh hoạt hỗn hợp.",
        "content": "Theo European Environment Agency, năm 2020 EU tạo ra khoảng 6,95 triệu tấn rác thải dệt may, tương đương khoảng 16 kg mỗi người. Khoảng 4,4 kg mỗi người được thu gom riêng để tái sử dụng hoặc tái chế, còn 11,6 kg mỗi người đi vào rác sinh hoạt hỗn hợp. Đây là số liệu của EU trong năm 2020, không phải số liệu Việt Nam hay tình hình hiện tại. EEA cũng nhấn mạnh rằng thu gom riêng không tự bảo đảm toàn bộ hàng dệt sẽ được tái sử dụng hoặc tái chế; năng lực phân loại và xử lý rất quan trọng.",
        "image_url": "https://images.unsplash.com/photo-1531058020387-3be344556be6?auto=format&fit=crop&w=1400&q=85",
        "source_url": "https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy",
    },
]


def initialise_database() -> None:
    """Create current model tables and populate an empty database with demo data."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(Category.id).limit(1)) is None:
            roots = [
                Category(name="Trang phục", slug="trang-phuc", description="Trang phục dùng hằng ngày"),
                Category(name="Phụ kiện", slug="phu-kien-goc", description="Phụ kiện tái sử dụng"),
            ]
            db.add_all(roots)
            db.flush()
            db.add_all([
                Category(name="Áo thun", slug="ao-thun", parent_id=roots[0].id),
                Category(name="Áo sơ mi", slug="ao-so-mi", parent_id=roots[0].id),
                Category(name="Áo khoác", slug="ao-khoac", parent_id=roots[0].id),
                Category(name="Quần dài", slug="quan-dai", parent_id=roots[0].id),
                Category(name="Túi tote", slug="tui-tote", parent_id=roots[1].id),
                Category(name="Phụ kiện khác", slug="phu-kien", parent_id=roots[1].id),
            ])
            db.flush()
        if db.scalar(select(Product.id).limit(1)) is None:
            category_ids = dict(db.execute(select(Category.slug, Category.id)).all())
            for row in PRODUCTS:
                product = Product(
                    category_id=category_ids[row["category"]], name=row["name"], code=row["code"],
                    slug=row["slug"], price=Decimal(row["price"]),
                    discount_price=Decimal(row["discount_price"]) if row["discount_price"] else None,
                    material_eco_type=row["material"], co2_saved_kg=row["co2"],
                    stock_quantity=row["stock"], description=row["description"],
                    content_detail=(row["description"] + "\n\nSản phẩm và chỉ số tác động trong trang demo là dữ liệu minh họa, chưa được kiểm định vòng đời."),
                )
                product.images.append(ProductImage(image_url=row["image"], is_thumbnail=True))
                db.add(product)
        if db.scalar(select(Article.id).limit(1)) is None:
            db.add_all([Article(**article) for article in ARTICLES])
        if settings.admin_email and settings.admin_password:
            existing_admin = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
            if existing_admin is None:
                db.add(User(
                    full_name="Quản trị ECO-LOOP",
                    email=settings.admin_email.lower(),
                    password_hash=hash_password(settings.admin_password),
                    role=UserRole.ADMIN,
                ))
        db.commit()
