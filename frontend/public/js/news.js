document.addEventListener("DOMContentLoaded", () => {
  const grid = document.querySelector("#news-grid"); const count = document.querySelector("#news-count");
  const load = async category => {
    grid.innerHTML = '<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>';
    try { const query = category ? `?category_type=${encodeURIComponent(category)}` : ""; const result = await Eco.request(`/articles${query}`); count.textContent = `${result.pagination.total} bài viết`; grid.innerHTML = result.items.length ? result.items.map(article=>`<article class="article-card">${Eco.image(article.image_url,article.title)}<div class="article-card-body"><span class="eyebrow">${Eco.escape(article.category_type.replace("_"," "))}</span><h3>${Eco.escape(article.title)}</h3><p>${Eco.escape(article.short_summary || "")}</p><a href="/news-detail.html?slug=${encodeURIComponent(article.slug)}">Đọc bài viết · ${article.views} lượt xem ↗</a></div></article>`).join("") : '<div class="empty-state" style="grid-column:1/-1">Chưa có bài viết trong danh mục này.</div>'; }
    catch(error){grid.innerHTML=`<div class="notice error">${Eco.escape(error.message)}</div>`;}
  };
  document.querySelector("#news-filters").addEventListener("click",event=>{const button=event.target.closest("[data-category]");if(button)load(button.dataset.category);});
  load("");
});
