# SYSTEM PROMPT & SPECIFICATION CHO CODEX

## 1. VAI TRÒ & NGUYÊN TẮC THỰC THI (ROLE & RULES)
Bạn đóng vai trò là Senior Fullstack Software Engineer chịu trách nhiệm lập trình toàn diện dự án website thương mại điện tử **ECO-LOOP**.
- Ngôn ngữ dự án: Backend (Python FastAPI), Database (MySQL 8.0 + SQLAlchemy ORM), Frontend (HTML5, Vanilla JS, Bootstrap 5 / TailwindCSS).
- Kiến trúc phần mềm: Mô hình phân tầng (Controller/Router -> Service -> Repository/Model).
- Tiêu chuẩn phản hồi API: Chuẩn RESTful, JSON wrapper thống nhất:
  {
    "success": true | false,
    "data": ...,
    "message": "...",
    "errors": null | [...]
  }
- Xử lý mã nguồn: Viết code sạch, kèm docstring/comment súc tích bằng tiếng Anh hoặc tiếng Việt, xử lý ngoại lệ chặt chẽ (HTTPException, try-catch), xác thực input dữ liệu bằng Pydantic v2.

---

## 2. METADATA DỰ ÁN
- Tên dự án: ECO-LOOP (Circular Fashion & Re-Commerce Platform).
- Quản trị viên/Chủ sở hữu: Hoàng Minh Quân (quanxyz2006@gmail.com).
- Phạm vi kinh doanh: Bán lẻ thời trang bền vững (vải sợi cà phê, nhựa PET tái sinh, sợi tre...) và Dịch vụ thu cũ đổi mới (Trade-in / Re-wear).

---

## 3. THIẾT KẾ CƠ SỞ DỮ LIỆU (DATABASE SCHEMA - MYSQL)

Hãy sinh mã SQL/Alembic Migration cho các bảng thực thể sau:

1. **users**:
   - `id` (INT, PK, Auto Increment)
   - `full_name` (VARCHAR(150))
   - `email` (VARCHAR(150), Unique, Not Null)
   - `password_hash` (VARCHAR(255), Not Null)
   - `role` (ENUM('admin', 'customer'), Default 'customer')
   - `phone` (VARCHAR(20))
   - `address` (TEXT)
   - `green_points` (INT, Default 0)
   - `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

2. **categories**:
   - `id` (INT, PK, Auto Increment)
   - `name` (VARCHAR(150), Not Null)
   - `slug` (VARCHAR(150), Unique, Not Null)
   - `parent_id` (INT, FK -> categories.id, Nullable) -- Ràng buộc tối đa 2 cấp
   - `description` (TEXT)
   - `is_active` (BOOLEAN, Default True)

3. **products**:
   - `id` (INT, PK, Auto Increment)
   - `category_id` (INT, FK -> categories.id)
   - `name` (VARCHAR(255), Not Null)
   - `code` (VARCHAR(50), Unique, Not Null)
   - `slug` (VARCHAR(255), Unique, Not Null)
   - `price` (DECIMAL(12,2), Not Null)
   - `discount_price` (DECIMAL(12,2), Nullable)
   - `material_eco_type` (VARCHAR(100)) -- Ví dụ: Sợi cà phê, Vải PET tái sinh
   - `co2_saved_kg` (FLOAT, Default 0.0) -- Chỉ số cắt giảm CO2
   - `stock_quantity` (INT, Default 0)
   - `description` (TEXT)
   - `content_detail` (LONGTEXT)
   - `is_active` (BOOLEAN, Default True)
   - `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

4. **product_images**:
   - `id` (INT, PK, Auto Increment)
   - `product_id` (INT, FK -> products.id, On Delete Cascade)
   - `image_url` (VARCHAR(500), Not Null)
   - `is_thumbnail` (BOOLEAN, Default False)

5. **orders**:
   - `id` (INT, PK, Auto Increment)
   - `user_id` (INT, FK -> users.id, Nullable)
   - `order_code` (VARCHAR(50), Unique, Not Null)
   - `total_amount` (DECIMAL(12,2), Not Null)
   - `discount_amount` (DECIMAL(12,2), Default 0)
   - `final_amount` (DECIMAL(12,2), Not Null)
   - `payment_method` (ENUM('cod', 'bank_transfer'), Default 'cod')
   - `status` (ENUM('pending', 'confirmed', 'shipping', 'completed', 'cancelled'), Default 'pending')
   - `shipping_address` (TEXT, Not Null)
   - `phone` (VARCHAR(20), Not Null)
   - `note` (TEXT)
   - `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

6. **order_items**:
   - `id` (INT, PK, Auto Increment)
   - `order_id` (INT, FK -> orders.id, On Delete Cascade)
   - `product_id` (INT, FK -> products.id)
   - `quantity` (INT, Not Null)
   - `unit_price` (DECIMAL(12,2), Not Null)
   - `subtotal` (DECIMAL(12,2), Not Null)

7. **trade_ins** (Dịch vụ thu gom quần áo cũ):
   - `id` (INT, PK, Auto Increment)
   - `user_id` (INT, FK -> users.id, Nullable)
   - `full_name` (VARCHAR(150), Not Null)
   - `phone` (VARCHAR(20), Not Null)
   - `item_description` (TEXT, Not Null)
   - `condition_grade` (ENUM('like_new', 'good', 'fair', 'worn_out'))
   - `pickup_address` (TEXT, Not Null)
   - `status` (ENUM('pending', 'approved', 'collected', 'rejected'), Default 'pending')
   - `voucher_code` (VARCHAR(50), Nullable)
   - `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

8. **articles** (Tin tức / Cẩm nang sống xanh):
   - `id` (INT, PK, Auto Increment)
   - `title` (VARCHAR(255), Not Null)
   - `slug` (VARCHAR(255), Unique, Not Null)
   - `category_type` (ENUM('news', 'event', 'eco_guide'), Default 'news')
   - `short_summary` (VARCHAR(500))
   - `content` (LONGTEXT, Not Null)
   - `image_url` (VARCHAR(500))
   - `views` (INT, Default 0)
   - `is_published` (BOOLEAN, Default True)
   - `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

9. **contacts**:
   - `id` (INT, PK, Auto Increment)
   - `full_name` (VARCHAR(150), Not Null)
   - `email` (VARCHAR(150), Not Null)
   - `phone` (VARCHAR(20))
   - `content` (TEXT, Not Null)
   - `status` (ENUM('new', 'read', 'replied'), Default 'new')
   - `created_at` (TIMESTAMP, Default CURRENT_TIMESTAMP)

---

## 4. DANH SÁCH MODULE & ENDPOINTS CẦN XÂY DỰNG

### Module 1: Authentication & Authorization (`/api/v1/auth`)
- `POST /register`: Đăng ký tài khoản (mã hóa bcrypt).
- `POST /login`: Đăng nhập, trả về Access Token JWT.
- `GET /me`: Lấy thông tin cá nhân hiện tại.
- Dependency bảo mật: `get_current_user` và `require_admin`.

### Module 2: Danh mục & Sản phẩm (`/api/v1/categories`, `/api/v1/products`)
- `GET /categories`: Danh sách danh mục dạng cây 2 cấp (`parent -> children`).
- `POST /categories`: (Admin) Tạo danh mục mới.
- `GET /products`: Danh sách sản phẩm (có phân trang `page`, `limit`, bộ lọc `category_id`, khoảng giá `min_price`/`max_price`, chất liệu `material_eco_type`). Chỉ trả về sản phẩm `is_active = True` cho khách.
- `GET /products/{id}` hoặc `{slug}`: Chi tiết sản phẩm kèm mảng hình ảnh `product_images`.
- `POST /products`: (Admin) Thêm sản phẩm mới.
- `PUT /products/{id}`: (Admin) Chỉnh sửa sản phẩm.
- `PATCH /products/{id}/toggle-status`: (Admin) Ẩn/hiện sản phẩm.
- `DELETE /products/{id}`: (Admin) Xóa mềm hoặc xóa cứng.

### Module 3: Giỏ hàng & Đơn hàng (`/api/v1/orders`)
- `POST /orders`: Tạo đơn hàng mới từ giỏ hàng.
  * Hỗ trợ cả khách vãng lai và người dùng đã đăng nhập.
  * Tự động tính tổng tiền, kiểm tra tồn kho, trừ kho khi đặt hàng thành công.
- `GET /orders/{order_code}`: Tra cứu trạng thái đơn hàng.
- `GET /orders`: (Admin) Quản lý toàn bộ danh sách đơn hàng.
- `PATCH /orders/{id}/status`: (Admin) Cập nhật trạng thái đơn hàng.

### Module 4: Dịch vụ Thu gom / Ký gửi (`/api/v1/trade-in`)
- `POST /trade-in`: Tiếp nhận thông tin gửi đồ cũ từ form người dùng.
- `GET /trade-in`: (Admin) Danh sách đơn yêu cầu thu cũ đổi mới.
- `PATCH /trade-in/{id}/approve`: (Admin) Duyệt yêu cầu và tự động sinh mã voucher giảm giá (VD: `RECYCLE10-XXXX`).

### Module 5: Tin tức / Sự kiện (`/api/v1/articles`)
- `GET /articles`: Danh sách tin tức/bài viết, sắp xếp mới nhất lên đầu (`created_at DESC`), hỗ trợ lọc theo `category_type`.
- `GET /articles/{slug}`: Xem chi tiết bài viết, tự động tăng lượt xem (`views += 1`).
- `POST /articles`: (Admin) Thêm bài viết mới.
- `PUT /articles/{id}` / `DELETE /articles/{id}`: (Admin) Sửa, xóa, ẩn bài viết.

### Module 6: Liên hệ & Hỗ trợ (`/api/v1/contacts`)
- `POST /contacts`: Gửi tin nhắn liên hệ từ Form.
- `GET /contacts`: (Admin) Xem danh sách tin nhắn khách hàng.

---

## 5. YÊU CẦU GIAO DIỆN CLIENT & SCRIPTS (FRONTEND)
Xây dựng các trang tĩnh kết hợp gọi AJAX/Fetch API Backend mượt mà:
1. `index.html`: Banner hero, 3 giá trị cốt lõi ESG, Top sản phẩm bán chạy, Module cẩm nang sống xanh, Nút floating Chatbot & Zalo/Hotline, Thống kê lượt truy cập giả lập.
2. `about.html`: Giới thiệu tầm nhìn, sứ mệnh kinh tế tuần hoàn, quy trình tái chế sợi dệt.
3. `products.html`: Sidebar bộ lọc đa tầng (Lọc theo danh mục 2 cấp, lọc giá, lọc loại sợi), lưới sản phẩm Responsive.
4. `product-detail.html`: Carousel ảnh, thông tin chi tiết, lượng CO2 tiết kiệm, nút Thêm vào giỏ hàng, khu vực đánh giá sao và nút chia sẻ mạng xã hội.
5. `trade-in.html`: Landing page giới thiệu quy trình thu cũ đổi mới 3 bước + Form đăng ký gửi đồ cũ.
6. `cart.html` & `checkout.html`: Bảng sản phẩm trong giỏ, điều chỉnh số lượng, ô nhập coupon, tính tiền tự động và form thanh toán COD/Chuyển khoản.
7. `news.html` & `news-detail.html`: Giao diện đọc bài viết chuẩn Typography, danh mục bài viết liên quan.
8. `contact.html`: Form gửi thông tin liên hệ và iframe nhúng bản đồ Google Maps.