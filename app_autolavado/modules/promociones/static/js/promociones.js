// ============================
// 💡 JS del módulo Promociones
// ============================

document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Módulo Promociones cargado correctamente.");

  // Ejemplo de detección de botones
  const promoButtons = document.querySelectorAll(".btn-promocion");
  promoButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      console.log("🔹 Clic detectado en botón de promoción:", btn.dataset.id);
    });
  });
});
