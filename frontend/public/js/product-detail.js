document.addEventListener("DOMContentLoaded", async () => {
  const root = document.querySelector("#product-detail");
  const query = new URLSearchParams(location.search);
  const identifier = query.get("slug") || query.get("id");
  if (!identifier) {
    root.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><h2>Chưa chọn sản phẩm</h2><a class="button" href="/products.html">Quay lại cửa hàng</a></div>';
    return;
  }
  try {
    const product = await Eco.request(`/products/${encodeURIComponent(identifier)}`);
    const imageUrl = product.images?.find(image => image.is_thumbnail)?.image_url || product.images?.[0]?.image_url;
    root.innerHTML = `<div class="detail-image">${Eco.image(imageUrl, product.name)}</div><div class="detail-copy"><span class="eyebrow">${Eco.escape(product.category || "ECO-LOOP")}</span><h1 class="title">${Eco.escape(product.name)}</h1><p class="muted">${Eco.escape(product.description || "")}</p><div class="detail-price">${Eco.money(product.discount_price ?? product.price)} ${product.discount_price ? `<span class="old-price" style="font-size:15px">${Eco.money(product.price)}</span>` : ""}</div><span class="stock">${product.stock_quantity > 0 ? `Còn ${product.stock_quantity} sản phẩm` : "Tạm hết hàng"}</span><div class="detail-actions"><input id="detail-quantity" class="qty-input" type="number" value="1" min="1" max="${Math.max(1, product.stock_quantity)}" aria-label="Số lượng"><button class="button" id="detail-add" ${product.stock_quantity < 1 ? "disabled" : ""}>Thêm vào giỏ hàng</button></div><div class="detail-facts"><div>Chất liệu<strong>${Eco.escape(product.material_eco_type || "Đang cập nhật")}</strong></div><div>CO₂ (demo)<strong>${Number(product.co2_saved_kg).toFixed(1)} kg*</strong></div><div>Mã sản phẩm<strong>${Eco.escape(product.code)}</strong></div></div><p class="muted" style="font-size:11px">* Chỉ số trong bản demo là minh họa, không phải kết quả đánh giá vòng đời được kiểm định.</p><div class="surface product-info"><strong>Thông tin sản phẩm</strong><p class="muted" style="white-space:pre-line">${Eco.escape(product.content_detail || product.description || "")}</p><button class="button button-light button-small" id="share-product">Chia sẻ sản phẩm ↗</button></div><section class="reviews" id="reviews-section"><span class="eyebrow">Cộng đồng ECO-LOOP</span><h2 class="title" style="font-size:27px">Đánh giá sản phẩm</h2><div id="reviews-summary" class="muted">Đang tải đánh giá…</div><div id="review-form-slot"></div><div id="review-list" class="review-list"></div></section></div>`;

    document.querySelector("#detail-add").addEventListener("click", () => {
      const quantity = Math.max(1, Math.min(product.stock_quantity, Number(document.querySelector("#detail-quantity").value) || 1));
      Eco.addToCart(product, quantity);
    });
    document.querySelector("#share-product").addEventListener("click", async () => {
      try {
        if (navigator.share) await navigator.share({ title: product.name, url: location.href });
        else { await navigator.clipboard.writeText(location.href); Eco.toast("Đã sao chép đường dẫn."); }
      } catch { /* Người dùng đóng hộp thoại chia sẻ. */ }
    });

    const summary = document.querySelector("#reviews-summary");
    const list = document.querySelector("#review-list");
    const formSlot = document.querySelector("#review-form-slot");
    const renderReviews = async () => {
      const data = await Eco.request(`/products/${product.id}/reviews`);
      summary.innerHTML = data.count ? `<strong>★ ${data.average}/5</strong> · ${data.count} đánh giá` : "Chưa có đánh giá. Hãy là người đầu tiên chia sẻ trải nghiệm!";
      list.innerHTML = data.items.map(review => `<article class="review-card"><div class="review-card-head"><strong>${Eco.escape(review.full_name)}</strong><span class="review-stars" aria-label="${review.rating} trên 5 sao">${"★".repeat(review.rating)}${"☆".repeat(5 - review.rating)}</span></div><p>${Eco.escape(review.content || "Sản phẩm tốt.")}</p><time>${new Date(review.created_at).toLocaleDateString("vi-VN")}</time></article>`).join("");
    };
    const token = localStorage.getItem("eco-loop-token");
    let currentUser = null;
    if (token) {
      try { currentUser = await Eco.request("/auth/me"); } catch { localStorage.removeItem("eco-loop-token"); }
    }
    if (!currentUser) {
      formSlot.innerHTML = '<p class="notice info">Vui lòng <a href="/account.html">đăng nhập</a> để gửi đánh giá. Mỗi tài khoản có một đánh giá cho sản phẩm và có thể cập nhật sau.</p>';
    } else {
      formSlot.innerHTML = `<form id="review-form" class="review-form"><label for="review-rating">Mức đánh giá</label><select id="review-rating" required><option value="5">★★★★★ · Rất tốt</option><option value="4">★★★★☆ · Tốt</option><option value="3">★★★☆☆ · Bình thường</option><option value="2">★★☆☆☆ · Chưa hài lòng</option><option value="1">★☆☆☆☆ · Không hài lòng</option></select><label for="review-content">Chia sẻ cảm nhận (không bắt buộc)</label><textarea id="review-content" maxlength="1200" placeholder="Chất liệu, trải nghiệm sử dụng…"></textarea><button class="button button-small" type="submit">Gửi đánh giá</button><span id="review-feedback" aria-live="polite"></span></form>`;
      formSlot.querySelector("#review-form").addEventListener("submit", async event => {
        event.preventDefault();
        const button = event.currentTarget.querySelector("button[type=submit]");
        button.disabled = true;
        try {
          await Eco.request(`/products/${product.id}/reviews`, { method: "POST", body: JSON.stringify({ rating: Number(formSlot.querySelector("#review-rating").value), content: formSlot.querySelector("#review-content").value.trim() || null }) });
          formSlot.querySelector("#review-feedback").textContent = "Đã lưu đánh giá.";
          await renderReviews();
        } catch (error) {
          formSlot.querySelector("#review-feedback").textContent = error.message;
        } finally { button.disabled = false; }
      });
    }
    await renderReviews();
    const related = await Eco.request("/products?limit=4");
    document.querySelector("#related-products").innerHTML = related.items.filter(item => item.id !== product.id).slice(0, 3).map(Eco.productCard).join("");
  } catch (error) {
    root.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><h2>Không tìm thấy sản phẩm</h2><p>${Eco.escape(error.message)}</p><a class="button" href="/products.html">Về cửa hàng</a></div>`;
  }
});
