# Nguồn dữ liệu và ghi chú mẫu

## Dữ liệu mẫu của storefront

Tên sản phẩm, mã hàng, giá, tồn kho, mô tả, vật liệu, ảnh và chỉ số CO₂ trong catalog mặc định là dữ liệu giả lập phục vụ demo. Chúng không mô tả hàng hóa có thật, không xác nhận chứng nhận (GRS/RCS hay tiêu chuẩn khác), và các con số CO₂ không phải kết quả đánh giá vòng đời (LCA). Nội dung tương tự được ghi rõ trong trang cửa hàng và bản ghi chi tiết sản phẩm.

Ảnh demo được nhúng từ CDN của Unsplash; ảnh có thể thay đổi hoặc không tải được nếu trình duyệt không có kết nối internet.

## Nguồn biên soạn bài viết

- [Textile Exchange — Preferred Synthetics](https://textileexchange.org/glossary/preferred-synthetics/): thuật ngữ của Textile Exchange về sợi tổng hợp ưu tiên; trang nêu polyester tái chế và nylon tái chế trong nhóm này, đồng thời tham chiếu các tiêu chuẩn chuỗi hành trình như RCS/GRS. Bài viết không suy diễn rằng mọi sản phẩm dùng sợi đó đều được chứng nhận hoặc có tác động môi trường tốt hơn trong mọi trường hợp.
- [Textile Exchange — Preferred Fiber/Material](https://textileexchange.org/glossary/preferred-fiber-material-pfm/): giải thích thuật ngữ “preferred” và các cách chứng minh/đánh giá thuộc tính vật liệu.
- [European Environment Agency — Management of used and waste textiles in Europe’s circular economy](https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy): số liệu năm 2020 của EU trong bài demo: 6,95 triệu tấn (khoảng 16 kg/người); 4,4 kg/người được thu gom riêng cho tái sử dụng/tái chế và 11,6 kg/người vào rác hỗn hợp. Đây là số liệu EU năm 2020, không đại diện Việt Nam hoặc hiện trạng mới nhất.
- [European Environment Agency — What happens to used textile products?](https://www.eea.europa.eu/en/about/contact-us/faqs/what-happens-to-our-used-textile-products-such-as-discarded-clothing-or-shoes): tổng quan về thu gom, tái sử dụng, tái chế và các hạn chế của hệ thống xử lý.

Seeder Python tự thêm catalog/bài viết khi cơ sở dữ liệu còn trống. [seed_data.sql](../database/seed_data.sql) là lựa chọn thay thế dành cho MySQL; không cần chạy cả hai cách.
