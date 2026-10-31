# ECO-LOOP — Yêu cầu nghiệp vụ

## Mục tiêu

Website demo thương mại điện tử thời trang tuần hoàn. Khách có thể duyệt catalog, tìm kiếm/lọc, tạo đơn với hoặc không đăng nhập, đăng ký thu gom quần áo cũ, đọc nội dung và gửi liên hệ. Quản trị viên xử lý catalog, đơn, trade-in, bài viết và liên hệ.

## Vai trò

- **Khách vãng lai:** đọc nội dung, lọc sản phẩm, checkout, tra cứu đơn bằng mã, gửi trade-in và liên hệ.
- **Khách hàng:** các quyền của khách vãng lai cùng thông tin cá nhân/điểm xanh và gắn đơn với tài khoản.
- **Quản trị viên:** thao tác quản trị yêu cầu bearer JWT và quyền `admin`.

## Quy tắc chính

1. Giá và tồn kho được đọc lại từ database khi checkout; client không quyết định giá cuối.
2. Checkout kiểm tra tồn kho, tạo order/items và trừ kho trong một giao dịch. Hủy đơn ở trạng thái chờ/xác nhận trả kho.
3. Trạng thái đơn theo luồng `pending → confirmed → shipping → completed`; đơn `pending`/`confirmed` có thể hủy.
4. Voucher 10% phát sinh khi admin duyệt trade-in, chỉ dùng một lần; hủy đơn có voucher sẽ trả quyền sử dụng.
5. Danh mục tối đa hai cấp.
6. Nội dung public chỉ hiển thị bài đã xuất bản; lượt xem tăng khi mở chi tiết.
7. Catalog mặc định là demo; chỉ số CO₂ chưa được kiểm định và không phải chứng nhận.

## Ngoài phạm vi demo

Thanh toán ngân hàng chưa tích hợp cổng thanh toán; chuyển khoản là lựa chọn phương thức để nhân viên xử lý. Đánh giá sao lưu ở trình duyệt, không tổng hợp trên server. Email giao dịch, vận chuyển và kiểm chứng chứng nhận vật liệu chưa tích hợp.
