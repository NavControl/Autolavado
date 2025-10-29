// =========================================================
// Script para confirmar la cita del cliente
// =========================================================

document.addEventListener('DOMContentLoaded', () => {
    const btnConfirmar = document.getElementById('btn-confirmar');

    if (!btnConfirmar) {
        setTimeout(() => {
            const retryBtn = document.getElementById('btn-confirmar');
            if (retryBtn) inicializarConfirmarCita(retryBtn);
        }, 500);
        return;
    }

    inicializarConfirmarCita(btnConfirmar);
});

function inicializarConfirmarCita(btnConfirmar) {

    async function cargarDatosCita() {
        try {
            const serviciosSeleccionados = JSON.parse(document.getElementById('data-servicios').textContent);
            const fechaSeleccionada = JSON.parse(document.getElementById('data-fecha').textContent);
            const horaSeleccionada = JSON.parse(document.getElementById('data-hora').textContent);
            const vehiculoInfo = JSON.parse(document.getElementById('data-vehiculo').textContent);

            if (serviciosSeleccionados.length > 0 && fechaSeleccionada && horaSeleccionada && vehiculoInfo.marca) {
                mostrarDatosCita({
                    servicios: serviciosSeleccionados,
                    fecha: fechaSeleccionada,
                    hora: horaSeleccionada,
                    vehiculo: vehiculoInfo
                });
            } else {
                const response = await fetch('/client/api/datos-cita');
                const data = await response.json();
                if (data.servicios && data.servicios.length > 0) {
                    mostrarDatosCita(data);
                } else {
                    alert('No se encontraron datos de la cita. Por favor, comienza de nuevo.');
                    window.location.href = '/client/nueva-cita';
                }
            }
        } catch (error) {
            console.error('Error al cargar datos de la cita:', error);
            alert('Error al cargar los datos de la cita.');
        }
    }

    function mostrarDatosCita(data) {
        document.getElementById('confirmar-fecha').textContent = data.fecha;
        document.getElementById('confirmar-hora').textContent = data.hora;

        const vehiculo = data.vehiculo;
        const vehiculoText = `${vehiculo.marca} ${vehiculo.modelo} - ${vehiculo.placas}${vehiculo.color ? ' (' + vehiculo.color + ')' : ''}`;
        document.getElementById('confirmar-vehiculo').textContent = vehiculoText;

        const serviciosList = document.getElementById('confirmar-servicios');
        let total = 0;
        let duracionTotal = 0;
        serviciosList.innerHTML = '';

        data.servicios.forEach(servicio => {
            const li = document.createElement('li');
            li.className = 'd-flex justify-content-between mb-2';
            li.innerHTML = `
                <span class="text-dark">${servicio.nombre}</span>
                <span class="text-dark">$${servicio.precio}</span>
            `;
            serviciosList.appendChild(li);
            total += parseFloat(servicio.precio);
            duracionTotal += parseInt(servicio.duracion);
        });

        document.getElementById('confirmar-total').textContent = total.toFixed(2);
        document.getElementById('confirmar-duracion').textContent = duracionTotal;
    }

    // =========================================================
    // Confirmar cita y redirigir a la vista de pago
    // =========================================================
    btnConfirmar.addEventListener('click', async () => {
        if (!confirm('¿Estás seguro de confirmar esta cita?')) return;

        btnConfirmar.disabled = true;
        btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';

        try {
            const response = await fetch('/client/procesar-cita', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success && data.redirect_url) {
                // ✅ Redirige exactamente al URL que devuelve Flask
                window.location.href = data.redirect_url;
            } else {
                alert('Error al confirmar la cita: ' + (data.message || 'Ocurrió un problema.'));
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '<i class="fas fa-calendar-check me-2"></i>Confirmar Cita';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al confirmar la cita.');
            btnConfirmar.disabled = false;
            btnConfirmar.innerHTML = '<i class="fas fa-calendar-check me-2"></i>Confirmar Cita';
        }
    });

    cargarDatosCita();
}
