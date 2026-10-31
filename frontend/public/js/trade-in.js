document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#trade-in-form");
  const feedback = document.querySelector("#form-feedback");
  form.addEventListener("submit", async event => {
    event.preventDefault(); feedback.innerHTML = "";
    const button = form.querySelector("button[type=submit]"); button.disabled = true;
    const payload = Object.fromEntries(new FormData(form));
    try {
      const result = await Eco.request("/trade-in", { method: "POST", body: JSON.stringify(payload) });
      feedback.innerHTML = `<div class="notice success">Đã nhận yêu cầu <strong>#${result.id}</strong>. Trạng thái: đang chờ xác nhận. Lưu mã yêu cầu để tiện tra cứu.</div>`;
      form.reset();
    } catch (error) { feedback.innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`; }
    finally { button.disabled = false; }
  });
});
