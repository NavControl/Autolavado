from flask import render_template, redirect, url_for, request, flash, session, jsonify
from . import servicio_bp
from config.db_connection import get_db_connection

#Listar
@servicio_bp.route('/')
def servicio_inicio():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM servicios")
    datos_servicios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('services/servicios.html', datos_servicios=datos_servicios)

#Agregar
@servicio_bp.route('/agregar-servicio', methods=['GET', 'POST'])
def agregar_servicio():
    if request.method == 'POST':
        nombre = request.form.get('inpNombre')
        descripcion = request.form.get('inpDescripcion')
        precio = request.form.get('inpPrecio')
        duracion = request.form.get('inpDuracion')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query = """
            INSERT INTO servicios (nombre, descripcion, precio, duracion, activo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (nombre, descripcion, precio, duracion, True))
        conn.commit()
        cur.close()
        conn.close()

        flash(('success', 'Servicio agregado correctamente'))
        return redirect(url_for('services.servicio_inicio'))  # Cambiado a 'services'

    return render_template('services/agregar_servicio.html')

#Editar 
@servicio_bp.route('/editar-servicio/<int:id_servicio>', methods=["GET", "POST"])
def editar_servicio(id_servicio):
    print(f"Ruta de editar servicio accedida - ID: {id_servicio}")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        nombre = request.form.get('inpNombre')
        descripcion = request.form.get('inpDescripcion')
        precio = request.form.get('inpPrecio')
        duracion = request.form.get('inpDuracion')

        query = """
            UPDATE servicios 
            SET nombre=%s, descripcion=%s, precio=%s, duracion=%s
            WHERE id_servicio=%s
        """
        cur.execute(query, (nombre, descripcion, precio, duracion, id_servicio))
        conn.commit()
        cur.close()
        conn.close()

        flash(('success', 'Servicio actualizado correctamente'))
        return redirect(url_for('services.servicio_inicio'))  # Cambiado a 'services'

    # Si es GET → mostrar datos actuales
    query = "SELECT * FROM servicios WHERE id_servicio = %s"
    cur.execute(query, (id_servicio,))
    servicio = cur.fetchone()

    cur.close()
    conn.close()

    if not servicio:
        flash(('error', 'Servicio no encontrado'))
        return redirect(url_for('services.servicio_inicio'))  # Cambiado a 'services'

    return render_template("services/editar_servicio.html", servicio=servicio) 

# Eliminar 
@servicio_bp.route('/eliminar-servicio', methods=["POST"])
def eliminar_servicio():
    try:
        data = request.json
        id_servicio = data.get('id_servicio')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query = "DELETE FROM servicios WHERE id_servicio = %s"
        cur.execute(query, (id_servicio,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "OK"}), 200
    except Exception as e:
        print(f"Error al eliminar servicio: {e}")
        return jsonify({"message": "ERROR"}), 500