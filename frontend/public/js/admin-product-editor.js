(() => {
  const panel = document.querySelector("#admin-panel");
  if (!panel || !window.Eco) return;

  const productsById = new Map();
  let loading = false;
  const api = Eco.request;
  const escape = Eco.escape;
  const value = (product, key) => escape(product[key] ?? "");

  const attachEditButtons = async () => {
    const toggles = [...panel.querySelectorAll("button[data-toggle-product]")];
    if (!toggles.length || toggles.some(button => button.parentElement.querySelector("[data-edit-product]")) || loading) return;
    loading = true;
    try {
      const result = await api("/products/admin/all?limit=100");
      productsById.clear();
      result.items.forEach(product => productsById.set(String(product.id), product));
      toggles.forEach(button => {
        if (!productsById.has(button.dataset.toggleProduct)) return;
        const edit = document.createElement("button");
        edit.type = "button";
        edit.className = "button button-light button-small";
        edit.dataset.editProduct = button.dataset.toggleProduct;
        edit.textContent = "Sửa";
        edit.style.marginRight = "6px";
        button.before(edit);
      });
    } catch (error) {
      Eco.toast(`Không tải được sản phẩm để sửa: ${error.message}`, true);
    } finally {
      loading = false;
    }
  };

  const showEditor = async product => {
    try {
      const tree = await api("/categories");
      const categories = tree.flatMap(category => [category, ...(category.children || [])]);
      const categoryOptions = categories.map(category => `<option value="${category.id}" ${category.id === product.category_id ? "selected" : ""}>${escape(category.name)}</option>`).join("");
      const images = (product.images || []).map(image => image.image_url).join("\n");
      const formMarkup = `<section class="surface" data-product-editor-form style="margin-bottom:20px"><h2 class="title" style="font-size:25px">Chỉnh sửa sản phẩm</h2><form><div class="form-grid"><div class="field"><label>Tên sản phẩm</label><input name="name" required minlength="2" value="${value(product, "name")}"></div><div class="field"><label>Mã sản phẩm</label><input name="code" required value="${value(product, "code")}"></div><div class="field"><label>Đường dẫn (slug)</label><input name="slug" required value="${value(product, "slug")}"></div><div class="field"><label>Danh mục</label><select name="category_id" required>${categoryOptions}</select></div><div class="field"><label>Giá niêm yết (₫)</label><input name="price" type="number" min="1" step="1" required value="${value(product, "price")}"></div><div class="field"><label>Giá khuyến mãi (để trống nếu không có)</label><input name="discount_price" type="number" min="1" step="1" value="${value(product, "discount_price")}"></div><div class="field"><label>Chất liệu</label><input name="material_eco_type" value="${value(product, "material_eco_type")}"></div><div class="field"><label>Tồn kho</label><input name="stock_quantity" type="number" min="0" required value="${value(product, "stock_quantity")}"></div><div class="field"><label>CO₂ tiết kiệm (kg)</label><input name="co2_saved_kg" type="number" min="0" step="0.1" value="${value(product, "co2_saved_kg")}"></div><div class="field"><label>Trạng thái</label><select name="is_active"><option value="true" ${product.is_active ? "selected" : ""}>Đang bán</option><option value="false" ${!product.is_active ? "selected" : ""}>Đã ẩn</option></select></div><div class="field span-2"><label>Mô tả ngắn</label><textarea name="description">${value(product, "description")}</textarea></div><div class="field span-2"><label>Nội dung chi tiết</label><textarea name="content_detail">${value(product, "content_detail")}</textarea></div><div class="field span-2"><label>URL ảnh (mỗi dòng một ảnh)</label><textarea name="images">${escape(images)}</textarea></div></div><div data-editor-feedback aria-live="polite"></div><button class="button" type="submit">Lưu thay đổi</button> <button class="button button-light" type="button" data-cancel-editor>Đóng</button></form></section>`;
      panel.insertAdjacentHTML("afterbegin", formMarkup);
      const editor = panel.querySelector("[data-product-editor-form]");
      editor.querySelector("[data-cancel-editor]").addEventListener("click", () => editor.remove());
      editor.querySelector("form").addEventListener("submit", async event => {
        event.preventDefault();
        const form = event.currentTarget;
        const submit = form.querySelector('button[type="submit"]');
        const fields = Object.fromEntries(new FormData(form));
        submit.disabled = true;
        try {
          await api(`/products/${product.id}`, {
            method: "PUT",
            body: JSON.stringify({
              ...fields,
              category_id: Number(fields.category_id),
              price: Number(fields.price),
              discount_price: fields.discount_price ? Number(fields.discount_price) : null,
              stock_quantity: Number(fields.stock_quantity),
              co2_saved_kg: Number(fields.co2_saved_kg || 0),
              is_active: fields.is_active === "true",
              images: fields.images.split(/\r?\n/).map(url => url.trim()).filter(Boolean),
            }),
          });
          Eco.toast("Đã cập nhật sản phẩm.");
          document.querySelector('[data-tab="products"]')?.click();
        } catch (error) {
          editor.querySelector("[data-editor-feedback]").innerHTML = `<div class="notice error">${escape(error.message)}</div>`;
          submit.disabled = false;
        }
      });
      editor.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      Eco.toast(`Không mở được biểu mẫu: ${error.message}`, true);
    }
  };

  panel.addEventListener("click", event => {
    const button = event.target.closest("[data-edit-product]");
    const product = button && productsById.get(button.dataset.editProduct);
    if (product) showEditor(product);
  });

  new MutationObserver(attachEditButtons).observe(panel, { childList: true, subtree: true });
})();
