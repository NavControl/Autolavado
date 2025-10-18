$(function () {
    const btn = document.getElementById('openSidebar');
    const sidebar = document.getElementById('sidebar');

    if (btn && sidebar) {
        btn.addEventListener('click', () => {
            const isOpen = sidebar.classList.toggle('open');
            btn.setAttribute('aria-expanded', String(isOpen));
        });

        // Cerrar sidebar al hacer clic fuera en móviles
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 768 && sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) && e.target !== btn) {
                sidebar.classList.remove('open');
                btn.setAttribute('aria-expanded', 'false');
            }
        });
    }
});

/* ===========================================================
   🗑️ Eliminar Usuario
   =========================================================== */
async function eliminar_usuario(id_usuario) {
    const confirmar = confirm("¿Desea eliminar el usuario seleccionado?");
    if (!confirmar) return;

    try {
        const res = await fetch('/admin/eliminar-usuario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_usuario })
        });

        const data = await res.json();

        if (data.message === "OK") {
            alert("✅ Usuario eliminado correctamente");
            location.reload();
        } else {
            alert("❌ Error al eliminar usuario");
        }
    } catch (err) {
        alert("⚠️ Error de conexión al intentar eliminar usuario");
        console.error(err);
    }
}

/* ===========================================================
   🔍 Filtro de búsqueda
   =========================================================== */
function filtrarUsuarios() {
    const input = document.getElementById("buscadorUsuarios").value.toLowerCase();
    const filas = document.querySelectorAll("#tablaUsuarios tbody tr");

    filas.forEach(fila => {
        fila.style.display = fila.textContent.toLowerCase().includes(input) ? "" : "none";
    });
}

/* ===========================================================
   👁️ Mostrar Detalles de Usuario
   =========================================================== */
function mostrarDetalles(idUsuario) {
    fetch(`/admin/detalle-usuario/${idUsuario}`)
        .then(res => res.json())
        .then(data => {
            const panel = document.getElementById("detalleUsuario");
            const cont = document.getElementById("contenidoDetalle");

            if (!data || data.message) {
                cont.innerHTML = `<p class="text-danger">No se encontraron detalles para este usuario.</p>`;
                return;
            }

            const estadoColor = data.estado === "activo"
                ? "bg-success"
                : data.estado === "bloqueado"
                    ? "bg-danger"
                    : "bg-secondary";

            cont.innerHTML = `
                <div class="detalle-info">
                    <p><strong>Usuario:</strong> ${data.username}</p>
                    <p><strong>Nombre completo:</strong> ${data.nombre_completo}</p>
                    <p><strong>Correo:</strong> ${data.correo}</p>
                    <p><strong>Teléfono:</strong> ${data.telefono || 'No registrado'}</p>
                    <p><strong>Rol:</strong> ${data.rol}</p>
                    <p><strong>Turno:</strong> ${data.turno || '-'}</p>
                    <p><strong>Fecha de contratación:</strong> ${data.fecha_contratacion || 'No registrada'}</p>
                    <p><strong>Salario:</strong> $${data.salario || 'No asignado'}</p>
                    <p><strong>Estado:</strong> <span class="badge ${estadoColor} text-white">${data.estado}</span></p>
                </div>

                <div class="acciones-detalle">
                    <a href="/admin/editar-usuario/${data.id_usuario}" class="btn-modern btn-modern-primary">
                        <i class="fa fa-edit"></i> Editar
                    </a>
                    <button class="btn-modern btn-modern-danger" onclick="eliminar_usuario(${data.id_usuario})">
                        <i class="fa fa-trash"></i> Eliminar
                    </button>
                    <button class="btn-modern btn-modern-outline" onclick="cerrarDetalles()">
                        <i class="fa fa-times"></i> Cerrar
                    </button>
                </div>
            `;

            panel.classList.remove("hidden");
            panel.scrollIntoView({ behavior: "smooth" });
        })
        .catch(err => {
            console.error(err);
            alert("Error al cargar los detalles del usuario");
        });
}

/* ===========================================================
   ❌ Cerrar Panel de Detalles
   =========================================================== */
function cerrarDetalles() {
    document.getElementById("detalleUsuario").classList.add("hidden");
}
