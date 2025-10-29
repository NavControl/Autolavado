// =========================================================
// Script: seleccionar_pago.js
// Gestión de la selección y confirmación del método de pago
// =========================================================

document.addEventListener('DOMContentLoaded', () => {
  const btnEfectivo = document.getElementById('btn-efectivo');
  const btnPaypal = document.getElementById('btn-paypal');
  const modalElement = document.getElementById('modalConfirmacion');
  const textoConfirmacion = document.getElementById('texto-confirmacion');
  const modalServicio = document.getElementById('modal-servicio');
  const modalTotal = document.getElementById('modal-total');
  const btnConfirmarModal = document.getElementById('btn-confirmar-modal');

  // Verifica que exista el modal antes de instanciarlo
  const modal = modalElement ? new bootstrap.Modal(modalElement) : null;

  let metodoSeleccionado = null;
  let formSeleccionado = null;

  // =========================================================
  // Asignar eventos a los botones de pago
  // =========================================================
  [btnEfectivo, btnPaypal].forEach((btn) => {
    if (!btn) return;

    btn.addEventListener('click', (e) => {
      e.preventDefault();

      // Obtener datos de la cita desde la interfaz
      const servicio = document.querySelector('.detalle-cita p:nth-child(2)')?.textContent?.replace('Servicio:', '').trim() || 'Servicio';
      const monto = document.querySelector('.detalle-cita span.text-success')?.textContent?.replace('$', '').trim() || '0.00';

      metodoSeleccionado = btn.id === 'btn-efectivo' ? 'Efectivo' : 'PayPal';
      formSeleccionado = btn.closest('form');

      if (modal) {
        textoConfirmacion.textContent = `¿Deseas confirmar el pago mediante ${metodoSeleccionado}?`;
        modalServicio.textContent = servicio;
        modalTotal.textContent = `$${monto}`;
        modal.show();
      } else {
        // Si no hay modal, enviar directamente
        formSeleccionado.submit();
      }
    });
  });

  // =========================================================
  // Confirmar método desde el modal (flujo tradicional)
  // =========================================================
  if (btnConfirmarModal) {
    btnConfirmarModal.addEventListener('click', () => {
      if (!formSeleccionado) return;

      modal?.hide();

      // Crear overlay visual
      const overlay = document.createElement('div');
      overlay.id = 'pago-overlay';
      overlay.innerHTML = `
        <div class="overlay-content">
          <div class="spinner-border text-primary" role="status"></div>
          <p class="mt-3 fw-semibold text-dark">Procesando tu pago...</p>
        </div>
      `;
      document.body.appendChild(overlay);

      // Aplicar estilos visuales
      Object.assign(overlay.style, {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: '9999'
      });

      // Envío tradicional (redirige al backend)
      formSeleccionado.submit();
    });
  }
});
