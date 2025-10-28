from flask import render_template, redirect, url_for, request, flash, session, jsonify
from . import services_bp
from config.db_connection import get_db_connection

#Listar
@services_bp.route('/')
def servicio_inicio():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM servicios")
    datos_servicios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('services/servicios.html', datos_servicios=datos_servicios)

#Agregar
@services_bp.route('/agregar-servicio', methods=['GET', 'POST'])
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
@services_bp.route('/editar-servicio/<int:id_servicio>', methods=["GET", "POST"])
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
@services_bp.route('/eliminar-servicio', methods=["POST"])
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
#==================================================================
#Paquetes
#==================================================================
@services_bp.route('/paquetes')
def listar_paquetes():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Obtener paquetes con sus servicios
    query = """
        SELECT p.*, 
               GROUP_CONCAT(DISTINCT s.nombre SEPARATOR ', ') as servicios_nombres,
               COUNT(DISTINCT s.id_servicio) as total_servicios
        FROM paquetes p
        LEFT JOIN paquete_servicios ps ON p.id_paquete = ps.id_paquete
        LEFT JOIN servicios s ON ps.id_servicio = s.id_servicio
        WHERE p.activo = TRUE
        GROUP BY p.id_paquete
        ORDER BY p.fecha_creacion DESC
    """
    cur.execute(query)
    datos_paquetes = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('services/paquetes.html', datos_paquetes=datos_paquetes)

# Vista para crear paquete (selección de servicios)
@services_bp.route('/crear-paquete')
def crear_paquete():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Obtener todos los servicios activos
    cur.execute("SELECT * FROM servicios WHERE activo = TRUE ORDER BY nombre")
    servicios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('services/crear_paquete.html', servicios=servicios)

# Procesar creación de paquete
@services_bp.route('/procesar-paquete', methods=['POST'])
def procesar_paquete():
    try:
        data = request.json
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        precio = data.get('precio')
        servicios_seleccionados = data.get('servicios', [])
        
        if not nombre or not precio or not servicios_seleccionados:
            return jsonify({"message": "ERROR", "error": "Faltan datos obligatorios"}), 400

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Calcular duración total
        duracion_total = 0
        placeholders = ','.join(['%s'] * len(servicios_seleccionados))
        query_duracion = f"SELECT SUM(duracion) as total FROM servicios WHERE id_servicio IN ({placeholders})"
        cur.execute(query_duracion, servicios_seleccionados)
        resultado = cur.fetchone()
        duracion_total = resultado['total'] or 0

        # Insertar paquete
        query_paquete = """
            INSERT INTO paquetes (nombre, descripcion, precio, duracion_total, activo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query_paquete, (nombre, descripcion, precio, duracion_total, True))
        id_paquete = cur.lastrowid

        # Insertar servicios del paquete
        for id_servicio in servicios_seleccionados:
            query_servicio = """
                INSERT INTO paquete_servicios (id_paquete, id_servicio)
                VALUES (%s, %s)
            """
            cur.execute(query_servicio, (id_paquete, id_servicio))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "OK", "id_paquete": id_paquete}), 200

    except Exception as e:
        print(f"Error al crear paquete: {e}")
        return jsonify({"message": "ERROR", "error": str(e)}), 500

# Ver detalle de paquete
@services_bp.route('/paquete/<int:id_paquete>')
def ver_paquete(id_paquete):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Obtener información del paquete
    query_paquete = "SELECT * FROM paquetes WHERE id_paquete = %s"
    cur.execute(query_paquete, (id_paquete,))
    paquete = cur.fetchone()
    
    if not paquete:
        cur.close()
        conn.close()
        flash(('error', 'Paquete no encontrado'))
        return redirect(url_for('services.listar_paquetes'))
    
    # Obtener servicios del paquete
    query_servicios = """
        SELECT s.* 
        FROM servicios s
        JOIN paquete_servicios ps ON s.id_servicio = ps.id_servicio
        WHERE ps.id_paquete = %s
    """
    cur.execute(query_servicios, (id_paquete,))
    servicios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('services/ver_paquete.html', paquete=paquete, servicios=servicios)

# Editar paquete (vista)
@services_bp.route('/editar-paquete/<int:id_paquete>')
def editar_paquete(id_paquete):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    # Obtener información del paquete
    query_paquete = "SELECT * FROM paquetes WHERE id_paquete = %s"
    cur.execute(query_paquete, (id_paquete,))
    paquete = cur.fetchone()
    
    if not paquete:
        cur.close()
        conn.close()
        flash(('error', 'Paquete no encontrado'))
        return redirect(url_for('services.listar_paquetes'))
    
    # Obtener servicios del paquete (ya seleccionados)
    query_servicios_paquete = """
        SELECT id_servicio 
        FROM paquete_servicios 
        WHERE id_paquete = %s
    """
    cur.execute(query_servicios_paquete, (id_paquete,))
    servicios_seleccionados = [item['id_servicio'] for item in cur.fetchall()]
    
    # Obtener todos los servicios activos
    cur.execute("SELECT * FROM servicios WHERE activo = TRUE ORDER BY nombre")
    servicios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('services/editar_paquete.html', 
                         paquete=paquete, 
                         servicios=servicios,
                         servicios_seleccionados=servicios_seleccionados)

# Procesar edición de paquete
@services_bp.route('/procesar-edicion-paquete', methods=['POST'])
def procesar_edicion_paquete():
    try:
        data = request.json
        id_paquete = data.get('id_paquete')
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        precio = data.get('precio')
        servicios_seleccionados = data.get('servicios', [])
        
        if not id_paquete or not nombre or not precio or not servicios_seleccionados:
            return jsonify({"message": "ERROR", "error": "Faltan datos obligatorios"}), 400

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Calcular duración total
        duracion_total = 0
        placeholders = ','.join(['%s'] * len(servicios_seleccionados))
        query_duracion = f"SELECT SUM(duracion) as total FROM servicios WHERE id_servicio IN ({placeholders})"
        cur.execute(query_duracion, servicios_seleccionados)
        resultado = cur.fetchone()
        duracion_total = resultado['total'] or 0

        # Actualizar paquete
        query_paquete = """
            UPDATE paquetes 
            SET nombre=%s, descripcion=%s, precio=%s, duracion_total=%s
            WHERE id_paquete=%s
        """
        cur.execute(query_paquete, (nombre, descripcion, precio, duracion_total, id_paquete))

        # Eliminar relaciones existentes y crear nuevas
        cur.execute("DELETE FROM paquete_servicios WHERE id_paquete = %s", (id_paquete,))

        # Insertar nuevos servicios
        for id_servicio in servicios_seleccionados:
            query_servicio = """
                INSERT INTO paquete_servicios (id_paquete, id_servicio)
                VALUES (%s, %s)
            """
            cur.execute(query_servicio, (id_paquete, id_servicio))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "OK"}), 200

    except Exception as e:
        print(f"Error al editar paquete: {e}")
        return jsonify({"message": "ERROR", "error": str(e)}), 500

# Eliminar paquete
@services_bp.route('/eliminar-paquete', methods=['POST'])
def eliminar_paquete():
    try:
        data = request.json
        id_paquete = data.get('id_paquete')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Eliminación lógica
        query = "UPDATE paquetes SET activo = FALSE WHERE id_paquete = %s"
        cur.execute(query, (id_paquete,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "OK"}), 200
        
    except Exception as e:
        print(f"Error al eliminar paquete: {e}")
        return jsonify({"message": "ERROR"}), 500