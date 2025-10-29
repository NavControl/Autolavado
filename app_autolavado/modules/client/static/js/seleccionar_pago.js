// =========================================================
// Script: seleccionar_pago.js
// Gestión de la selección y confirmación del método de pago
// =========================================================

document.addEventListener('DOMContentLoaded', () => {
  const btnEfectivo = document.getElementById('btn-efectivo');
  const btnPaypal = document.getElementById('btn-paypal');
  const modal = new bootstrap.Modal(document.getElementById('modalConfirmacion'));
  const textoConfirmacion = document.getElementById('texto-confirmacion');
  const modalServicio = document.getElementById('modal-servicio');
  const modalTotal = document.getElementById('modal-total');
  const btnConfirmarModal = document.getElementById('btn-confirmar-modal');

  let metodoSeleccionado = null;
  let formSeleccionado = null;

  // =========================================================
  // Manejo de botones de pago
  // =========================================================
  [btnEfectivo, btnPaypal].forEach((btn) => {
    if (!btn) return;

    btn.addEventListener('click', (e) => {
      e.preventDefault();

      const servicio = btn.dataset.servicio || 'Servicio';
      const monto = btn.dataset.monto || '0.00';
      metodoSeleccionado = btn.id === 'btn-efectivo' ? 'Efectivo' : 'PayPal';
      formSeleccionado = btn.closest('form');

      // Llenar los datos del modal
      textoConfirmacion.textContent = `¿Deseas confirmar el pago mediante ${metodoSeleccionado}?`;
      modalServicio.textContent = servicio;
      modalTotal.textContent = `$${monto}`;

      modal.show();
    });
  });

  // =========================================================
  // Confirmar método en el modal
  // =========================================================
  btnConfirmarModal.addEventListener('click', async () => {
    if (!formSeleccionado) return;

    modal.hide();
    const btn = formSeleccionado.querySelector('button');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';

    try {
      const response = await fetch(formSeleccionado.action, {
        method: formSeleccionado.method,
        body: new FormData(formSeleccionado)
      });

      if (!response.ok) throw new Error('Error HTTP al procesar el pago');

      const html = await response.text();

      // Si el backend redirige, actualizamos la vista
      if (response.redirected) {
        window.location.href = response.url;
      } else {
        // Mostrar mensaje de éxito o actualizar dinámicamente
        document.body.innerHTML = html;
      }
    } catch (error) {
      console.error('Error al procesar el pago:', error);
      alert('Error al procesar el pago. Intenta de nuevo.');
    } finally {
      btn.disabled = false;
      btn.innerHTML = metodoSeleccionado === 'Efectivo'
        ? '<i class="fas fa-money-bill-wave me-2"></i>Pagar en efectivo'
        : '<i class="fab fa-paypal me-2"></i>Pagar con PayPal';
    }
  });
});
