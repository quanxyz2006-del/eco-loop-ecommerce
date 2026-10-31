# ECO-LOOP API v1

Base path: `/api/v1`. Response envelope: `{ "success": boolean, "data": any|null, "message": string, "errors": array|null }`. OpenAPI tương tác tại `/api/v1/docs`.

## Trợ lý cửa hàng

- `GET /api/v1/chatbot/status`: trạng thái cấu hình Gemini và model (không tiết lộ API key).
- `POST /api/v1/chatbot/message`: nhận `{ "message": "...", "history": [{"role":"user|assistant", "content":"..."}] }`; lịch sử tối đa 8 lượt, câu hỏi tối đa 1.200 ký tự. Nội dung được grounding bằng FAQ cửa hàng và catalog đang bán. Nếu Gemini chưa cấu hình hoặc tạm lỗi, API trả lời từ FAQ dự phòng.
- Lệnh chat giới hạn cơ bản 10 yêu cầu mỗi phút cho từng IP của worker.

## Quyền đặt hàng

- `POST /api/v1/orders` yêu cầu `Authorization: Bearer <token>`; đơn hàng luôn gắn với khách hàng đã đăng nhập.

## Authentication

| Method | Path | Quyền | Chức năng |
|---|---|---|---|
| POST | `/auth/register` | Public | Tạo tài khoản khách hàng |
| POST | `/auth/login` | Public | Trả về bearer JWT |
| GET | `/auth/me` | Customer/Admin | Hồ sơ hiện tại |

## Catalog

| Method | Path | Quyền | Chức năng |
|---|---|---|---|
| GET | `/categories` | Public | Cây danh mục tối đa hai cấp |
| POST | `/categories` | Admin | Tạo danh mục |
| GET | `/products` | Public | Phân trang; lọc `category_id`, `min_price`, `max_price`, `material_eco_type`, `search` |
| GET | `/products/{identifier}` | Public | Chi tiết theo ID hoặc slug |
| GET | `/products/admin/all` | Admin | Bao gồm sản phẩm ẩn |
| POST/PUT | `/products[/{id}]` | Admin | Tạo/cập nhật sản phẩm và ảnh |
| PATCH | `/products/{id}/toggle-status` | Admin | Ẩn/hiện |
| DELETE | `/products/{id}` | Admin | Xóa mềm |

## Commerce và trade-in

| Method | Path | Quyền | Chức năng |
|---|---|---|---|
| POST | `/orders/coupon?code=...` | Public | Kiểm tra voucher |
| POST | `/orders` | Customer (Bearer token bắt buộc) | Tạo đơn gắn với tài khoản; giá/tồn kho do server tính |
| GET | `/orders/{order_code}` | Public | Tra cứu status và dòng hàng, không trả địa chỉ/điện thoại |
| GET | `/orders` | Admin | Danh sách đơn phân trang |
| PATCH | `/orders/{id}/status` | Admin | Chuyển trạng thái theo luồng hợp lệ |
| POST | `/trade-in` | Public/Customer | Tạo yêu cầu thu gom |
| GET | `/trade-in` | Admin | Danh sách/lọc yêu cầu |
| PATCH | `/trade-in/{id}/approve` | Admin | Duyệt và sinh voucher `REWEAR10-XXXXXX` |
| PATCH | `/trade-in/{id}/status` | Admin | Đánh dấu đã thu hoặc từ chối |

## Nội dung, liên hệ, quản trị

| Method | Path | Quyền | Chức năng |
|---|---|---|---|
| GET | `/articles` | Public | Bài đã xuất bản, lọc `category_type` |
| GET | `/articles/{slug}` | Public | Chi tiết và tăng view |
| GET | `/articles/admin/all` | Admin | Bao gồm bản nháp/ẩn |
| POST/PUT/DELETE | `/articles[/{id}]` | Admin | Tạo, cập nhật, ẩn bài |
| POST | `/contacts` | Public | Gửi liên hệ |
| GET | `/contacts` | Admin | Danh sách/lọc theo trạng thái |
| PATCH | `/contacts/{id}/status` | Admin | Cập nhật `new/read/replied` |
| GET | `/admin/summary` | Admin | Số liệu tổng quan |

Health: `GET /health` và `GET /api/v1/health/database`.
