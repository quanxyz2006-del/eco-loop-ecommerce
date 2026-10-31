document.addEventListener("DOMContentLoaded", async () => {
  const root = document.querySelector("#cart-content");
  let cart = Eco.readCart();
  const couponKey = "eco-loop-coupon";
  let coupon = localStorage.getItem(couponKey) || "";
  const renderEmpty = () => { root.innerHTML = '<div class="empty-state"><div class="value-icon">♡</div><h2>Giỏ hàng đang trống</h2><p class="muted">Khám phá bộ sưu tập để tìm món đồ phù hợp với bạn.</p><a class="button" href="/products.html">Khám phá sản phẩm</a></div>'; };
  if (!cart.length) { renderEmpty(); return; }
  root.innerHTML = '<div class="skeleton"></div>';
  try {
    cart = await Promise.all(cart.map(async line => {
      try { const product = await Eco.request(`/products/${line.id}`); return { ...line, name: product.name, slug: product.slug, price: product.discount_price ?? product.price, image: product.images?.[0]?.image_url || line.image, stock: product.stock_quantity }; }
      catch { return null; }
    }));
    cart = cart.filter(Boolean); Eco.writeCart(cart);
  } catch { /* use locally saved cart values if the catalog request is unavailable */ }
  if (!cart.length) { renderEmpty(); return; }
  const total = () => cart.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0);
  const render = () => {
    if (!cart.length) { renderEmpty(); return; }
    const subtotal = total(); const discount = coupon ? Math.round(subtotal * .1) : 0;
    root.innerHTML = `<div class="cart-layout"><div class="surface" style="padding:20px"><div class="section-head"><h2 class="title" style="font-size:27px;margin:0">Sản phẩm của bạn</h2><span class="muted">${cart.reduce((sum,item)=>sum+item.quantity,0)} món</span></div><table class="cart-table"><thead><tr><th>Sản phẩm</th><th>Đơn giá</th><th>Số lượng</th><th>Tạm tính</th><th></th></tr></thead><tbody>${cart.map(item=>`<tr><td><div class="cart-product">${Eco.image(item.image,item.name)}<div><strong>${Eco.escape(item.name)}</strong><div class="muted" style="font-size:11px">${Eco.escape(item.slug)}</div></div></div></td><td>${Eco.money(item.price)}</td><td><input class="qty-input" data-qty="${item.id}" aria-label="Số lượng ${Eco.escape(item.name)}" type="number" min="1" max="${item.stock || 50}" value="${item.quantity}"></td><td><strong>${Eco.money(Number(item.price)*item.quantity)}</strong></td><td><button class="button button-light button-small" data-remove="${item.id}" type="button">Xóa</button></td></tr>`).join("")}</tbody></table><a class="button button-light button-small" href="/products.html" style="margin-top:18px">← Tiếp tục mua sắm</a></div><aside class="cart-summary"><h2 class="title" style="font-size:25px">Tóm tắt</h2><div class="field"><label for="coupon-code">Mã ưu đãi từ chương trình thu gom</label><div style="display:flex;gap:7px"><input id="coupon-code" value="${Eco.escape(coupon)}" placeholder="REWEAR10-XXXXXX"><button class="button button-small" id="apply-coupon" type="button">Dùng</button></div><div id="coupon-feedback" class="muted" style="font-size:11px;margin-top:5px">${coupon ? "Đã áp dụng ưu đãi demo 10%." : "Mã được cấp sau khi yêu cầu thu gom được duyệt."}</div></div><div class="summary-row"><span>Tạm tính</span><span>${Eco.money(subtotal)}</span></div><div class="summary-row"><span>Ưu đãi</span><span>− ${Eco.money(discount)}</span></div><div class="summary-row"><span>Giao hàng</span><span>Được xác nhận sau</span></div><div class="summary-row total"><span>Tổng cộng tạm tính</span><span>${Eco.money(subtotal-discount)}</span></div><a class="button" href="/checkout.html" style="width:100%;margin-top:15px">Tiến hành thanh toán →</a><p class="muted" style="font-size:10px">Giá cuối cùng được máy chủ tính lại khi đặt hàng.</p></aside></div>`;
    root.querySelectorAll("[data-qty]").forEach(input=>input.addEventListener("change",()=>{const line=cart.find(item=>item.id===Number(input.dataset.qty));line.quantity=Math.max(1,Math.min(Number(input.max),Number(input.value)||1));Eco.writeCart(cart);render();}));
    root.querySelectorAll("[data-remove]").forEach(button=>button.addEventListener("click",()=>{cart=cart.filter(item=>item.id!==Number(button.dataset.remove));Eco.writeCart(cart);render();}));
    root.querySelector("#apply-coupon").addEventListener("click",async()=>{const input=root.querySelector("#coupon-code").value.trim();const note=root.querySelector("#coupon-feedback");try{const data=await Eco.request(`/orders/coupon?code=${encodeURIComponent(input)}`,{method:"POST"});coupon=data.code;localStorage.setItem(couponKey,coupon);Eco.toast(`Đã áp dụng ưu đãi ${data.discount_percent}%.`);render();}catch(error){coupon="";localStorage.removeItem(couponKey);note.textContent=error.message;note.style.color="#8d3823";}});
  };
  render();
});
