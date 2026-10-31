document.addEventListener("DOMContentLoaded", async () => {
  const visitorKey = "eco-loop-demo-visits";
  const visits = Number(localStorage.getItem(visitorKey) || 0) + 1;
  localStorage.setItem(visitorKey, String(visits));
  const visitorNode = document.querySelector("#visitor-count");
  if (visitorNode) visitorNode.textContent = new Intl.NumberFormat("vi-VN").format(visits);
  const productsNode = document.querySelector("#featured-products");
  const articlesNode = document.querySelector("#featured-articles");
  try {
    const [products, articles] = await Promise.all([Eco.request("/products?limit=4"), Eco.request("/articles?limit=3")]);
    productsNode.innerHTML = products.items.map(Eco.productCard).join("");
    articlesNode.innerHTML = articles.items.map(article => `<article class="article-card">${Eco.image(article.image_url, article.title)}<div class="article-card-body"><span class="eyebrow">${Eco.escape(article.category_type.replace("_", " "))}</span><h3>${Eco.escape(article.title)}</h3><p>${Eco.escape(article.short_summary || "")}</p><a href="/news-detail.html?slug=${encodeURIComponent(article.slug)}">Đọc bài viết ↗</a></div></article>`).join("");
  } catch (error) {
    productsNode.innerHTML = `<p class="notice error">${Eco.escape(error.message)}</p>`;
    articlesNode.innerHTML = "<p class='muted'>Chưa thể tải bài viết.</p>";
  }
});
