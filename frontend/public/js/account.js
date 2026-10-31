document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector("#account-content");
  const continueToCheckout = new URLSearchParams(location.search).get("next") === "checkout";

  const renderVerification = email => {
    root.innerHTML = `<span class="eyebrow">Bảo mật tài khoản</span><h2 class="title" style="font-size:30px">Xác minh email</h2><p class="muted">Nhập mã 6 chữ số đã gửi tới <strong>${Eco.escape(email)}</strong>. Mã có hiệu lực trong 10 phút.</p><form id="verify-form"><div class="field"><label for="verify-code">Mã xác minh</label><input id="verify-code" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" required></div><div id="verify-feedback" aria-live="polite"></div><button class="button" type="submit">Xác minh email</button><button class="button button-light" id="resend-code" type="button" style="margin-left:8px">Gửi mã mới</button></form><p class="muted" style="font-size:12px">Không thấy thư? Hãy kiểm tra mục Spam/Thư rác.</p>`;
    root.querySelector("#verify-form").addEventListener("submit", async event => {
      event.preventDefault();
      const button = event.currentTarget.querySelector("button[type=submit]");
      button.disabled = true;
      try {
        await Eco.request("/auth/verify-email", { method: "POST", body: JSON.stringify({ email, code: root.querySelector("#verify-code").value.trim() }) });
        Eco.toast("Email đã xác minh. Mời bạn đăng nhập.");
        renderLogin(email);
      } catch (error) {
        root.querySelector("#verify-feedback").innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`;
      } finally { button.disabled = false; }
    });
    root.querySelector("#resend-code").addEventListener("click", async event => {
      const button = event.currentTarget;
      button.disabled = true;
      try {
        await Eco.request("/auth/resend-verification", { method: "POST", body: JSON.stringify({ email }) });
        root.querySelector("#verify-feedback").innerHTML = '<div class="notice success">Nếu yêu cầu xác minh còn hiệu lực, mã mới đã được gửi.</div>';
      } catch (error) {
        root.querySelector("#verify-feedback").innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`;
      } finally { button.disabled = false; }
    });
  };

  const renderAccount = async () => {
    const user = await Eco.request("/auth/me");
    if (continueToCheckout) { location.replace("/checkout.html"); return; }
    let orders = { items: [] };
    try { orders = await Eco.request("/orders/mine?limit=50"); } catch { /* Keep profile usable if order history is temporarily unavailable. */ }
    root.innerHTML = `<span class="eyebrow">Tài khoản ECO-LOOP</span><h2 class="title" style="font-size:31px">Xin chào, ${Eco.escape(user.full_name)}</h2><p class="muted">${Eco.escape(user.email)} · ${user.role === "admin" ? "Quản trị viên" : "Khách hàng"}</p><div class="story-band" style="padding:25px;margin:20px 0"><div><span class="eyebrow" style="color:var(--lime)">Green points</span><strong style="display:block;font:600 32px 'Playfair Display',serif;color:var(--lime)">${user.green_points}</strong><span>điểm xanh</span></div><p>Điểm xanh tích lũy từ các đơn hàng hoàn tất và hoạt động thu gom.</p></div><h3 class="title" style="font-size:24px">Đơn hàng của tôi</h3>${orders.items.length ? `<div class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Mã đơn</th><th>Ngày</th><th>Trạng thái</th><th>Tổng tiền</th></tr></thead><tbody>${orders.items.map(order => `<tr><td>${Eco.escape(order.order_code)}</td><td>${new Date(order.created_at).toLocaleDateString("vi-VN")}</td><td>${Eco.escape(order.status)}</td><td>${Eco.money(order.final_amount)}</td></tr>`).join("")}</tbody></table></div>` : '<p class="muted">Bạn chưa có đơn hàng nào.</p>'}<button id="account-logout" class="button button-light" style="margin-top:20px">Đăng xuất</button>`;
    Eco.refreshAuthNav(user);
    root.querySelector("#account-logout").addEventListener("click", () => { localStorage.removeItem("eco-loop-token"); Eco.refreshAuthNav(null); renderLogin(); });
  };

  const renderLogin = (prefillEmail = "") => {
    root.innerHTML = `<div class="account-tabs"><button class="button button-small" data-mode="login">Đăng nhập</button><button class="button button-light button-small" data-mode="register">Tạo tài khoản</button></div><form id="account-form"><h2 class="title" id="account-title" style="font-size:29px">Đăng nhập</h2><div class="field" id="name-field" hidden><label for="full_name">Họ và tên</label><input id="full_name" name="full_name" minlength="2" autocomplete="name"></div><div class="field"><label for="email">Email</label><input id="email" name="email" type="email" required autocomplete="email" value="${Eco.escape(prefillEmail)}"></div><div class="field"><label for="password">Mật khẩu</label><input id="password" name="password" type="password" required minlength="8" autocomplete="current-password"></div><div class="field" id="phone-field" hidden><label for="phone">Điện thoại (không bắt buộc)</label><input id="phone" name="phone" autocomplete="tel"></div><div class="field" id="address-field" hidden><label for="address">Địa chỉ (không bắt buộc)</label><textarea id="address" name="address" autocomplete="street-address"></textarea></div><div id="account-feedback" aria-live="polite"></div><button class="button" type="submit">Đăng nhập</button></form><p class="muted" style="font-size:12px;margin-top:15px">Đăng ký cần xác minh quyền truy cập email. Mật khẩu tối thiểu 8 ký tự.</p>`;
    let mode = "login";
    const setMode = next => {
      mode = next;
      const register = mode === "register";
      root.querySelector("#account-title").textContent = register ? "Tạo tài khoản" : "Đăng nhập";
      root.querySelector("#name-field").hidden = !register;
      root.querySelector("#phone-field").hidden = !register;
      root.querySelector("#address-field").hidden = !register;
      root.querySelector("#full_name").required = register;
      root.querySelector("#password").autocomplete = register ? "new-password" : "current-password";
      root.querySelector("form button[type=submit]").textContent = register ? "Tiếp tục xác minh email" : "Đăng nhập";
      root.querySelectorAll("[data-mode]").forEach(button => button.classList.toggle("button-light", button.dataset.mode !== mode));
    };
    root.querySelectorAll("[data-mode]").forEach(button => button.addEventListener("click", () => setMode(button.dataset.mode)));
    root.querySelector("#account-form").addEventListener("submit", async event => {
      event.preventDefault();
      const form = event.currentTarget;
      const button = form.querySelector("button[type=submit]");
      button.disabled = true;
      const fields = Object.fromEntries(new FormData(form));
      try {
        if (mode === "register") {
          const registration = { ...fields, email: String(fields.email).trim().toLowerCase() };
          await Eco.request("/auth/register", { method: "POST", body: JSON.stringify(registration) });
          renderVerification(registration.email);
          return;
        }
        const auth = await Eco.request("/auth/login", { method: "POST", body: JSON.stringify({ email: fields.email, password: fields.password }) });
        localStorage.setItem("eco-loop-token", auth.access_token);
        await renderAccount();
      } catch (error) {
        root.querySelector("#account-feedback").innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`;
      } finally { button.disabled = false; }
    });
  };

  if (localStorage.getItem("eco-loop-token")) {
    renderAccount().catch(() => { localStorage.removeItem("eco-loop-token"); Eco.refreshAuthNav(null); renderLogin(); });
  } else renderLogin();
});
