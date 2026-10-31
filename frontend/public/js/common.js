(() => {
  const API = "/api/v1";
  const cartKey = "eco-loop-cart-v1";
  const money = value => new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND", maximumFractionDigits: 0 }).format(Number(value || 0));
  const escape = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
  const safeUrl = value => { try { const url = new URL(String(value || ""), location.origin); return ["http:", "https:"].includes(url.protocol) ? url.href : ""; } catch { return ""; } };
  const readCart = () => { try { return JSON.parse(localStorage.getItem(cartKey) || "[]"); } catch { return []; } };
  const writeCart = cart => { localStorage.setItem(cartKey, JSON.stringify(cart)); updateCartCount(); };
  const toast = (message, error = false) => {
    let node = document.querySelector(".toast");
    if (!node) { node = document.createElement("div"); node.className = "toast"; document.body.append(node); }
    node.textContent = message; node.style.background = error ? "#8d3823" : ""; node.classList.add("show");
    clearTimeout(window.__ecoToast); window.__ecoToast = setTimeout(() => node.classList.remove("show"), 2800);
  };
  const request = async (path, options = {}) => {
    const headers = new Headers(options.headers || {});
    if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
    const token = localStorage.getItem("eco-loop-token");
    if (token) headers.set("Authorization", `Bearer ${token}`);
    const response = await fetch(`${API}${path}`, { ...options, headers });
    let body; try { body = await response.json(); } catch { throw new Error("Máy chủ trả về dữ liệu không hợp lệ."); }
    if (!response.ok || body.success === false) throw new Error(body.message || `Lỗi ${response.status}`);
    return body.data;
  };
  const image = (url, alt, className = "") => `<img class="${className}" src="${escape(safeUrl(url) || "https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=70")}" alt="${escape(alt)}" loading="lazy" onerror="this.onerror=null;this.src='https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=70'">`;
  const productCard = product => {
    const thumb = product.images?.find(i => i.is_thumbnail)?.image_url || product.images?.[0]?.image_url;
    return `<article class="product-card"><a class="product-image" href="/product-detail.html?slug=${encodeURIComponent(product.slug)}">${image(thumb, product.name)}<span class="badge">${escape(product.material_eco_type || "ECO-LOOP")}</span></a><button class="quick-add" type="button" aria-label="Thêm ${escape(product.name)} vào giỏ" data-add-cart="${product.id}">+</button><div class="product-meta"><h3><a href="/product-detail.html?slug=${encodeURIComponent(product.slug)}">${escape(product.name)}</a></h3><p>${escape(product.category || "Bộ sưu tập ECO-LOOP")}</p><div class="price-row"><span>${money(product.discount_price ?? product.price)}</span>${product.discount_price ? `<span class="old-price">${money(product.price)}</span>` : ""}</div></div></article>`;
  };
  const updateCartCount = () => {
    const count = readCart().reduce((sum, item) => sum + Number(item.quantity || 0), 0);
    document.querySelectorAll("[data-cart-count]").forEach(node => node.textContent = count);
  };
  const addToCart = (product, quantity = 1) => {
    const cart = readCart(); const line = cart.find(item => item.id === product.id);
    if (line) line.quantity = Math.min(50, line.quantity + quantity);
    else cart.push({ id: product.id, name: product.name, slug: product.slug, price: product.discount_price ?? product.price, image: product.images?.[0]?.image_url || "", quantity });
    writeCart(cart); toast("Đã thêm sản phẩm vào giỏ hàng.");
  };
  const refreshAuthNav = user => {
    const adminLink = document.querySelector('.nav-actions a[href="/admin"]');
    if (adminLink) adminLink.hidden = user?.role !== "admin";
    const link = document.querySelector('.nav-actions a[href="/account.html"]');
    if (!link) return;
    link.textContent = user?.full_name || "Tài khoản";
    link.title = user?.email || "Đăng nhập hoặc đăng ký";
    link.classList.toggle("is-authenticated", Boolean(user));
  };
  const siteHeader = `
    <div class="announcement">Mặc tốt hơn · Dùng lâu hơn · Sống xanh hơn</div>
    <div class="nav-wrap"><button class="menu-toggle" aria-label="Mở menu">☰</button><a class="brand" href="/">ECO-LOOP<small>CIRCULAR LIVING</small></a>
    <nav class="nav-links"><a href="/">Trang chủ</a><a href="/products.html">Sản phẩm</a><a href="/about.html">Câu chuyện</a><a href="/trade-in.html">Thu cũ đổi mới</a><a href="/news.html">Sống xanh</a><a href="/contact.html">Liên hệ</a></nav>
    <div class="nav-actions"><a class="admin-link" href="/account.html">Tài khoản</a><a class="admin-link" href="/admin" aria-label="Quản trị">Quản trị</a><a class="cart-link" href="/cart.html">Giỏ hàng <span class="cart-count" data-cart-count>0</span></a></div></div>`;
  const siteFooter = `<div class="container"><div class="footer-grid"><div><a class="brand" href="/" style="color:white">ECO-LOOP<small style="color:#c5d7bb">CIRCULAR LIVING</small></a><p>Thời trang tuần hoàn, lựa chọn có trách nhiệm và vòng đời sản phẩm dài hơn.</p></div><div><h4>Khám phá</h4><p><a href="/products.html">Sản phẩm</a></p><p><a href="/trade-in.html">Thu cũ đổi mới</a></p><p><a href="/news.html">Cẩm nang sống xanh</a></p></div><div><h4>Hỗ trợ</h4><p><a href="/contact.html">Liên hệ</a></p><p><a href="/cart.html">Giỏ hàng</a></p><p><a href="/account.html">Tài khoản</a></p><p><a href="https://zalo.me/0966618840">Zalo: 0966618840</a></p><p><a href="mailto:quanxyz2006@gmail.com">quanxyz2006@gmail.com</a></p></div><div><h4>Cam kết minh bạch</h4><p>Thông tin và chỉ số sản phẩm trên bản demo là dữ liệu minh họa, không phải chứng nhận hay LCA đã kiểm định.</p></div></div><div class="footer-bottom"><span>© <span data-year></span> ECO-LOOP — Demo thương mại tuần hoàn</span><span>Made with care for a greener loop</span></div></div>`;
  document.addEventListener("DOMContentLoaded", () => {
    if (!document.querySelector("style[data-hidden-attribute]")) {
      const hiddenStyle = document.createElement("style");
      hiddenStyle.dataset.hiddenAttribute = "true";
      hiddenStyle.textContent = "[hidden]{display:none!important}";
      document.head.append(hiddenStyle);
    }
    if (!document.querySelector('link[data-account-review-styles]')) {
      const styles = document.createElement("link");
      styles.rel = "stylesheet";
      styles.href = "/assets/css/account-reviews.css";
      styles.dataset.accountReviewStyles = "true";
      document.head.append(styles);
    }
    document.querySelectorAll("[data-site-header]").forEach(node => node.innerHTML = siteHeader);
    document.querySelectorAll('.nav-actions a[href="/admin"]').forEach(node => { node.hidden = true; });
    document.querySelectorAll("[data-site-footer]").forEach(node => node.innerHTML = siteFooter);
    document.querySelectorAll("[data-year]").forEach(node => node.textContent = new Date().getFullYear());
    if (location.pathname === "/admin" && !document.querySelector('script[data-admin-users]')) {
      const adminUsers = document.createElement("script");
      adminUsers.src = "/assets/js/admin-users.js";
      adminUsers.dataset.adminUsers = "true";
      document.body.append(adminUsers);
    }
    if (location.pathname === "/admin" && !document.querySelector('script[data-admin-product-editor]')) {
      const productEditor = document.createElement("script");
      productEditor.src = "/assets/js/admin-product-editor.js";
      productEditor.dataset.adminProductEditor = "true";
      document.body.append(productEditor);
    }
    if (location.pathname === "/checkout.html" && !document.querySelector('script[data-checkout-payment]')) {
      const checkoutPayment = document.createElement("script");
      checkoutPayment.src = "/assets/js/checkout-payment.js";
      checkoutPayment.dataset.checkoutPayment = "true";
      document.body.append(checkoutPayment);
    }
    if (localStorage.getItem("eco-loop-token")) request("/auth/me").then(refreshAuthNav).catch(() => {
      localStorage.removeItem("eco-loop-token");
      refreshAuthNav(null);
    });
    updateCartCount();
    if (!document.querySelector(".floating-help")) {
      if (!document.querySelector("link[data-chat-styles]")) {
        const chatStyles = document.createElement("link");
        chatStyles.rel = "stylesheet";
        chatStyles.href = "/assets/css/chatbot.css";
        chatStyles.dataset.chatStyles = "true";
        document.head.append(chatStyles);
      }
      const help = document.createElement("div"); help.className = "floating-help";
      help.innerHTML = `<a href="https://zalo.me/0966618840" target="_blank" rel="noopener">Zalo 0966618840</a><a href="mailto:quanxyz2006@gmail.com">Email</a><button type="button" class="chat-launcher" aria-expanded="false">✦ Hỏi ECO-LOOP</button><section class="chat-panel" aria-label="Trợ lý ECO-LOOP" hidden><header class="chat-heading"><div><strong>Trợ lý ECO-LOOP</strong><small>Gemini · Hỏi về sản phẩm và cửa hàng</small></div><button type="button" class="chat-close" aria-label="Đóng chat">×</button></header><div class="chat-messages" role="log" aria-live="polite"></div><div class="chat-prompts"><button type="button" data-chat-prompt="Tôi muốn đăng ký và đặt hàng như thế nào?">Cách đặt hàng?</button><button type="button" data-chat-prompt="Chương trình thu cũ đổi mới hoạt động thế nào?">Thu cũ đổi mới</button></div><form class="chat-form"><label class="sr-only" for="eco-chat-input">Câu hỏi</label><textarea id="eco-chat-input" maxlength="1200" rows="2" placeholder="Nhập câu hỏi của bạn…" required></textarea><button type="submit" aria-label="Gửi câu hỏi">Gửi</button></form><p class="chat-disclaimer">Không gửi mật khẩu, OTP hoặc thông tin thẻ.</p></section>`;
      document.body.append(help);
      const panel = help.querySelector(".chat-panel");
      const launcher = help.querySelector(".chat-launcher");
      const messages = help.querySelector(".chat-messages");
      const chatForm = help.querySelector(".chat-form");
      const chatInput = help.querySelector("#eco-chat-input");
      const history = [];
      const appendMessage = (role, content) => {
        const bubble = document.createElement("p");
        bubble.className = `chat-message ${role}`;
        bubble.textContent = content;
        messages.append(bubble);
        messages.scrollTop = messages.scrollHeight;
        return bubble;
      };
      appendMessage("assistant", "Xin chào! Mình có thể giúp bạn tìm hiểu sản phẩm, cách đặt hàng và chương trình thu cũ đổi mới.");
      const openChat = open => {
        panel.hidden = !open;
        launcher.setAttribute("aria-expanded", String(open));
        if (open) chatInput.focus();
      };
      launcher.addEventListener("click", () => openChat(panel.hidden));
      help.querySelector(".chat-close").addEventListener("click", () => openChat(false));
      help.querySelectorAll("[data-chat-prompt]").forEach(button => button.addEventListener("click", () => {
        chatInput.value = button.dataset.chatPrompt;
        chatForm.requestSubmit();
      }));
      chatForm.addEventListener("submit", async event => {
        event.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;
        const submit = chatForm.querySelector("button[type=submit]");
        chatInput.value = "";
        chatInput.disabled = true;
        submit.disabled = true;
        appendMessage("user", message);
        const pending = appendMessage("assistant", "Đang tìm câu trả lời…");
        try {
          const result = await request("/chatbot/message", {
            method: "POST",
            body: JSON.stringify({ message, history: history.slice(-8) }),
          });
          pending.textContent = result.reply;
          history.push({ role: "user", content: message }, { role: "assistant", content: result.reply });
          if (history.length > 8) history.splice(0, history.length - 8);
        } catch (error) {
          pending.textContent = `${error.message} Bạn có thể liên hệ Zalo 0966618840 hoặc quanxyz2006@gmail.com.`;
        } finally {
          chatInput.disabled = false;
          submit.disabled = false;
          chatInput.focus();
          messages.scrollTop = messages.scrollHeight;
        }
      });
    }
    document.querySelector(".menu-toggle")?.addEventListener("click", () => document.querySelector(".nav-links")?.classList.toggle("menu-open"));
    document.addEventListener("click", async event => {
      const button = event.target.closest("[data-add-cart]"); if (!button) return;
      button.disabled = true;
      try { const product = await request(`/products/${button.dataset.addCart}`); addToCart(product); }
      catch (error) { toast(error.message, true); }
      finally { button.disabled = false; }
    });
  });
  window.Eco = { API, request, money, escape, safeUrl, image, productCard, toast, readCart, writeCart, addToCart, updateCartCount, refreshAuthNav };
})();
