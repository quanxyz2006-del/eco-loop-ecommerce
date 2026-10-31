document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#contact-form"); const feedback = document.querySelector("#contact-feedback");
  form.addEventListener("submit", async event => {
    event.preventDefault(); feedback.innerHTML = "";
    const button=form.querySelector("button[type=submit]");button.disabled=true;
    try { const result=await Eco.request("/contacts",{method:"POST",body:JSON.stringify(Object.fromEntries(new FormData(form)))});feedback.innerHTML=`<div class="notice success">${Eco.escape(result.message || "Tin nhắn đã được gửi.")} Mã tiếp nhận: #${result.id}.</div>`;form.reset(); }
    catch(error){feedback.innerHTML=`<div class="notice error">${Eco.escape(error.message)}</div>`;}
    finally{button.disabled=false;}
  });
});
