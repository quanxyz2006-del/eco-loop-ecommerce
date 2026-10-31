document.addEventListener("DOMContentLoaded", async () => {
  const form = document.querySelector("#filter-form");
  const grid = document.querySelector("#product-grid");
  const result = document.querySelector("#result-count");
  let products = [];
  const loadCategories = async () => {
    const tree = await Eco.request("/categories");
    const select = document.querySelector("#category");
    for (const parent of tree) {
      const root = document.createElement("option"); root.value = parent.id; root.textContent = parent.name; select.append(root);
      for (const child of parent.children || []) {
        const option = document.createElement("option"); option.value = child.id; option.textContent = `— ${child.name}`; select.append(option);
      }
    }
  };
  const loadProducts = async () => {
    const query = new URLSearchParams(new FormData(form));
    for (const [key, value] of [...query.entries()]) if (!value) query.delete(key);
    grid.innerHTML = '<div class="skeleton"></div><div class="skeleton"></div>';
    try {
      const resultData = await Eco.request(`/products?${query.toString()}`);
      products = resultData.items;
      render();
      result.textContent = `${resultData.pagination.total} sản phẩm`;
    } catch (error) {
      grid.innerHTML = `<p class="notice error">${Eco.escape(error.message)}</p>`;
      result.textContent = "Không tải được danh sách";
    }
  };
  const render = () => {
    const sort = document.querySelector("#sort").value;
    const rows = [...products];
    if (sort === "price-low") rows.sort((a, b) => (a.discount_price ?? a.price) - (b.discount_price ?? b.price));
    if (sort === "price-high") rows.sort((a, b) => (b.discount_price ?? b.price) - (a.discount_price ?? a.price));
    grid.innerHTML = rows.length ? rows.map(Eco.productCard).join("") : '<div class="empty-state" style="grid-column:1/-1"><div class="value-icon">⌕</div><h3>Chưa tìm thấy sản phẩm phù hợp</h3><p class="muted">Thử thay đổi bộ lọc hoặc từ khóa nhé.</p></div>';
  };
  form.addEventListener("submit", event => { event.preventDefault(); loadProducts(); });
  document.querySelector("#sort").addEventListener("change", render);
  document.querySelector("#clear-filters").addEventListener("click", () => { form.reset(); loadProducts(); });
  try { await loadCategories(); } catch (error) { Eco.toast(error.message, true); }
  await loadProducts();
});
