(() => {
  const init = () => {
    document.querySelector("#admin-login-form")?.addEventListener("submit", () => {
      window.setTimeout(loadOwnerTools, 900);
    });
    loadOwnerTools();
  };

  const loadOwnerTools = async () => {
    if (!localStorage.getItem("eco-loop-token")) return;
    const nav = document.querySelector(".admin-nav");
    const panel = document.querySelector("#admin-panel");
    if (!nav || !panel) return;
    let owner;
    try { owner = await Eco.request("/auth/me"); } catch { return; }
    if (!owner.is_superadmin) return;

    const button = document.createElement("button");
    button.type = "button";
    button.dataset.tab = "users";
    button.textContent = "Phân quyền tài khoản";
    nav.append(button);

    nav.addEventListener("click", async event => {
      if (event.target.closest('[data-tab="users"]') !== button) return;
      event.preventDefault();
      panel.innerHTML = '<div class="skeleton"></div>';
      try {
        const result = await Eco.request("/admin/users");
        panel.innerHTML = `<div class="admin-heading"><h1>Phân quyền tài khoản</h1></div><div class="notice info">Quản trị viên được thao tác các module cửa hàng. Chỉ tài khoản chủ sở hữu mới có thể cấp hoặc thu hồi quyền quản trị.</div><div class="admin-table-wrap"><table class="admin-table"><thead><tr><th>Họ tên</th><th>Email</th><th>Loại tài khoản</th><th>Thao tác</th></tr></thead><tbody>${result.items.map(user => `<tr><td>${Eco.escape(user.full_name)}${user.is_superadmin ? ' <span class="status-pill">Chủ hệ thống</span>' : ""}</td><td>${Eco.escape(user.email)}</td><td>${user.is_superadmin ? "Superadmin" : user.role === "admin" ? "Quản trị viên" : "Khách hàng"}</td><td>${user.is_superadmin ? "—" : `<button type="button" class="button ${user.role === "admin" ? "button-light" : ""} button-small" data-change-role="${user.id}" data-next-role="${user.role === "admin" ? "customer" : "admin"}">${user.role === "admin" ? "Thu hồi quyền admin" : "Cấp quyền admin"}</button>`}</td></tr>`).join("")}</tbody></table></div>`;
        panel.querySelectorAll("[data-change-role]").forEach(action => action.addEventListener("click", async () => {
          const nextRole = action.dataset.nextRole;
          if (!window.confirm(`${nextRole === "admin" ? "Cấp quyền quản trị" : "Thu hồi quyền quản trị"} cho tài khoản này?`)) return;
          action.disabled = true;
          try {
            await Eco.request(`/admin/users/${action.dataset.changeRole}/role`, {
              method: "PATCH",
              body: JSON.stringify({ role: nextRole }),
            });
            Eco.toast("Đã cập nhật quyền tài khoản.");
            button.click();
          } catch (error) {
            Eco.toast(error.message, true);
            action.disabled = false;
          }
        }));
      } catch (error) {
        panel.innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`;
      }
    });
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
