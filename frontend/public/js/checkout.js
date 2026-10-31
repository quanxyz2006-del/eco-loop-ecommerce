document.addEventListener("DOMContentLoaded", async () => {
  const form = document.querySelector("#checkout-form"); const summary = document.querySelector("#checkout-summary");
  const feedback = document.querySelector("#checkout-feedback"); const cart = Eco.readCart();
  if (!localStorage.getItem("eco-loop-token")) { location.replace("/account.html?next=checkout"); return; }
  try {
    const user = await Eco.request("/auth/me");
    form.elements.full_name.value = user.full_name || "";
    form.elements.phone.value = user.phone || "";
    form.elements.shipping_address.value = user.address || "";
  } catch {
    localStorage.removeItem("eco-loop-token");
    location.replace("/account.html?next=checkout");
    return;
  }
  if (!cart.length) { form.innerHTML = '<div class="empty-state"><h2>Giỏ hàng trống</h2><a class="button" href="/products.html">Chọn sản phẩm</a></div>'; summary.remove(); return; }
  const subtotal = cart.reduce((sum,item)=>sum+Number(item.price)*Number(item.quantity),0);
  const coupon = localStorage.getItem("eco-loop-coupon") || ""; const discount = coupon ? Math.round(subtotal*.1) : 0;
  summary.innerHTML = `<h2 class="title" style="font-size:25px">Đơn hàng</h2>${cart.map(item=>`<div class="summary-row"><span>${Eco.escape(item.name)} × ${item.quantity}</span><strong>${Eco.money(Number(item.price)*item.quantity)}</strong></div>`).join("")}<div class="summary-row"><span>Tạm tính</span><span>${Eco.money(subtotal)}</span></div><div class="summary-row"><span>Ưu đãi ${coupon?`(${Eco.escape(coupon)})`:""}</span><span>− ${Eco.money(discount)}</span></div><div class="summary-row total"><span>Tổng tạm tính</span><span>${Eco.money(subtotal-discount)}</span></div><p class="muted" style="font-size:11px">Máy chủ sẽ xác thực tồn kho và tính lại tổng tiền khi xác nhận.</p>`;
  form.addEventListener("submit", async event => {
    event.preventDefault(); feedback.innerHTML = "";
    const button = form.querySelector("button[type=submit]"); button.disabled = true;
    const values = Object.fromEntries(new FormData(form));
    const payload = { ...values, coupon_code: coupon || null, items: cart.map(item=>({product_id:item.id,quantity:Number(item.quantity)})) };
    try {
      const order = await Eco.request("/orders", { method: "POST", body: JSON.stringify(payload) });
      Eco.writeCart([]); localStorage.removeItem("eco-loop-coupon");
      form.innerHTML = `<div class="empty-state"><div class="value-icon">✓</div><span class="eyebrow">Order confirmed</span><h2>Đặt hàng thành công</h2><p class="muted">Mã đơn hàng của bạn</p><h2 style="color:var(--forest)">${Eco.escape(order.order_code)}</h2><p class="muted">Tổng thanh toán: <strong>${Eco.money(order.final_amount)}</strong></p><p class="muted">Hãy lưu mã này để tra cứu trạng thái đơn hàng.</p><button class="button button-light" id="track-order" type="button">Tra cứu đơn hàng</button><a class="button" href="/products.html">Tiếp tục khám phá</a><div id="order-tracking"></div></div>`;
      form.querySelector("#track-order").addEventListener("click",async()=>{const tracking=document.querySelector("#order-tracking");try{const result=await Eco.request(`/orders/${encodeURIComponent(order.order_code)}`);tracking.innerHTML=`<div class="notice info">Trạng thái: ${Eco.escape(result.status)} · Tổng tiền: ${Eco.money(result.final_amount)}</div>`;}catch(error){tracking.innerHTML=`<div class="notice error">${Eco.escape(error.message)}</div>`;}});
      summary.innerHTML = "";
    } catch (error) { feedback.innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`; button.disabled = false; }
  });
});
