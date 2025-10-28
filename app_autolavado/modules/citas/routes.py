from flask import render_template, redirect, url_for, request, flash, session, jsonify
from . import citas_bp
from config.db_connection import get_db_connection
from datetime import datetime, timedelta
import json
# ==============================================
# RUTA TEMPORAL PARA PRUEBAS - ELIMINAR EN PRODUCCIÓN
# ==============================================

@citas_bp.route('/test/notificacion/<int:id_cita>')
def test_notificacion(id_cita):
    """Ruta temporal para probar notificaciones sin autenticación"""
    print(f"🔧 TEST: Solicitando notificación para cita #{id_cita}")
    
    success = enviar_notificacion_cita(id_cita, "confirmacion")
    
    return jsonify({
        "success": success, 
        "message": "Notificación de prueba enviada",
        "cita_id": id_cita,
        "nota": "Esta ruta es solo para testing - Eliminar en producción"
    })

# ==============================================
# SISTEMA DE NOTIFICACIONES BÁSICO (VERSIÓN SIMPLIFICADA)
# ==============================================

def enviar_notificacion_cita(cita_id, tipo="confirmacion"):
    """Enviar notificación por email (versión simplificada sin dependencias)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT c.*, u.nombre_completo, u.correo, v.marca, v.modelo, v.placas
            FROM citas c
            JOIN clientes cl ON c.id_cliente = cl.id_cliente
            JOIN usuarios u ON cl.id_usuario = u.id_usuario
            JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
            WHERE c.id_cita = %s
        """, (cita_id,))
        
        cita = cur.fetchone()
        
        if not cita or not cita['correo']:
            return False
        
        # Configuración de mensajes
        if tipo == "confirmacion":
            asunto = f"Confirmación de Cita #{cita_id} - Autolavado"
            mensaje = f"""
            Hola {cita['nombre_completo']},
            
            Tu cita ha sido confirmada:
            
            📅 Fecha: {cita['fecha']}
            ⏰ Hora: {cita['hora']}
            🚗 Vehículo: {cita['marca']} {cita['modelo']} - {cita['placas']}
            💰 Total: ${cita['total']}
            
            Por favor llega 10 minutos antes.
            
            Gracias,
            Equipo Autolavado
            """
        elif tipo == "recordatorio":
            asunto = f"Recordatorio de Cita #{cita_id} - Autolavado"
            mensaje = f"""
            Recordatorio: Tienes una cita mañana:
            
            📅 Fecha: {cita['fecha']}
            ⏰ Hora: {cita['hora']}
            🚗 Vehículo: {cita['marca']} {cita['modelo']}
            
            ¡Te esperamos!
            """
        
        # Por ahora solo lo registramos en consola
        # En producción, aquí integrarías con un servicio de email
        print("=" * 50)
        print(f"📧 NOTIFICACIÓN {tipo.upper()} - CITA #{cita_id}")
        print("=" * 50)
        print(f"Para: {cita['nombre_completo']} <{cita['correo']}>")
        print(f"Asunto: {asunto}")
        print(f"Mensaje: {mensaje}")
        print("=" * 50)
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        return False

@citas_bp.route('/admin/enviar-notificacion/<int:id_cita>')
def enviar_notificacion_manual(id_cita):
    """Endpoint para enviar notificación manual"""
    # Verificación básica de admin (puedes mejorar esto)
    if not session.get('user_id'):
        return "No autorizado", 403
    
    success = enviar_notificacion_cita(id_cita, "confirmacion")
    return jsonify({"success": success, "message": "Notificación enviada"})

# ==============================================
# RUTAS PÚBLICAS (PARA CLIENTES)
# ==============================================

@citas_bp.route('/nueva-cita')
def nueva_cita_cliente():
    """Página inicial para crear una nueva cita"""
    return render_template('citas/nueva_cita.html')

@citas_bp.route('/seleccionar-servicios')
def seleccionar_servicios():
    """Página para seleccionar servicios y paquetes"""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM servicios WHERE activo = TRUE ORDER BY nombre")
    servicios = cur.fetchall()
    
    cur.execute("""
        SELECT p.*, 
               GROUP_CONCAT(s.nombre SEPARATOR ', ') as servicios_incluidos
        FROM paquetes p
        LEFT JOIN paquete_servicios ps ON p.id_paquete = ps.id_paquete
        LEFT JOIN servicios s ON ps.id_servicio = s.id_servicio
        WHERE p.activo = TRUE
        GROUP BY p.id_paquete
        ORDER BY p.nombre
    """)
    paquetes = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('citas/seleccionar_servicios.html', 
                         servicios=servicios, 
                         paquetes=paquetes)

@citas_bp.route('/seleccionar-fecha')
def seleccionar_fecha_cliente():
    """Página para seleccionar fecha y hora"""
    return render_template('citas/seleccionar_fecha.html')

@citas_bp.route('/informacion-vehiculo')
def informacion_vehiculo_cliente():
    """Página para ingresar información del vehículo"""
    return render_template('citas/informacion_vehiculo.html')

@citas_bp.route('/confirmar-cita')
def confirmar_cita_cliente():
    """Página para confirmar la cita"""
    # Recuperar datos de la sesión
    servicios_seleccionados = session.get('servicios_seleccionados', [])
    fecha_seleccionada = session.get('fecha_seleccionada')
    hora_seleccionada = session.get('hora_seleccionada')
    vehiculo_info = session.get('vehiculo_info', {})
    
    # Calcular total
    total = sum(servicio['precio'] for servicio in servicios_seleccionados)
    
    return render_template('citas/confirmar_cita.html',
                         servicios=servicios_seleccionados,
                         fecha=fecha_seleccionada,
                         hora=hora_seleccionada,
                         vehiculo=vehiculo_info,
                         total=total)

@citas_bp.route('/guardar-servicios', methods=['POST'])
def guardar_servicios():
    """Guardar servicios seleccionados en sesión"""
    try:
        data = request.json
        session['servicios_seleccionados'] = data.get('servicios', [])
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/guardar-fecha', methods=['POST'])
def guardar_fecha():
    """Guardar fecha y hora seleccionadas en sesión"""
    try:
        data = request.json
        session['fecha_seleccionada'] = data.get('fecha')
        session['hora_seleccionada'] = data.get('hora')
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/guardar-vehiculo', methods=['POST'])
def guardar_vehiculo():
    """Guardar información del vehículo en sesión"""
    try:
        data = request.json
        session['vehiculo_info'] = data
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/procesar-cita', methods=['POST'])
def procesar_cita_cliente():
    """Procesar la creación de la cita"""
    try:
        # Recuperar datos de la sesión
        servicios_seleccionados = session.get('servicios_seleccionados', [])
        fecha = session.get('fecha_seleccionada')
        hora = session.get('hora_seleccionada')
        vehiculo_info = session.get('vehiculo_info', {})
        
        
        if not all([servicios_seleccionados, fecha, hora, vehiculo_info]):
            return jsonify({"message": "ERROR", "error": "Faltan datos de la cita"}), 400
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Calcular total y duración
        total = sum(servicio['precio'] for servicio in servicios_seleccionados)
        duracion_total = sum(servicio['duracion'] for servicio in servicios_seleccionados)
        
        # 1. Crear o obtener cliente (usando el usuario de sesión o creando uno temporal)
        id_usuario = session.get('user_id', 3)  # Usar 3 como cliente temporal si no hay sesión
        cur.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (id_usuario,))
        cliente = cur.fetchone()
        
        if not cliente:
            # Crear cliente temporal
            cur.execute("""
                INSERT INTO clientes (folio, id_usuario) 
                VALUES (%s, %s)
            """, (f"TEMP_{datetime.now().strftime('%Y%m%d%H%M%S')}", id_usuario))
            id_cliente = cur.lastrowid
        else:
            id_cliente = cliente['id_cliente']
        
        # 2. Crear vehículo
        cur.execute("""
            INSERT INTO vehiculos (marca, modelo, placas, color, anio, id_cliente)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            vehiculo_info.get('marca'),
            vehiculo_info.get('modelo'),
            vehiculo_info.get('placas'),
            vehiculo_info.get('color'),
            vehiculo_info.get('anio'),
            id_cliente
        ))
        id_vehiculo = cur.lastrowid
        
        # 3. Crear cita
        cur.execute("""
            INSERT INTO citas (id_cliente, id_vehiculo, fecha, hora, duracion_total, total, estado)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')
        """, (id_cliente, id_vehiculo, fecha, hora, duracion_total, total))
        id_cita = cur.lastrowid
        
        # 4. Agregar servicios a la cita
        for servicio in servicios_seleccionados:
            cur.execute("""
                INSERT INTO cita_servicios (id_cita, id_servicio, tipo, precio, duracion)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_cita,
                servicio['id'],
                servicio['tipo'],
                servicio['precio'],
                servicio['duracion']
            ))
        
        conn.commit()
        # 5. Enviar notificación de confirmación
        if id_cita:
            enviar_notificacion_cita(id_cita, "confirmacion")

        cur.close()
        conn.close()
        
        # Limpiar sesión
        session.pop('servicios_seleccionados', None)
        session.pop('fecha_seleccionada', None)
        session.pop('hora_seleccionada', None)
        session.pop('vehiculo_info', None)
        
        return jsonify({"message": "OK", "id_cita": id_cita}), 200
        
    except Exception as e:
        print(f"Error al procesar cita: {e}")
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/confirmacion/<int:id_cita>')
def confirmacion_cita_cliente(id_cita):
    """Página de confirmación exitosa"""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("""
        SELECT c.*, u.nombre_completo, v.marca, v.modelo, v.placas
        FROM citas c
        JOIN clientes cl ON c.id_cliente = cl.id_cliente
        JOIN usuarios u ON cl.id_usuario = u.id_usuario
        JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
        WHERE c.id_cita = %s
    """, (id_cita,))
    cita = cur.fetchone()
    
    cur.execute("""
        SELECT cs.*, s.nombre 
        FROM cita_servicios cs
        LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
        WHERE cs.id_cita = %s
    """, (id_cita,))
    servicios = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('citas/confirmacion.html', cita=cita, servicios=servicios)

# ==============================================
# RUTAS DE ADMINISTRACIÓN
# ==============================================

@citas_bp.route('/admin/citas')
def admin_citas():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            c.id_cita,
            c.fecha,
            c.hora,
            u.nombre_completo as nombre_cliente,
            u.telefono,
            v.marca,
            v.modelo,
            v.placas,
            c.total,
            c.estado,
            GROUP_CONCAT(DISTINCT s.nombre SEPARATOR ', ') as servicios
        FROM citas c
        JOIN clientes cl ON c.id_cliente = cl.id_cliente
        JOIN usuarios u ON cl.id_usuario = u.id_usuario
        JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
        LEFT JOIN cita_servicios cs ON c.id_cita = cs.id_cita
        LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
        GROUP BY c.id_cita
        ORDER BY c.fecha DESC, c.hora DESC
        """
        
        cur.execute(query)
        citas = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('citas/admin_citas.html', citas=citas)
        
    except Exception as e:
        print(f"Error: {e}")
        return f"Error al cargar las citas: {str(e)}", 500

@citas_bp.route('/admin/estadisticas')
def estadisticas_citas():
    """API para obtener estadísticas de citas"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Total de citas por estado
        cur.execute("""
            SELECT estado, COUNT(*) as total 
            FROM citas 
            GROUP BY estado
        """)
        stats_estado = cur.fetchall()
        
        # Citas de hoy
        cur.execute("""
            SELECT COUNT(*) as total 
            FROM citas 
            WHERE fecha = CURDATE()
        """)
        citas_hoy = cur.fetchone()
        
        # Ingresos del mes
        cur.execute("""
            SELECT COALESCE(SUM(total), 0) as ingresos 
            FROM citas 
            WHERE MONTH(fecha) = MONTH(CURDATE()) 
            AND YEAR(fecha) = YEAR(CURDATE())
            AND estado = 'completada'
        """)
        ingresos_mes = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'estados': stats_estado,
            'citas_hoy': citas_hoy['total'],
            'ingresos_mes': float(ingresos_mes['ingresos'])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@citas_bp.route('/admin/editar/<int:id_cita>')
def editar_cita_admin(id_cita):
    """Editar una cita existente"""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("""
        SELECT c.*, u.nombre_completo as nombre_cliente, v.*
        FROM citas c
        JOIN clientes cl ON c.id_cliente = cl.id_cliente
        JOIN usuarios u ON cl.id_usuario = u.id_usuario
        JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
        WHERE c.id_cita = %s
    """, (id_cita,))
    cita = cur.fetchone()
    
    cur.execute("""
        SELECT cs.*, s.nombre 
        FROM cita_servicios cs
        LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
        WHERE cs.id_cita = %s
    """, (id_cita,))
    servicios_cita = cur.fetchall()
    
    # Obtener servicios y paquetes disponibles
    cur.execute("SELECT * FROM servicios WHERE activo = TRUE ORDER BY nombre")
    servicios = cur.fetchall()
    
    cur.execute("SELECT * FROM paquetes WHERE activo = TRUE ORDER BY nombre")
    paquetes = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('citas/editar_cita.html', 
                         cita=cita, 
                         servicios_cita=servicios_cita,
                         servicios=servicios,
                         paquetes=paquetes)

@citas_bp.route('/admin/actualizar-estado', methods=['POST'])
def actualizar_estado_cita():
    """Actualizar el estado de una cita"""
    try:
        data = request.json
        id_cita = data.get('id_cita')
        nuevo_estado = data.get('estado')
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        query = "UPDATE citas SET estado = %s WHERE id_cita = %s"
        cur.execute(query, (nuevo_estado, id_cita))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/admin/eliminar-cita/<int:id_cita>', methods=['DELETE'])
def eliminar_cita_admin(id_cita):
    """Eliminar una cita"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "DELETE FROM citas WHERE id_cita = %s"
        cur.execute(query, (id_cita,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "Cita eliminada correctamente"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

# ==============================================
# APIs - NOMBRES ÚNICOS
# ==============================================

@citas_bp.route('/api/servicios-disponibles')
def api_obtener_servicios():
    """API para obtener servicios y paquetes disponibles"""
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("""
        SELECT id_servicio as id, nombre, descripcion, precio, duracion, 'servicio' as tipo
        FROM servicios 
        WHERE activo = TRUE
        ORDER BY nombre
    """)
    servicios = cur.fetchall()
    
    cur.execute("""
        SELECT p.id_paquete as id, p.nombre, p.descripcion, p.precio, p.duracion_total as duracion, 'paquete' as tipo
        FROM paquetes p
        WHERE p.activo = TRUE
        ORDER BY p.nombre
    """)
    paquetes = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify({
        'servicios': servicios,
        'paquetes': paquetes
    })

@citas_bp.route('/api/horarios-disponibles')
def api_obtener_horarios():
    """API para obtener horarios disponibles"""
    fecha = request.args.get('fecha')
    
    if not fecha:
        return jsonify({'error': 'Fecha requerida'}), 400
    
    try:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    dia_semana = fecha_obj.strftime('%A').lower()
    # Ajustar nombres en español
    dias_map = {
        'monday': 'lunes',
        'tuesday': 'martes', 
        'wednesday': 'miercoles',
        'thursday': 'jueves',
        'friday': 'viernes',
        'saturday': 'sabado',
        'sunday': 'domingo'
    }
    dia_semana = dias_map.get(dia_semana, dia_semana)
    
    cur.execute("""
        SELECT hora_apertura, hora_cierre 
        FROM horarios_disponibles 
        WHERE dia_semana = %s AND disponible = TRUE
    """, (dia_semana,))
    
    horario = cur.fetchone()
    
    if not horario:
        cur.close()
        conn.close()
        return jsonify({'disponible': False, 'mensaje': 'No hay horarios disponibles para este día'})
    
    hora_apertura = datetime.strptime(str(horario['hora_apertura']), '%H:%M:%S')
    hora_cierre = datetime.strptime(str(horario['hora_cierre']), '%H:%M:%S')
    
    slots = []
    current_time = hora_apertura
    
    while current_time < hora_cierre:
        slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=30)
    
    cur.execute("""
        SELECT hora, duracion_total 
        FROM citas 
        WHERE fecha = %s AND estado IN ('pendiente', 'confirmada', 'en_proceso')
    """, (fecha,))
    
    citas_existentes = cur.fetchall()
    
    slots_ocupados = set()
    for cita in citas_existentes:
        hora_cita = datetime.strptime(str(cita['hora']), '%H:%M:%S')
        duracion = cita['duracion_total'] or 60
        
        tiempo_fin = hora_cita + timedelta(minutes=duracion)
        current_slot = hora_cita
        
        while current_slot < tiempo_fin:
            slots_ocupados.add(current_slot.strftime('%H:%M'))
            current_slot += timedelta(minutes=30)
    
    cur.close()
    conn.close()
    
    slots_disponibles = [slot for slot in slots if slot not in slots_ocupados]
    
    return jsonify({
        'disponible': True,
        'slots': slots_disponibles,
        'hora_apertura': hora_apertura.strftime('%H:%M'),
        'hora_cierre': hora_cierre.strftime('%H:%M')
    })

@citas_bp.route('/api/verificar-disponibilidad')
def api_verificar_disponibilidad_cita():
    """API para verificar disponibilidad de una fecha/hora específica"""
    fecha = request.args.get('fecha')
    hora = request.args.get('hora')
    duracion = int(request.args.get('duracion', 60))
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM citas 
        WHERE fecha = %s AND hora = %s AND estado IN ('pendiente', 'confirmada', 'en_proceso')
    """, (fecha, hora))
    
    cita_existente = cur.fetchone()
    
    cur.close()
    conn.close()
    
    disponible = cita_existente['count'] == 0
    
    return jsonify({'disponible': disponible})

#Nuevas APIS================================
# Agregar estas rutas en tu routes.py existente

@citas_bp.route('/api/servicios-seleccionados')
def api_servicios_seleccionados():
    """API para obtener servicios seleccionados de la sesión"""
    servicios = session.get('servicios_seleccionados', [])
    return jsonify({'servicios': servicios})

@citas_bp.route('/api/datos-cita')
def api_datos_cita():
    """API para obtener todos los datos de la cita en sesión"""
    datos = {
        'servicios': session.get('servicios_seleccionados', []),
        'fecha': session.get('fecha_seleccionada'),
        'hora': session.get('hora_seleccionada'),
        'vehiculo': session.get('vehiculo_info', {})
    }
    return jsonify(datos)

@citas_bp.route('/admin/actualizar-cita/<int:id_cita>', methods=['PUT'])
def actualizar_cita_admin(id_cita):
    """Actualizar una cita completa"""
    try:
        data = request.json
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        query = """
            UPDATE citas 
            SET fecha = %s, hora = %s, estado = %s, total = %s, notas = %s 
            WHERE id_cita = %s
        """
        cur.execute(query, (
            data.get('fecha'),
            data.get('hora'),
            data.get('estado'),
            data.get('total'),
            data.get('notas'),
            id_cita
        ))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/admin/eliminar-servicio-cita/<int:id_servicio_cita>', methods=['DELETE'])
def eliminar_servicio_cita_admin(id_servicio_cita):
    """Eliminar un servicio de una cita"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "DELETE FROM cita_servicios WHERE id_cita_servicio = %s"
        cur.execute(query, (id_servicio_cita,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500
    
    # ==============================================
# RUTAS PARA CLIENTES - GESTIÓN DE SUS CITAS
# ==============================================

@citas_bp.route('/mis-citas')
def mis_citas():
    """Página para que los clientes vean sus citas"""
    # En un sistema real, aquí se verificaría la sesión del cliente
    # Por ahora, usaremos un ID de cliente temporal
    id_cliente = session.get('cliente_id', 3)  # Usar 3 como ejemplo
    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("""
        SELECT c.*, v.marca, v.modelo, v.placas, v.color
        FROM citas c
        JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
        WHERE c.id_cliente = %s
        ORDER BY c.fecha DESC, c.hora DESC
    """, (id_cliente,))
    
    citas = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('citas/mis_citas.html', citas=citas)

@citas_bp.route('/cancelar-cita/<int:id_cita>', methods=['POST'])
def cancelar_cita_cliente(id_cita):
    """Cancelar una cita desde el lado del cliente"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verificar que la cita pertenezca al cliente (en un sistema real)
        cur.execute("UPDATE citas SET estado = 'cancelada' WHERE id_cita = %s", (id_cita,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "Cita cancelada correctamente"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@citas_bp.route('/solicitar-modificacion/<int:id_cita>', methods=['POST'])
def solicitar_modificacion_cita(id_cita):
    """Solicitar modificación de cita (pendiente de aprobación)"""
    try:
        data = request.json
        nueva_fecha = data.get('fecha')
        nueva_hora = data.get('hora')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Aquí podrías crear una tabla de solicitudes_modificacion
        # Por ahora, actualizamos directamente
        cur.execute("""
            UPDATE citas 
            SET fecha = %s, hora = %s, estado = 'pendiente' 
            WHERE id_cita = %s
        """, (nueva_fecha, nueva_hora, id_cita))
        conn.commit()
        
        cur.close()
        conn.close()
        
        return jsonify({"message": "Solicitud de modificación enviada"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR", "error": str(e)}), 500
    
    # ==============================================
# SISTEMA DE RECORDATORIOS AUTOMÁTICOS
# ==============================================

def enviar_recordatorios():
    """Función para enviar recordatorios de citas (ejecutar diariamente)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Obtener citas para mañana
        fecha_manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        cur.execute("""
            SELECT c.*, u.nombre_completo, u.correo, u.telefono, 
                   v.marca, v.modelo, v.placas,
                   GROUP_CONCAT(s.nombre SEPARATOR ', ') as servicios
            FROM citas c
            JOIN clientes cl ON c.id_cliente = cl.id_cliente
            JOIN usuarios u ON cl.id_usuario = u.id_usuario
            JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
            LEFT JOIN cita_servicios cs ON c.id_cita = cs.id_cita
            LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
            WHERE c.fecha = %s 
            AND c.estado IN ('pendiente', 'confirmada')
            GROUP BY c.id_cita
        """, (fecha_manana,))
        
        citas_manana = cur.fetchall()
        
        for cita in citas_manana:
            # Aquí integrarías con un servicio de email/SMS
            # Por ahora solo lo registramos
            print(f"RECORDATORIO: Cita #{cita['id_cita']} para {cita['nombre_completo']}")
            print(f"  Fecha: {cita['fecha']} {cita['hora']}")
            print(f"  Vehículo: {cita['marca']} {cita['modelo']} - {cita['placas']}")
            print(f"  Servicios: {cita['servicios']}")
            print(f"  Contacto: {cita['correo']} | {cita['telefono']}")
            print("---")
        
        cur.close()
        conn.close()
        
        return len(citas_manana)
    except Exception as e:
        print(f"Error en recordatorios: {e}")
        return 0

@citas_bp.route('/admin/enviar-recordatorios')
def enviar_recordatorios_manual():
    """Endpoint manual para probar recordatorios"""
    if session.get('user_role') != 'admin':
        return "No autorizado", 403
    
    cantidad = enviar_recordatorios()
    return jsonify({"message": f"Recordatorios enviados para {cantidad} citas"})

@citas_bp.route('/api/verificar-disponibilidad-completa', methods=['POST'])
def api_verificar_disponibilidad_completa():
    """Verificación completa de disponibilidad incluyendo duración"""
    try:
        data = request.json
        fecha = data.get('fecha')
        hora = data.get('hora')
        duracion = int(data.get('duracion', 60))
        
        if not fecha or not hora:
            return jsonify({'error': 'Fecha y hora requeridas'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        # Convertir hora a datetime
        hora_datetime = datetime.strptime(hora, '%H:%M')
        hora_fin = hora_datetime + timedelta(minutes=duracion)
        
        # Verificar citas existentes en ese rango
        cur.execute("""
            SELECT c.hora, c.duracion_total 
            FROM citas c
            WHERE c.fecha = %s 
            AND c.estado IN ('pendiente', 'confirmada', 'en_proceso')
        """, (fecha,))
        
        citas_existentes = cur.fetchall()
        
        disponible = True
        conflicto_con = None
        
        for cita in citas_existentes:
            cita_hora = datetime.strptime(str(cita['hora']), '%H:%M:%S')
            cita_duracion = cita['duracion_total'] or 60
            cita_hora_fin = cita_hora + timedelta(minutes=cita_duracion)
            
            # Verificar superposición
            if (hora_datetime < cita_hora_fin) and (hora_fin > cita_hora):
                disponible = False
                conflicto_con = f"Cita a las {cita_hora.strftime('%H:%M')} ({cita_duracion} min)"
                break
        
        cur.close()
        conn.close()
        
        return jsonify({
            'disponible': disponible,
            'conflicto': conflicto_con,
            'rango_solicitado': f"{hora} - {hora_fin.strftime('%H:%M')}",
            'duracion': duracion
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@citas_bp.route('/agendar')
def agendar_cita():
    """Página para que los clientes agenden citas"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Aquí va la lógica para agendar citas
    return render_template('citas/agendar_cita.html')