async function eliminar_servicio(id_servicio) {
    const resultado = await mostrarConfirmacion(`¿Desea eliminar el servicio seleccionado?`);
    if (resultado) {
        fetch('/services/eliminar-servicio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_servicio: id_servicio
            })
        }).then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error');
            }
        }).then(data => {
            if (data.message == "OK") {
                alert("Se eliminó el servicio");
                window.location = "/services";
            } else {
                alert("No se eliminó el servicio");
            }
        }).catch(error => {
            alert("No se eliminó el servicio");
        });
    }
}