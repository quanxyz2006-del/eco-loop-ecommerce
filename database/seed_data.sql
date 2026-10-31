-- DATA MẪU CHO DEMO: tên sản phẩm, giá, tồn kho và CO2 là dữ liệu giả lập.
-- Ảnh tải từ Unsplash; các bài viết tham khảo nguồn gốc được gắn source_url.
USE eco_loop;

INSERT INTO categories (name, slug, description) VALUES
('Trang phục', 'trang-phuc', 'Trang phục dùng hằng ngày'),
('Phụ kiện', 'phu-kien-goc', 'Phụ kiện tái sử dụng')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO categories (name, slug, parent_id) VALUES
('Áo thun', 'ao-thun', (SELECT id FROM (SELECT id FROM categories WHERE slug='trang-phuc') AS root_category)),
('Áo sơ mi', 'ao-so-mi', (SELECT id FROM (SELECT id FROM categories WHERE slug='trang-phuc') AS root_category)),
('Áo khoác', 'ao-khoac', (SELECT id FROM (SELECT id FROM categories WHERE slug='trang-phuc') AS root_category)),
('Quần dài', 'quan-dai', (SELECT id FROM (SELECT id FROM categories WHERE slug='trang-phuc') AS root_category)),
('Túi tote', 'tui-tote', (SELECT id FROM (SELECT id FROM categories WHERE slug='phu-kien-goc') AS root_category)),
('Phụ kiện khác', 'phu-kien', (SELECT id FROM (SELECT id FROM categories WHERE slug='phu-kien-goc') AS root_category))
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO products
(category_id, name, code, slug, price, discount_price, material_eco_type, co2_saved_kg, stock_quantity, description, content_detail, is_active)
VALUES
((SELECT id FROM categories WHERE slug='ao-thun'), 'Áo thun Sương Mai', 'ECO-TS-001', 'ao-thun-suong-mai', 329000, 289000, 'Cotton hữu cơ (demo)', 0.8, 32, 'Áo thun tối giản, mềm nhẹ, phối đồ hằng ngày.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='ao-thun'), 'Áo thun Mầm Xanh', 'ECO-TS-002', 'ao-thun-mam-xanh', 359000, NULL, 'Sợi tre pha cotton (demo)', 0.6, 24, 'Phom relaxed thoáng mát, bảng màu lấy cảm hứng từ thiên nhiên.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='ao-so-mi'), 'Sơ mi Vệt Nắng', 'ECO-SH-003', 'so-mi-vet-nang', 549000, NULL, 'Cotton và polyester tái chế (demo)', 1.1, 18, 'Sơ mi dễ mặc cho ngày làm việc lẫn cuối tuần.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='ao-khoac'), 'Áo khoác Gió Rừng', 'ECO-JK-004', 'ao-khoac-gio-rung', 890000, 790000, 'Polyester tái chế (demo)', 1.7, 12, 'Lớp khoác nhẹ gọn, phù hợp những chuyến đi ngắn.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='tui-tote'), 'Túi tote Vòng Đời', 'ECO-BG-005', 'tui-tote-vong-doi', 219000, NULL, 'Vải canvas tái sử dụng (demo)', 0.4, 45, 'Túi nhiều không gian cho sách, bình nước và vật dụng hằng ngày.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='phu-kien'), 'Mũ bucket Lá Non', 'ECO-AC-006', 'mu-bucket-la-non', 259000, NULL, 'Cotton dư thừa sản xuất (demo)', 0.3, 21, 'Phụ kiện gọn nhẹ với vành mềm, dễ gấp mang theo.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='quan-dai'), 'Quần dài Đường Mòn', 'ECO-PT-007', 'quan-dai-duong-mon', 629000, NULL, 'Cotton pha sợi tái chế (demo)', 1.0, 15, 'Phom suông thoải mái, túi sâu tiện dụng.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE),
((SELECT id FROM categories WHERE slug='ao-khoac'), 'Áo khoác denim Hồi Sinh', 'ECO-DN-008', 'ao-khoac-denim-hoi-sinh', 990000, 899000, 'Denim pha cotton tái chế (demo)', 1.4, 9, 'Phom denim cổ điển, gợi ý mặc lâu và sửa chữa.', 'Dữ liệu demo; chất liệu và CO2 chỉ minh họa, chưa được kiểm định vòng đời.', TRUE)
ON DUPLICATE KEY UPDATE name = VALUES(name), price = VALUES(price), stock_quantity = VALUES(stock_quantity);

INSERT INTO product_images (product_id, image_url, is_thumbnail)
SELECT p.id, image_data.image_url, TRUE
FROM products AS p
JOIN (
  SELECT 'ao-thun-suong-mai' AS slug, 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=1000&q=85' AS image_url UNION ALL
  SELECT 'ao-thun-mam-xanh', 'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=1000&q=85' UNION ALL
  SELECT 'so-mi-vet-nang', 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?auto=format&fit=crop&w=1000&q=85' UNION ALL
  SELECT 'ao-khoac-gio-rung', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=1000&q=85' UNION ALL
  SELECT 'tui-tote-vong-doi', 'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=1000&q=85' UNION ALL
  SELECT 'mu-bucket-la-non', 'https://images.unsplash.com/photo-1521369909029-2afed882baee?auto=format&fit=crop&w=1000&q=85' UNION ALL
  SELECT 'quan-dai-duong-mon', 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=1000&q=85' UNION ALL
  SELECT 'ao-khoac-denim-hoi-sinh', 'https://images.unsplash.com/photo-1543076447-215ad9ba6923?auto=format&fit=crop&w=1000&q=85'
) AS image_data ON image_data.slug = p.slug
WHERE NOT EXISTS (
  SELECT 1 FROM product_images AS existing WHERE existing.product_id = p.id AND existing.is_thumbnail = TRUE
);

-- Nguồn đọc thêm: Textile Exchange (https://textileexchange.org/glossary/preferred-synthetics/)
-- và European Environment Agency (https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy).
INSERT INTO articles (title, slug, category_type, short_summary, content, image_url, source_url, views, is_published) VALUES
('Mặc lâu hơn, bắt đầu một vòng đời mới', 'mac-lau-hon-vong-doi-moi', 'eco_guide', 'Sửa chữa, trao đổi và tái sử dụng là những lựa chọn thiết thực trước khi một món đồ trở thành rác thải.', 'Một chiếc áo được mặc lâu hơn thường không cần thay thế sớm. Hãy ưu tiên giặt đúng hướng dẫn, sửa chi tiết nhỏ và trao tặng hoặc bán lại khi bạn không còn sử dụng. Tái chế là một phần của kinh tế tuần hoàn, nhưng kéo dài thời gian sử dụng giúp giữ giá trị sản phẩm lâu hơn. Bài viết minh họa, không phải kết quả kiểm định vòng đời sản phẩm.', 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?auto=format&fit=crop&w=1400&q=85', 'https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy', 0, TRUE),
('Vải tái chế: đọc nhãn và truy xuất nguồn gốc', 'vai-tai-che-doc-nhan-truy-xuat', 'news', 'Tên gọi vật liệu chưa đủ để chứng minh tác động; hãy xem thành phần, tiêu chuẩn và thông tin chuỗi cung ứng.', 'Polyester tái chế và nylon tái chế được Textile Exchange xếp vào nhóm sợi tổng hợp ưu tiên trong khung thuật ngữ của tổ chức. Điều đó không tự động chứng minh mọi sản phẩm làm từ chúng đều bền vững. Người mua nên tìm tỷ lệ thành phần, tiêu chuẩn bên thứ ba phù hợp và khả năng truy xuất chuỗi cung ứng. Sản phẩm ở ECO-LOOP demo không đại diện cho chứng nhận hàng hóa thật.', 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=1400&q=85', 'https://textileexchange.org/glossary/preferred-synthetics/', 0, TRUE),
('Tái sử dụng hay tái chế? Chọn đúng bước tiếp theo', 'tai-su-dung-hay-tai-che', 'eco_guide', 'Phân loại tình trạng món đồ trước khi gửi đi để tăng cơ hội tiếp tục sử dụng.', 'Nếu quần áo còn tốt, hãy cân nhắc sửa chữa, tặng lại hoặc bán lại trước. Nếu không thể mặc tiếp, hãy tìm chương trình thu gom có thông tin rõ về khâu phân loại và xử lý. Cơ quan Môi trường châu Âu lưu ý hoạt động tái sử dụng và tái chế phụ thuộc vào năng lực phân loại, xử lý và thị trường đầu ra.', 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1400&q=85', 'https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy', 0, TRUE)
 ,('Rác thải dệt may: nhìn vào dữ liệu trước khi hành động', 'du-lieu-rac-thai-det-may-eu', 'news', 'EEA ước tính EU tạo ra 6,95 triệu tấn rác thải dệt may năm 2020; phần lớn vẫn nằm trong rác sinh hoạt hỗn hợp.', 'Theo European Environment Agency, năm 2020 EU tạo ra khoảng 6,95 triệu tấn rác thải dệt may, tương đương khoảng 16 kg mỗi người. Khoảng 4,4 kg mỗi người được thu gom riêng để tái sử dụng hoặc tái chế, còn 11,6 kg mỗi người đi vào rác sinh hoạt hỗn hợp. Đây là số liệu của EU trong năm 2020, không phải số liệu Việt Nam hay tình hình hiện tại. Năng lực phân loại và xử lý cũng rất quan trọng.', 'https://images.unsplash.com/photo-1531058020387-3be344556be6?auto=format&fit=crop&w=1400&q=85', 'https://www.eea.europa.eu/en/analysis/publications/management-of-used-and-waste-textiles-in-europes-circular-economy', 0, TRUE)
ON DUPLICATE KEY UPDATE title = VALUES(title), short_summary = VALUES(short_summary);
