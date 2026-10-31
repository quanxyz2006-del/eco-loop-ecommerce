# 🌿 ECO-LOOP - Circular Fashion & Re-Commerce Platform

ECO-LOOP là website thương mại điện tử thời trang tuần hoàn, gồm cửa hàng dành cho khách, API FastAPI, trang quản trị và các luồng đăng ký/đặt hàng/thu cũ đổi mới. Dự án có thể chạy local bằng Python hoặc đóng gói bằng Docker Compose.

> Nền tảng Thương mại Điện tử chuyên về Thời trang Bền vững, Trang phục Dã ngoại Sinh thái và Dịch vụ Thu gom - Tái chế Tuần hoàn (Trade-in / Re-wear).

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat&logo=mysql)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Giới thiệu đề tài

Dự án giải quyết bài toán rác thải dệt may và sự thiếu minh bạch của xu hướng thời trang xanh bằng cách kết hợp:
1. **Thương mại điện tử:** Bán lẻ trang phục sản xuất từ sợi sinh thái (sợi cà phê, sợi tre, nhựa PET tái sinh).
2. **Kinh tế tuần hoàn (Re-commerce):** Cung cấp dịch vụ thu gom quần áo cũ đổi lấy điểm thưởng/voucher giảm giá (Trade-in Service).
3. **Lan tỏa lối sống xanh:** Chuyên mục tin tức, cẩm nang bảo quản và tính toán lượng khí thải CO₂ cắt giảm trên từng đơn hàng.

---

## 🚀 Tính năng chính

### 🛒 Dành cho Khách hàng (Storefront)
* **Trang chủ & Điều hướng:** Banner chiến dịch, danh mục sản phẩm nổi bật, cam kết phát triển bền vững (ESG).
* **Danh mục sản phẩm 2 cấp:** Lọc linh hoạt theo chất liệu sinh thái và công năng sử dụng; đánh giá sao & chia sẻ mạng xã hội.
* **Dịch vụ Thu gom (Trade-in):** Đăng ký gửi đồ cũ, chọn mức độ tình trạng và nhận mã giảm giá.
* **Giỏ hàng & Thanh toán:** Tích hợp mã giảm giá sinh thái, đa dạng hình thức thanh toán (COD, Chuyển khoản).
* **Tin tức & Sự kiện:** Cẩm nang sống xanh, tối ưu SEO, hiển thị bài viết theo thứ tự thời gian.
* **Hỗ trợ khách hàng:** Chatbot tư vấn chọn size/chất liệu tự động, widget mạng xã hội, form liên hệ tích hợp Google Maps.

### ⚙️ Dành cho Quản trị viên (Admin Portal)
* Quản lý sản phẩm, danh mục (thêm, sửa, xóa, ẩn/hiện).
* Tiếp nhận và duyệt các yêu cầu thu gom/ký gửi đồ cũ.
* Theo dõi, cập nhật trạng thái đơn hàng (Chờ duyệt, Đang giao, Hoàn tất).
* Quản lý bài viết tin tức và xử lý thông tin liên hệ từ khách hàng.

---

## 🏗️ Kiến trúc & Ngăn xếp Công nghệ

* **Backend:** Python (FastAPI), SQLAlchemy ORM, Pydantic v2.
* **Database:** MySQL 8.0, Alembic (Database Migrations).
* **Frontend:** HTML5, CSS3, JavaScript (Bootstrap 5 / TailwindCSS Responsive).
* **Bảo mật:** JWT Authentication, Passlib/Bcrypt.

```text
eco-loop-ecommerce/
├── backend/          # RESTful API Service
│   ├── app/          # Controllers, Services, Models, Schemas
│   └── migrations/   # Alembic database migrations
├── frontend/         # Giao diện người dùng & Admin
│   ├── pages/        # Các trang HTML theo đặc tả đề cương
│   └── public/       # File tĩnh (CSS, JS, Assets)
├── docs/             # Báo cáo, Use Case, Sơ đồ ERD, Hợp đồng điện tử
└── database/         # Script khởi tạo CSDL & Seed Data
```

## ⚡ Chạy ECO-LOOP trên máy cá nhân

Yêu cầu Python 3.11 trở lên. Cài dependencies và chạy từ thư mục `backend`:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Lần chạy đầu, ứng dụng tự tạo schema và catalog/bài viết demo vào `database/eco_loop.db` (đường dẫn mặc định). Nếu dùng MySQL 8, đặt `DATABASE_URL` trong `backend/.env`, ví dụ `mysql+pymysql://user:password@localhost:3306/eco_loop`, rồi tạo database trước khi khởi động. File `.env.example` là mẫu cấu hình; không đưa mật khẩu thật vào Git.

Trợ lý khách hàng dùng Google GenAI SDK với Gemini 3.8 Flash. Khóa API chỉ đặt trong `backend/.env` dưới biến `GEMINI_API_KEY`; không đặt khóa trong HTML/JavaScript. Nếu chưa cấu hình khóa, chatbot dùng FAQ dự phòng cục bộ. Trợ lý được grounding bằng danh sách catalog hiện tại và dữ liệu FAQ cửa hàng; đây không phải huấn luyện lại trọng số Gemini. Xem [tài liệu Gemini API chính thức](https://ai.google.dev/gemini-api/docs/text-generation).

- Cửa hàng: <http://127.0.0.1:8000/>
- Tài liệu API: <http://127.0.0.1:8000/api/v1/docs>
- Health check: <http://127.0.0.1:8000/health>
- Cổng quản trị: <http://127.0.0.1:8000/admin>
- Chatbot cửa hàng: nút “Hỏi ECO-LOOP” ở góc màn hình.
- Zalo: <https://zalo.me/0966618840> · Email: <mailto:quanxyz2006@gmail.com>

Tạo tài khoản admin (mật khẩu được nhập ẩn, tối thiểu 8 ký tự):

```powershell
.\.venv\Scripts\python.exe -m app.create_admin --email admin@eco-loop.local
```

Sau đó đăng nhập tại `/admin`. Tài khoản đăng ký từ storefront mặc định chỉ có quyền khách hàng.

## 🗂️ Dữ liệu mẫu và nguồn tham khảo

Catalog có 8 sản phẩm, cây danh mục 2 cấp và 4 bài viết. Giá, tồn kho, tên hàng và chỉ số CO₂ là dữ liệu giả lập; không biểu thị hàng hóa/chứng nhận/LCA có thật. Một số bài viết dẫn nguồn Textile Exchange và European Environment Agency, kèm phạm vi và năm của số liệu. Chi tiết nằm trong [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md).

Ứng dụng tự seed khi bảng liên quan còn trống. Với MySQL có thể chạy [`database/schema.sql`](database/schema.sql) rồi [`database/seed_data.sql`](database/seed_data.sql); không cần seed theo cả hai cách.

## 🧩 Module

| Module | Chức năng chính |
| --- | --- |
| Tài khoản & xác thực | Đăng ký, đăng nhập JWT, xác thực email qua SMTP, hồ sơ người dùng và phân quyền khách hàng/quản trị viên. |
| Danh mục & sản phẩm | Danh mục hai cấp; tìm kiếm, lọc, phân trang; quản trị viên tạo/sửa/ẩn/hiện sản phẩm. |
| Giỏ hàng & đơn hàng | Giỏ hàng, checkout cần đăng nhập, xác thực giá/tồn kho phía máy chủ, mã giảm giá, theo dõi trạng thái và hoàn kho khi hủy. |
| Thanh toán | Hỗ trợ COD và hướng dẫn chuyển khoản/QR cấu hình riêng theo cửa hàng. Không đưa QR ngân hàng cá nhân vào repository công khai. |
| Đánh giá sản phẩm | Người dùng đăng nhập có thể gửi và xem đánh giá sản phẩm. |
| Thu cũ đổi mới | Gửi yêu cầu thu gom, quản trị duyệt/cập nhật trạng thái và cấp voucher theo luồng cửa hàng. |
| Chatbot hỗ trợ | Gemini API với ngữ cảnh FAQ/catalog; có câu trả lời dự phòng khi chưa cấu hình API key hoặc dịch vụ tạm lỗi. |
| Tin tức & nội dung | Danh sách/lọc bài viết, lượt xem; quản trị tạo/sửa/ẩn nội dung. |
| Liên hệ & dashboard | Tiếp nhận, phân loại yêu cầu liên hệ và tổng quan hoạt động quản trị. |
| Storefront responsive | Trang chủ, giới thiệu, tìm sản phẩm, chi tiết, tài khoản, giỏ hàng, thanh toán, tin tức và liên hệ. |
| API & triển khai | REST API FastAPI, Swagger UI, MySQL/Alembic và Docker Compose với Caddy reverse proxy. |

## Luồng xử lý và thuật toán chính

- **Đăng ký/đăng nhập:** chuẩn hóa và kiểm tra email, băm mật khẩu trước khi lưu; gửi mã xác thực qua SMTP, chỉ xác nhận tài khoản khi mã băm khớp và mã còn hạn; đăng nhập trả JWT và kiểm tra role ở API quản trị.
- **Tìm kiếm sản phẩm:** ghép các điều kiện từ khóa/danh mục/khoảng giá/chất liệu/trạng thái, sắp theo thời điểm tạo mới nhất và phân trang ở truy vấn cơ sở dữ liệu thay vì tải toàn bộ danh sách lên trình duyệt.
- **Tạo đơn:** máy chủ đọc lại giá và tồn kho hiện hành, kiểm tra số lượng, tính tổng bằng số thập phân và áp voucher hợp lệ; lưu đơn, trừ kho và đánh dấu voucher đã dùng trong cùng transaction để tránh dùng mã lặp.
- **Hủy đơn:** khi đơn chuyển sang trạng thái hủy lần đầu, hoàn số lượng hàng và mở lại voucher đã dùng theo transaction.
- **Đánh giá:** yêu cầu JWT; mỗi tài khoản có một đánh giá cho mỗi sản phẩm, gửi lại sẽ cập nhật đánh giá hiện có.
- **Thu cũ đổi mới:** quản trị viên duyệt yêu cầu; chỉ yêu cầu được duyệt mới nhận mã voucher ngẫu nhiên giảm 10%, dùng một lần.
- **Chatbot:** ghép FAQ cửa hàng với catalog hiện hành làm ngữ cảnh cho Gemini; giới hạn tốc độ theo IP và trả lời FAQ dự phòng khi API key chưa cấu hình hoặc Gemini lỗi.

Các bước kiểm tra quyền và validation được thực hiện ở backend; giao diện chỉ hiển thị luồng tương ứng, không được xem là ranh giới bảo mật.

## Cấu trúc thư mục dự án

```text
eco-loop-ecommerce/
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/     # Auth, catalog, orders, content, admin, chatbot, trade-in
│   │   ├── core/               # Cấu hình, database, JWT và dependency quyền
│   │   ├── models/             # SQLAlchemy entities/relationships
│   │   ├── repositories/       # Truy cập dữ liệu dùng chung
│   │   ├── schemas/            # Pydantic request/response validation
│   │   └── services/           # Logic commerce, seed, email verification
│   └── migrations/versions/    # Alembic migrations
├── database/                   # Schema và seed data mẫu
├── docs/                       # API, yêu cầu nghiệp vụ, nguồn dữ liệu
├── frontend/
│   ├── pages/                  # Storefront, tài khoản và admin
│   └── public/
│       ├── css/                # Stylesheets
│       ├── js/                 # Các module giao diện theo trang
│       └── images/             # Ảnh tĩnh; QR cá nhân được cấu hình riêng
├── scripts/                    # Khởi tạo Docker và di chuyển SQLite → MySQL
├── Caddyfile                   # Reverse proxy
├── Dockerfile                  # Image ứng dụng FastAPI
└── compose.yaml                # App, MySQL và Caddy
```

### Cấu hình riêng khi triển khai

Không commit `.env`, khóa Gemini/Gmail, mật khẩu hoặc ảnh QR ngân hàng cá nhân. Tạo cấu hình riêng từ `backend/.env.example`; nếu cửa hàng dùng QR chuyển khoản, hãy cung cấp ảnh QR của chính cửa hàng trên môi trường triển khai riêng. Dữ liệu trong catalog demo được đánh dấu là minh họa.

Đặc tả API: [docs/API_Specification.md](docs/API_Specification.md). Yêu cầu nghiệp vụ: [docs/BA_Requirements.md](docs/BA_Requirements.md).
