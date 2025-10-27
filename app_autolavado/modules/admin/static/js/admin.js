$(function () {
    const btn = document.getElementById('openSidebar');
    const sidebar = document.getElementById('sidebar');

    if (btn && sidebar) {
        btn.addEventListener('click', () => {
            const isOpen = sidebar.classList.toggle('open');
            btn.setAttribute('aria-expanded', String(isOpen));
        });

        // Cerrar sidebar al hacer clic fuera en dispositivos móviles
        document.addEventListener('click', (e) => {
            if (window.innerWidth < 768 && sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) && e.target !== btn) {
                sidebar.classList.remove('open');
                btn.setAttribute('aria-expanded', 'false');
            }
        });
    }

});

async function eliminar_usuario(id_usuario) {
    const resultado = await mostrarConfirmacion(`¿Desea eliminar el usuario seleccionado?`);
    if (resultado) {
        fetch('/admin/eliminar-usuario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_usuario: id_usuario
            })
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error');
            }
        }).then(data => {
            if (data.message == "OK") {
                alert("Se eliminó");
                window.location = "/admin/usuarios";
            } else {
                alert("No se eliminó");
            }
        }).catch(error => {
            alert("No se eliminó");
        });
    }
}