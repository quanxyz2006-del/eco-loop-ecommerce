document.addEventListener("DOMContentLoaded", async () => {
  const root = document.querySelector("#article-detail"); const slug = new URLSearchParams(location.search).get("slug");
  if (!slug) { root.innerHTML = '<div class="empty-state">Chưa chọn bài viết. <a href="/news.html">Quay lại tạp chí</a></div>'; return; }
  try {
    const article = await Eco.request(`/articles/${encodeURIComponent(slug)}`);
    document.title = `${article.title} — ECO-LOOP`;
    const paragraphs = article.content.split(/\n\s*\n/).filter(Boolean).map(text=>`<p>${Eco.escape(text)}</p>`).join("");
    let sourceLink = "";
    if (article.source_url) { const url = Eco.safeUrl(article.source_url); if (url.startsWith("https://")) sourceLink = `<p class="notice info">Nguồn tham khảo: <a href="${Eco.escape(url)}" target="_blank" rel="noopener">${Eco.escape(new URL(url).hostname)} ↗</a></p>`; }
    root.innerHTML = `<div><span class="eyebrow">${Eco.escape(article.category_type.replace("_"," "))} · ${new Date(article.created_at).toLocaleDateString("vi-VN")}</span><h1 class="title" style="font-size:clamp(34px,4vw,52px)">${Eco.escape(article.title)}</h1><p class="lead">${Eco.escape(article.short_summary || "")}</p>${article.image_url?Eco.image(article.image_url,article.title,"article-cover"):""}<div class="article-content">${paragraphs}</div>${sourceLink}<p class="muted" style="font-size:11px">${article.views} lượt xem · Bài viết chỉ cung cấp thông tin tham khảo.</p></div><aside><div class="surface"><span class="eyebrow">Đọc có chọn lọc</span><p class="muted">Hãy kiểm tra nguồn gốc vật liệu và tiêu chuẩn cụ thể trước khi tin vào tuyên bố môi trường của một sản phẩm.</p><a href="/products.html" class="button button-light button-small">Khám phá sản phẩm</a></div></aside>`;
    const related = await Eco.request("/articles?limit=3");
    document.querySelector("#related-articles").innerHTML = related.items.filter(item=>item.slug!==article.slug).slice(0,2).map(item=>`<article class="article-card">${Eco.image(item.image_url,item.title)}<div class="article-card-body"><h3>${Eco.escape(item.title)}</h3><p>${Eco.escape(item.short_summary||"")}</p><a href="/news-detail.html?slug=${encodeURIComponent(item.slug)}">Đọc tiếp ↗</a></div></article>`).join("");
  } catch(error) { root.innerHTML = `<div class="notice error">${Eco.escape(error.message)}</div>`; }
});
