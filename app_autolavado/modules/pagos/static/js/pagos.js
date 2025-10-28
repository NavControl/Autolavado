// Archivo: pagos.js
// Funciones: eliminar, autocompletar usuario, cargar servicios/paquetes y asignar monto.

document.addEventListener("DOMContentLoaded", () => {

  // Modal de eliminación de pago
  const modalEliminar = document.getElementById("modalEliminar");
  if (modalEliminar) {
    modalEliminar.addEventListener("show.bs.modal", (event) => {
      const button = event.relatedTarget;
      const idPago = button?.getAttribute("data-id");
      if (!idPago) return;
      const form = document.getElementById("formEliminar");
      if (form) form.action = `/pagos/eliminar/${idPago}`;
    });
  }

  // Autocompletado de usuarios
  const inputUsuario = document.getElementById("buscar_usuario");
  const sugerencias = document.getElementById("sugerencias_usuarios");
  const idUsuario = document.getElementById("id_usuario");

  if (inputUsuario && sugerencias) {
    inputUsuario.addEventListener("input", async () => {
      const q = inputUsuario.value.trim();
      sugerencias.innerHTML = "";
      if (q.length < 2) return;

      try {
        const res = await fetch(`/pagos/api/usuarios?q=${encodeURIComponent(q)}`);
        const data = await res.json();

        if (!data.length) {
          sugerencias.innerHTML = '<div class="list-group-item text-muted">Sin resultados</div>';
          return;
        }

        data.forEach(u => {
          const item = document.createElement("button");
          item.type = "button";
          item.className = "list-group-item list-group-item-action";
          item.textContent = u.nombre_completo;
          item.onclick = () => {
            inputUsuario.value = u.nombre_completo;
            idUsuario.value = u.id_usuario;
            sugerencias.innerHTML = "";
          };
          sugerencias.appendChild(item);
        });
      } catch (error) {
        console.error("Error al cargar usuarios:", error);
      }
    });

    // Cerrar sugerencias al hacer clic fuera
    document.addEventListener("click", (e) => {
      if (!sugerencias.contains(e.target) && e.target !== inputUsuario) {
        sugerencias.innerHTML = "";
      }
    });
  }

  // Cargar servicios o paquetes
  const tipoRadios = document.querySelectorAll("input[name='tipo']");
  const selectItem = document.getElementById("select_item");
  const idItem = document.getElementById("id_item");
  const montoInput = document.getElementById("monto");

  async function cargarItems(tipo) {
    if (!selectItem) return;
    selectItem.innerHTML = '<option value="">Cargando...</option>';
    try {
      const url = tipo === "paquete" ? "/pagos/api/paquetes" : "/pagos/api/servicios";
      const res = await fetch(url);
      const data = await res.json();

      selectItem.innerHTML = '<option value="">Seleccione una opción...</option>';

      data.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = `${item.nombre} - $${parseFloat(item.precio).toFixed(2)}`;
        option.dataset.precio = item.precio;
        selectItem.appendChild(option);
      });
    } catch (error) {
      console.error("Error al cargar ítems:", error);
      selectItem.innerHTML = '<option value="">Error al cargar datos</option>';
    }
  }

  tipoRadios.forEach(radio => {
    radio.addEventListener("change", () => {
      cargarItems(radio.value);
      montoInput.value = "";
      idItem.value = "";
    });
  });

  if (selectItem) {
    selectItem.addEventListener("change", () => {
      const option = selectItem.options[selectItem.selectedIndex];
      if (option && option.dataset.precio) {
        montoInput.value = parseFloat(option.dataset.precio).toFixed(2);
        idItem.value = option.value;
      } else {
        montoInput.value = "";
        idItem.value = "";
      }
    });
  }

  const tipoInicial = document.querySelector("input[name='tipo']:checked");
  if (tipoInicial) cargarItems(tipoInicial.value);

  // Validar antes de enviar el formulario
  const formPago = document.getElementById("formPago");
  if (formPago) {
    formPago.addEventListener("submit", (e) => {
      if (!idUsuario.value || !idItem.value) {
        e.preventDefault();
        alert("Debe seleccionar un usuario y un servicio o paquete antes de registrar el pago.");
      }
    });
  }

});
