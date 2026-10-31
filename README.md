# 🌿 ECO-LOOP - Circular Fashion & Re-Commerce Platform

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