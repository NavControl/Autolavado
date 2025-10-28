// ===========================
// INTERACTIVIDAD DEL MÓDULO
// ===========================
document.addEventListener("DOMContentLoaded", () => {

    // ---------------------------
    // 🗑️ Eliminar tarjeta promoción
    // ---------------------------
    document.querySelectorAll(".btn-delete-promo").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            if (!confirm("¿Seguro que deseas eliminar esta promoción?")) return;

            try {
                const res = await fetch(`/promociones/eliminar/${id}`, { method: "DELETE" });
                const data = await res.json();

                if (data.success) {
                    const card = btn.closest(".promo-card");
                    card.style.transition = "all 0.4s ease";
                    card.style.opacity = "0";
                    card.style.transform = "scale(0.95)";
                    setTimeout(() => card.remove(), 400);
                } else {
                    alert("Error al eliminar la promoción");
                }
            } catch (err) {
                alert("Ocurrió un error en la conexión con el servidor.");
            }
        });
    });

    // ---------------------------
    // 🗓️ Validación de fechas
    // ---------------------------
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]');
    const fechaFin = document.querySelector('input[name="fecha_fin"]');

    if (fechaInicio) {
        const hoy = new Date().toISOString().split('T')[0];
        fechaInicio.setAttribute('min', hoy);

        // Evitar que la fecha de fin sea menor a la de inicio
        fechaInicio.addEventListener("change", () => {
            if (fechaFin) {
                fechaFin.min = fechaInicio.value;
            }
        });
    }

    // ---------------------------
    // 🔔 Inicializar toasts de Bootstrap
    // ---------------------------
    const toastElList = document.querySelectorAll('.toast');
    const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl, { delay: 3000 }));
    toastList.forEach(toast => toast.show());
});
