(() => {
  const form = document.querySelector("#checkout-form");
  const paymentMethod = form?.elements.payment_method;
  if (!form || !paymentMethod || !window.Eco) return;

  const box = document.createElement("section");
  box.id = "bank-transfer-details";
  box.className = "notice info";
  box.hidden = true;
  box.style.margin = "16px 0";
  paymentMethod.closest(".field")?.after(box);

  const renderTransferDetails = order => {
    const amount = order ? `<p><strong>Số tiền: ${Eco.money(order.final_amount)}</strong></p>` : "";
    const transferNote = order ? `ECO-LOOP ${order.order_code}` : "Mã đơn hàng sẽ được tạo sau khi bạn xác nhận đặt hàng.";
    box.innerHTML = `<h3 style="margin-top:0">Chuyển khoản VietQR</h3><img src="/assets/images/payment-qr.png" alt="Mã QR chuyển khoản ECO-LOOP" style="display:block;width:min(100%,360px);height:auto;margin:12px auto;border-radius:12px"><p>Người nhận: <strong>HOANG MINH QUAN</strong></p><p>Liên hệ: <a href="tel:0966618840">0966618840</a></p>${amount}<p>Nội dung chuyển khoản: <strong>${Eco.escape(transferNote)}</strong></p><p>Quét QR bằng ứng dụng ngân hàng. Kiểm tra đúng người nhận và số tiền trước khi xác nhận; QR tĩnh có thể cần nhập số tiền/nội dung thủ công.</p>`;
    box.hidden = false;
  };

  const refresh = () => {
    if (paymentMethod.value === "bank_transfer") renderTransferDetails();
    else box.hidden = true;
  };
  paymentMethod.addEventListener("change", refresh);
  refresh();

  const request = Eco.request;
  Eco.request = async (path, options = {}) => {
    const result = await request(path, options);
    if (path === "/orders" && options.method === "POST" && paymentMethod.value === "bank_transfer") {
      window.__ecoBankTransferOrder = result;
    }
    return result;
  };

  new MutationObserver(() => {
    const order = window.__ecoBankTransferOrder;
    if (!order || !form.querySelector("#track-order") || form.querySelector("#bank-transfer-confirmation")) return;
    const confirmation = document.createElement("section");
    confirmation.id = "bank-transfer-confirmation";
    confirmation.className = "notice info";
    confirmation.style.marginTop = "18px";
    confirmation.innerHTML = `<h3>Hoàn tất thanh toán chuyển khoản</h3><p>Đơn <strong>${Eco.escape(order.order_code)}</strong> đã được tạo.</p><p>Số tiền cần chuyển: <strong>${Eco.money(order.final_amount)}</strong></p><p>Nội dung chuyển khoản: <strong>ECO-LOOP ${Eco.escape(order.order_code)}</strong></p><img src="/assets/images/payment-qr.png" alt="Mã QR chuyển khoản ECO-LOOP" style="display:block;width:min(100%,360px);height:auto;margin:12px auto;border-radius:12px"><p>Người nhận HOANG MINH QUAN · Zalo <a href="tel:0966618840">0966618840</a>. Nếu QR không tự điền số tiền, vui lòng nhập đúng số tiền và nội dung ở trên.</p>`;
    form.append(confirmation);
  }).observe(form, { childList: true, subtree: true });
})();
