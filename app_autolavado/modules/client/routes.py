import sys
import os
import re
from datetime import datetime, timedelta

# Agregar el directorio raíz al path para las importaciones
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from flask import render_template, request, jsonify, session, redirect, url_for, flash
from config.db_connection import get_db_connection
from config.email_templates import *
from . import client_bp

# ==================== Dashboard del Cliente ====================
@client_bp.route('/inicio')
def cliente_inicio():
    """Dashboard principal del cliente"""
    if 'user_id' not in session or session.get('user_type') != 'client':
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener información del cliente y usuario
        cursor.execute("""
            SELECT u.*, c.curp, c.rfc, c.folio, c.fecha_nacimiento, c.id_cliente
            FROM usuarios u 
            JOIN clientes c ON u.id_usuario = c.id_usuario 
            WHERE u.id_usuario = %s
        """, (user_id,))
        cliente = cursor.fetchone()
        
        # Obtener citas próximas
        cursor.execute("""
            SELECT c.*, s.nombre as servicio_nombre, s.precio, s.duracion
            FROM citas c 
            JOIN servicios s ON c.servicio_id = s.id 
            WHERE c.cliente_id = %s AND c.fecha_hora >= CURDATE()
            ORDER BY c.fecha_hora ASC
            LIMIT 5
        """, (cliente['id_cliente'],))
        proximas_citas = cursor.fetchall()
        
        # Obtener estadísticas
        cursor.execute("""
            SELECT 
                COUNT(*) as total_citas,
                SUM(CASE WHEN estado = 'completado' THEN 1 ELSE 0 END) as completadas,
                SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) as pendientes
            FROM citas 
            WHERE cliente_id = %s
        """, (cliente['id_cliente'],))
        stats = cursor.fetchone()
        
        return render_template('client/dashboard.html', 
                             cliente=cliente, 
                             proximas_citas=proximas_citas,
                             stats=stats)
    
    except Exception as e:
        flash('Error al cargar el dashboard: ' + str(e), 'error')
        return render_template('client/dashboard.html', cliente=None)
    
    finally:
        cursor.close()
        conn.close()

# ==================== Perfil del Cliente ====================
@client_bp.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """Perfil del cliente - ver y editar"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        try:
            # Datos del formulario
            nombre = request.form['nombre_completo']
            email = request.form['correo']
            telefono = request.form['telefono']
            curp = request.form.get('curp', '')
            rfc = request.form.get('rfc', '')
            fecha_nacimiento = request.form.get('fecha_nacimiento', '')
            
            # Validaciones básicas
            if not nombre or not email:
                flash('Nombre y email son obligatorios', 'error')
                return redirect(url_for('client.perfil'))
            
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                flash('El formato del email no es válido', 'error')
                return redirect(url_for('client.perfil'))
            
            # Actualizar tabla usuarios
            cursor.execute("""
                UPDATE usuarios 
                SET nombre_completo = %s, correo = %s, telefono = %s 
                WHERE id_usuario = %s
            """, (nombre, email, telefono, user_id))
            
            # Actualizar tabla clientes
            cursor.execute("""
                UPDATE clientes 
                SET curp = %s, rfc = %s, fecha_nacimiento = %s 
                WHERE id_usuario = %s
            """, (curp, rfc, fecha_nacimiento if fecha_nacimiento else None, user_id))
            
            conn.commit()
            flash('Perfil actualizado correctamente', 'success')
            
        except Exception as e:
            conn.rollback()
            flash('Error al actualizar el perfil: ' + str(e), 'error')
        
        return redirect(url_for('client.perfil'))
    
    # GET: Mostrar perfil
    try:
        cursor.execute("""
            SELECT u.*, c.curp, c.rfc, c.folio, c.fecha_nacimiento, c.id_cliente
            FROM usuarios u 
            JOIN clientes c ON u.id_usuario = c.id_usuario 
            WHERE u.id_usuario = %s
        """, (user_id,))
        cliente = cursor.fetchone()
        
        return render_template('client/perfil.html', cliente=cliente)
    
    except Exception as e:
        flash('Error al cargar el perfil: ' + str(e), 'error')
        return render_template('client.perfil.html', cliente=None)
    
    finally:
        cursor.close()
        conn.close()

@client_bp.route('/vehiculos')
def vehiculos():
    """Página de gestión de vehículos del cliente"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener id_cliente
        cursor.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (user_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('client.cliente_inicio'))
        
        # Obtener vehículos del cliente
        cursor.execute("""
            SELECT * FROM vehiculos 
            WHERE id_cliente = %s 
            ORDER BY id_vehiculo DESC
        """, (cliente['id_cliente'],))
        vehiculos = cursor.fetchall()
        
        return render_template('client/vehiculos.html', vehiculos=vehiculos)
    
    except Exception as e:
        flash('Error al cargar los vehículos: ' + str(e), 'error')
        return render_template('client/vehiculos.html', vehiculos=[])
    
    finally:
        cursor.close()
        conn.close()

@client_bp.route('/api/vehiculos', methods=['GET', 'POST'])
def gestion_vehiculos():
    """API para gestionar vehículos del cliente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener id_cliente
        cursor.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (user_id,))
        cliente = cursor.fetchone()
        
        if request.method == 'GET':
            # Obtener vehículos del cliente
            cursor.execute("""
                SELECT * FROM vehiculos 
                WHERE id_cliente = %s 
                ORDER BY id_vehiculo DESC
            """, (cliente['id_cliente'],))
            vehiculos = cursor.fetchall()
            return jsonify({'success': True, 'vehiculos': vehiculos})
        
        elif request.method == 'POST':
            # Agregar nuevo vehículo
            data = request.json
            cursor.execute("""
                INSERT INTO vehiculos (marca, modelo, placas, color, anio, id_cliente)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data.get('marca'),
                data.get('modelo'), 
                data.get('placas'),
                data.get('color'),
                data.get('anio'),
                cliente['id_cliente']
            ))
            conn.commit()
            return jsonify({'success': True, 'message': 'Vehículo agregado correctamente'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@client_bp.route('/api/vehiculos/<int:vehiculo_id>', methods=['DELETE', 'PUT'])
def gestion_vehiculo_individual(vehiculo_id):
    """API para editar o eliminar un vehículo específico"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar que el vehículo pertenece al cliente
        cursor.execute("""
            SELECT v.* FROM vehiculos v
            JOIN clientes c ON v.id_cliente = c.id_cliente
            WHERE v.id_vehiculo = %s AND c.id_usuario = %s
        """, (vehiculo_id, user_id))
        
        vehiculo = cursor.fetchone()
        if not vehiculo:
            return jsonify({'success': False, 'message': 'Vehículo no encontrado'}), 404
        
        if request.method == 'DELETE':
            # Verificar que el vehículo no esté en uso en citas futuras
            cursor.execute("""
                SELECT COUNT(*) as count FROM citas 
                WHERE id_vehiculo = %s AND fecha >= CURDATE() 
                AND estado IN ('pendiente', 'confirmada')
            """, (vehiculo_id,))
            
            citas_futuras = cursor.fetchone()
            if citas_futuras['count'] > 0:
                return jsonify({
                    'success': False, 
                    'message': 'No se puede eliminar el vehículo porque tiene citas futuras programadas'
                }), 400
            
            cursor.execute("DELETE FROM vehiculos WHERE id_vehiculo = %s", (vehiculo_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Vehículo eliminado correctamente'})
        
        elif request.method == 'PUT':
            # Actualizar vehículo
            data = request.json
            cursor.execute("""
                UPDATE vehiculos 
                SET marca = %s, modelo = %s, placas = %s, color = %s, anio = %s
                WHERE id_vehiculo = %s
            """, (
                data.get('marca'),
                data.get('modelo'),
                data.get('placas'), 
                data.get('color'),
                data.get('anio'),
                vehiculo_id
            ))
            conn.commit()
            return jsonify({'success': True, 'message': 'Vehículo actualizado correctamente'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
        
# ==================== Gestión de Citas ====================
@client_bp.route('/buscar')
def buscar():
    query = request.args.get('q', '')
    # Lógica para buscar en citas, servicios, etc.
    # Retornar resultados a una plantilla específica

@client_bp.route('/citas')
def citas():
    """Gestión de citas del cliente"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener id_cliente
        cursor.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (user_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('client.cliente_inicio'))
        
        # Obtener todas las citas del cliente con información CORREGIDA
        cursor.execute("""
            SELECT 
                c.id_cita,
                c.fecha,
                c.hora,
                c.duracion_total,
                c.total as precio,
                c.estado,
                c.notas,
                v.marca,
                v.modelo,
                v.placas,
                s.nombre as servicio_nombre,
                s.precio as servicio_precio
            FROM citas c 
            LEFT JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
            LEFT JOIN cita_servicios cs ON c.id_cita = cs.id_cita
            LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
            WHERE c.id_cliente = %s 
            ORDER BY c.fecha DESC, c.hora DESC
        """, (cliente['id_cliente'],))
        citas = cursor.fetchall()
        
        # Procesar los datos para la plantilla
        citas_procesadas = []
        for cita in citas:
            cita_procesada = {
                'id_cita': cita['id_cita'],
                'fecha_hora': None,
                'servicio_nombre': cita['servicio_nombre'] or 'Servicio no especificado',
                'precio': cita['precio'] or cita['servicio_precio'] or 0,
                'estado': cita['estado'],
                'marca': cita['marca'],
                'modelo': cita['modelo'],
                'placas': cita['placas']
            }
            
            # Combinar fecha y hora en un objeto datetime
            if cita['fecha'] and cita['hora']:
                try:
                    fecha_hora_str = f"{cita['fecha']} {cita['hora']}"
                    cita_procesada['fecha_hora'] = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    cita_procesada['fecha_hora'] = None
            
            citas_procesadas.append(cita_procesada)
        
        # Obtener servicios disponibles para agendar nuevas citas
        cursor.execute("SELECT * FROM servicios WHERE activo = 1")
        servicios = cursor.fetchall()
        
        return render_template('client/citas.html', citas=citas_procesadas, servicios=servicios)
    
    except Exception as e:
        flash('Error al cargar las citas: ' + str(e), 'error')
        import traceback
        traceback.print_exc()
        return render_template('citas/citas.html', citas=[], servicios=[])
    
    finally:
        cursor.close()
        conn.close()

# ==================== Historial de Servicios ====================
@client_bp.route('/historial')
def historial():
    """Historial de servicios del cliente"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Obtener id_cliente
        cursor.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (user_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('client.cliente_inicio'))
        
        print(f"🔍 Buscando historial para cliente ID: {cliente['id_cliente']}")
        
        # Obtener historial de servicios - CONSULTA CORREGIDA
        cursor.execute("""
            SELECT 
                c.id_cita,
                s.nombre as servicio_nombre, 
                cs.precio, 
                cs.duracion,
                c.fecha,
                c.hora,
                c.estado,
                c.total,
                v.marca,
                v.modelo,
                v.placas,
                cs.precio as total_pagado,
                'Efectivo' as metodo_pago
            FROM citas c 
            JOIN cita_servicios cs ON c.id_cita = cs.id_cita
            JOIN servicios s ON cs.id_servicio = s.id_servicio
            LEFT JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
            WHERE c.id_cliente = %s AND c.estado = 'completada'
            ORDER BY c.fecha DESC, c.hora DESC
        """, (cliente['id_cliente'],))
        
        historial_raw = cursor.fetchall()
        
        print(f"📊 Historial encontrado: {len(historial_raw)} registros")
        
        # Procesar los datos para crear fecha_hora combinada
        historial = []
        for servicio in historial_raw:
            servicio_procesado = dict(servicio)  # Convertir a dict mutable
            
            # Combinar fecha y hora en un objeto datetime
            if servicio['fecha'] and servicio['hora']:
                try:
                    # Manejar diferentes tipos de datos para fecha y hora
                    fecha = servicio['fecha']
                    hora = servicio['hora']
                    
                    # Si fecha es datetime.date, convertir a string
                    if hasattr(fecha, 'strftime'):
                        fecha_str = fecha.strftime('%Y-%m-%d')
                    else:
                        fecha_str = str(fecha)
                    
                    # Si hora es datetime.time o timedelta, convertir a string
                    if hasattr(hora, 'strftime'):
                        hora_str = hora.strftime('%H:%M:%S')
                    elif hasattr(hora, 'total_seconds'):
                        # Si es timedelta
                        total_seconds = int(hora.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        hora_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        hora_str = str(hora)
                    
                    # Combinar en datetime
                    fecha_hora_str = f"{fecha_str} {hora_str}"
                    servicio_procesado['fecha_hora'] = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
                    
                except Exception as e:
                    print(f"❌ Error al procesar fecha/hora: {e}")
                    servicio_procesado['fecha_hora'] = None
            else:
                servicio_procesado['fecha_hora'] = None
            
            historial.append(servicio_procesado)
        
        # Calcular total gastado
        total_gastado = sum(float(item['precio']) for item in historial)
        
        # Debug: mostrar primeros registros
        for i, item in enumerate(historial[:3]):
            print(f"📅 Registro {i+1}: fecha={item.get('fecha')}, hora={item.get('hora')}, fecha_hora={item.get('fecha_hora')}")
        
        return render_template('client/historial.html', 
                             historial=historial, 
                             total_gastado=total_gastado)
    
    except Exception as e:
        flash(f'Error al cargar el historial: {str(e)}', 'error')
        print(f"❌ Error en historial: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('client/historial.html', historial=[], total_gastado=0)
    
    finally:
        cursor.close()
        conn.close()
# ==================== Proceso de Citas ====================
@client_bp.route('/nueva-cita')
def nueva_cita():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('citas/nueva_cita.html') 

@client_bp.route('/seleccionar-servicios')
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

@client_bp.route('/seleccionar-fecha')
def seleccionar_fecha():
    """Página para seleccionar fecha y hora"""
    return render_template('citas/seleccionar_fecha.html')

@client_bp.route('/informacion-vehiculo')
def informacion_vehiculo_cliente():
    """Página para ingresar información del vehículo"""
    return render_template('citas/informacion_vehiculo.html')

@client_bp.route('/confirmar-cita')
def confirmar_cita_cliente():
    """Página para confirmar la cita"""
    servicios_seleccionados = session.get('servicios_seleccionados', [])
    fecha_seleccionada = session.get('fecha_seleccionada')
    hora_seleccionada = session.get('hora_seleccionada')
    vehiculo_info = session.get('vehiculo_info', {})
    
    total = sum(servicio['precio'] for servicio in servicios_seleccionados)
    
    return render_template('citas/confirmar_cita.html',
                         servicios=servicios_seleccionados,
                         fecha=fecha_seleccionada,
                         hora=hora_seleccionada,
                         vehiculo=vehiculo_info,
                         total=total)

# ==================== APIs para Citas ====================
@client_bp.route('/guardar-servicios', methods=['POST'])
def guardar_servicios():
    """Guardar servicios seleccionados en sesión"""
    try:
        data = request.json
        session['servicios_seleccionados'] = data.get('servicios', [])
        return jsonify({"success": True, "message": "Servicios guardados correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@client_bp.route('/guardar-fecha', methods=['POST'])
def guardar_fecha():
    """Guardar fecha y hora seleccionadas en sesión"""
    try:
        data = request.json
        session['fecha_seleccionada'] = data.get('fecha')
        session['hora_seleccionada'] = data.get('hora')
        return jsonify({"success": True, "message": "Fecha y hora guardadas correctamente"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
@client_bp.route('/api/datos-cita')
def api_datos_cita():
    """API para obtener todos los datos de la cita en sesión"""
    datos = {
        'servicios': session.get('servicios_seleccionados', []),
        'fecha': session.get('fecha_seleccionada'),
        'hora': session.get('hora_seleccionada'),
        'vehiculo': session.get('vehiculo_info', {})
    }
    return jsonify(datos)
@client_bp.route('/guardar-vehiculo', methods=['POST'])
def guardar_vehiculo():
    """Guardar información del vehículo en sesión"""
    try:
        data = request.json
        session['vehiculo_info'] = data
        return jsonify({"success": True, "message": "Información del vehículo guardada"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@client_bp.route('/api/servicios-seleccionados')
def api_servicios_seleccionados():
    """API para obtener servicios seleccionados desde sesión"""
    servicios = session.get('servicios_seleccionados', [])
    return jsonify({'servicios': servicios, 'success': True})

@client_bp.route('/api/horarios-disponibles')
def api_obtener_horarios():
    """API para obtener horarios disponibles"""
    fecha = request.args.get('fecha')
    excluir_cita_id = request.args.get('excluir_cita_id', type=int)
    
    if not fecha:
        return jsonify({'success': False, 'message': 'Fecha no proporcionada'})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Horarios base del negocio (formato time)
        horarios_base = [
            "09:00:00", "10:00:00", "11:00:00", "12:00:00", 
            "14:00:00", "15:00:00", "16:00:00", "17:00:00"
        ]
        
        # Consultar horarios ocupados
        query = """
            SELECT hora 
            FROM citas 
            WHERE fecha = %s 
            AND estado IN ('pendiente', 'confirmada', 'en_proceso')
        """
        params = [fecha]
        
        if excluir_cita_id:
            query += " AND id_cita != %s"
            params.append(excluir_cita_id)
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        # Procesar horarios ocupados - manejar diferentes tipos de datos
        horarios_ocupados = []
        for row in resultados:
            hora = row['hora']
            # Manejar diferentes tipos de datos que puede devolver MySQL
            if hasattr(hora, 'strftime'):
                # Si es datetime o time
                hora_str = hora.strftime('%H:%M:%S')
            elif hasattr(hora, 'total_seconds'):
                # Si es timedelta
                total_seconds = int(hora.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                hora_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                # Si ya es string
                hora_str = str(hora)
            
            horarios_ocupados.append(hora_str)
        
        # Filtrar horarios disponibles
        horarios_disponibles = [
            hora for hora in horarios_base 
            if hora not in horarios_ocupados
        ]
        
        # Formatear para mostrar (sin segundos)
        horarios_formateados = [hora[:-3] for hora in horarios_disponibles]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'horarios': horarios_formateados,
            'message': f'Hay {len(horarios_formateados)} horarios disponibles'
        })
        
    except Exception as e:
        import traceback
        print(f"Error en api_obtener_horarios: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': str(e)})
    
@client_bp.route('/procesar-cita', methods=['POST'])
def procesar_cita_cliente():
    """Procesar la creación de la cita"""
    try:
        servicios_seleccionados = session.get('servicios_seleccionados', [])
        fecha = session.get('fecha_seleccionada')
        hora = session.get('hora_seleccionada')
        vehiculo_info = session.get('vehiculo_info', {})

        print("🔍 Datos de la cita:")
        print(f"   Servicios: {servicios_seleccionados}")
        print(f"   Fecha: {fecha}")
        print(f"   Hora: {hora}")
        print(f"   Vehículo: {vehiculo_info}")

        if not all([servicios_seleccionados, fecha, hora, vehiculo_info]):
            return jsonify({"success": False, "message": "Faltan datos de la cita"}), 400

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Calcular total y duración
        total = sum(float(servicio['precio']) for servicio in servicios_seleccionados)
        duracion_total = sum(int(servicio['duracion']) for servicio in servicios_seleccionados)

        # Obtener cliente
        id_usuario = session.get('user_id')
        cur.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (id_usuario,))
        cliente = cur.fetchone()

        if not cliente:
            return jsonify({"success": False, "message": "Cliente no encontrado"}), 404

        id_cliente = cliente['id_cliente']

        # Crear vehículo
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

        # Crear cita
        cur.execute("""
            INSERT INTO citas (id_cliente, id_vehiculo, fecha, hora, duracion_total, total, estado)
            VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')
        """, (id_cliente, id_vehiculo, fecha, hora, duracion_total, total))
        id_cita = cur.lastrowid

        # Agregar servicios a la cita
        for servicio in servicios_seleccionados:
            servicio_id = servicio['id']
            servicio_tipo = servicio['tipo']

            if servicio_tipo == 'servicio':
                cur.execute("""
                    INSERT INTO cita_servicios (id_cita, id_servicio, tipo, precio, duracion)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    id_cita,
                    servicio_id,
                    servicio_tipo,
                    servicio['precio'],
                    servicio['duracion']
                ))

            elif servicio_tipo == 'paquete':
                cur.execute("""
                    SELECT ps.id_servicio 
                    FROM paquete_servicios ps 
                    WHERE ps.id_paquete = %s
                """, (servicio_id,))
                servicios_del_paquete = cur.fetchall()

                if not servicios_del_paquete:
                    continue

                for servicio_paquete in servicios_del_paquete:
                    cur.execute("""
                        INSERT INTO cita_servicios (id_cita, id_servicio, tipo, precio, duracion)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        id_cita,
                        servicio_paquete['id_servicio'],
                        'paquete',
                        servicio['precio'] / len(servicios_del_paquete),
                        servicio['duracion'] / len(servicios_del_paquete)
                    ))

        conn.commit()

        # ==================== Envío de correo ====================
        try:
            cur.execute("""
                SELECT u.nombre_completo, u.correo 
                FROM usuarios u 
                WHERE u.id_usuario = %s
            """, (id_usuario,))
            cliente_info = cur.fetchone()

            if cliente_info and cliente_info['correo']:
                datos_cita_correo = {
                    'nombre_cliente': cliente_info['nombre_completo'],
                    'fecha': fecha,
                    'hora': hora,
                    'vehiculo': f"{vehiculo_info.get('marca', '')} {vehiculo_info.get('modelo', '')} ({vehiculo_info.get('placas', '')})",
                    'duracion': duracion_total,
                    'estado': 'Confirmada',
                    'total': total,
                    'servicios': servicios_seleccionados
                }

                mensaje_html = plantilla_confirmacion_cita(datos_cita_correo)
                enviar_correo(
                    destinatario=cliente_info['correo'],
                    asunto=f"✅ Confirmación de Cita - Autolavado - {fecha}",
                    mensaje_html=mensaje_html
                )
        except Exception as e:
            print(f"Error en envío de correo: {e}")
        # ========================================================

        cur.close()
        conn.close()

        # Limpiar sesión
        session.pop('servicios_seleccionados', None)
        session.pop('fecha_seleccionada', None)
        session.pop('hora_seleccionada', None)
        session.pop('vehiculo_info', None)

        # Redirigir directamente a la vista de pago
        redirect_url = url_for('client.pago_cliente', id_cita=id_cita)
        return jsonify({
            "success": True,
            "message": "Cita creada exitosamente",
            "redirect_url": redirect_url
        }), 200

    except Exception as e:
        print(f"❌ Error al procesar cita: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

        
@client_bp.route('/confirmacion/<int:id_cita>')
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

# ==================== Cancelar Cita ====================
@client_bp.route('/cancelar_cita/<int:cita_id>', methods=['POST'])
def cancelar_cita(cita_id):
    """Cancelar una cita existente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la cita pertenece al cliente
        cursor.execute("""
            SELECT c.*, u.nombre_completo, u.correo 
            FROM citas c
            JOIN clientes cl ON c.id_cliente = cl.id_cliente
            JOIN usuarios u ON cl.id_usuario = u.id_usuario
            WHERE c.id_cita = %s AND cl.id_usuario = %s
        """, (cita_id, user_id))
        
        cita = cursor.fetchone()
        
        if not cita:
            return jsonify({'success': False, 'message': 'Cita no encontrada'}), 404
        
        # Guardar información para el correo antes de cancelar
        info_cita = {
            'nombre_cliente': cita['nombre_completo'],
            'fecha': cita['fecha'].strftime('%Y-%m-%d') if hasattr(cita['fecha'], 'strftime') else str(cita['fecha']),
            'hora': cita['hora'].strftime('%H:%M') if hasattr(cita['hora'], 'strftime') else str(cita['hora']),
            'correo': cita['correo']
        }
        
        # Actualizar estado de la cita
        cursor.execute("""
            UPDATE citas SET estado = 'cancelada' WHERE id_cita = %s
        """, (cita_id,))
        
        conn.commit()

        # ==================== ENVÍO DE CORREO DE CANCELACIÓN ====================
        try:       
            mensaje_cancelacion = f"""
            <html>
            <body>
                <h2>❌ Cita Cancelada - Autolavado</h2>
                <p>Hola {info_cita['nombre_cliente']},</p>
                <p>Tu cita programada para el <strong>{info_cita['fecha']}</strong> a las <strong>{info_cita['hora']}</strong> ha sido cancelada.</p>
                <p>Si esto fue un error o necesitas agendar una nueva cita, por favor visita nuestro sistema.</p>
                <br>
                <p>¡Esperamos verte pronto!</p>
                <p><strong>Autolavado</strong></p>
            </body>
            </html>
            """
            
            resultado_correo = enviar_correo(
                destinatario=info_cita['correo'],
                asunto="❌ Cita Cancelada - Autolavado",
                mensaje_html=mensaje_cancelacion
            )
            
            print(f"📧 Resultado envío de correo (cancelación): {resultado_correo}")
            
        except Exception as e:
            print(f"❌ Error al enviar correo de cancelación: {str(e)}")
        # ==================== FIN ENVÍO DE CORREO ====================
        
        return jsonify({'success': True, 'message': 'Cita cancelada correctamente'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()
# ==================== Reprogramar Cita ====================
@client_bp.route('/reprogramar_cita/<int:cita_id>')
def reprogramar_cita(cita_id):
    """Página para reprogramar una cita existente"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Verificar que la cita pertenece al cliente y puede ser reprogramada
        cursor.execute("""
            SELECT 
                c.id_cita,
                c.fecha,
                c.hora,
                c.estado,
                v.marca,
                v.modelo,
                v.placas,
                s.nombre as servicio_nombre
            FROM citas c
            JOIN clientes cl ON c.id_cliente = cl.id_cliente
            JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
            LEFT JOIN cita_servicios cs ON c.id_cita = cs.id_cita
            LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
            WHERE c.id_cita = %s AND cl.id_usuario = %s 
            AND c.estado IN ('pendiente', 'confirmada')
        """, (cita_id, user_id))
        
        cita_actual = cursor.fetchone()
        
        if not cita_actual:
            flash('Cita no encontrada o no se puede reprogramar', 'error')
            return redirect(url_for('client.citas'))
        
        # Procesar fecha y hora para la plantilla
        fecha_actual = None
        hora_actual = None
        
        if cita_actual['fecha']:
            fecha_actual = cita_actual['fecha'].strftime('%d/%m/%Y') if hasattr(cita_actual['fecha'], 'strftime') else str(cita_actual['fecha'])
        
        if cita_actual['hora']:
            # Manejar diferentes tipos de datos para la hora
            hora = cita_actual['hora']
            if hasattr(hora, 'strftime'):
                hora_actual = hora.strftime('%H:%M')
            elif hasattr(hora, 'total_seconds'):
                # Si es timedelta
                total_seconds = int(hora.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                hora_actual = f"{hours:02d}:{minutes:02d}"
            else:
                hora_actual = str(hora)
        
        # Crear un objeto con la información formateada
        cita_procesada = {
            'id_cita': cita_actual['id_cita'],
            'servicio_nombre': cita_actual['servicio_nombre'] or 'Servicio no especificado',
            'marca': cita_actual['marca'],
            'modelo': cita_actual['modelo'],
            'placas': cita_actual['placas'],
            'fecha_actual': fecha_actual,
            'hora_actual': hora_actual,
            'estado': cita_actual['estado']
        }
        
        # Fecha mínima para el calendario (hoy)
        min_date = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('citas/reprogramar_cita.html', 
                             cita_actual=cita_procesada, 
                             min_date=min_date)
    
    except Exception as e:
        flash(f'Error al cargar la página de reprogramación: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('client.citas'))
    
    finally:
        cursor.close()
        conn.close()

@client_bp.route('/procesar_reprogramacion', methods=['POST'])
def procesar_reprogramacion():
    """Procesar la reprogramación de una cita"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.json
        cita_id = data.get('cita_id')
        nueva_fecha = data.get('nueva_fecha')
        nueva_hora = data.get('nueva_hora')
        
        if not all([cita_id, nueva_fecha, nueva_hora]):
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que la cita pertenece al cliente y puede ser reprogramada
        cursor.execute("""
            SELECT c.* FROM citas c
            JOIN clientes cl ON c.id_cliente = cl.id_cliente
            WHERE c.id_cita = %s AND cl.id_usuario = %s 
            AND c.estado IN ('pendiente', 'confirmada')
        """, (cita_id, user_id))
        
        cita = cursor.fetchone()
        
        if not cita:
            return jsonify({'success': False, 'message': 'Cita no encontrada o no se puede reprogramar'}), 404
        
        # Verificar disponibilidad de la nueva fecha y hora
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM citas 
            WHERE fecha = %s AND hora = %s 
            AND estado IN ('pendiente', 'confirmada', 'en_proceso')
            AND id_cita != %s
        """, (nueva_fecha, nueva_hora, cita_id))
        
        cita_existente = cursor.fetchone()
        
        if cita_existente['count'] > 0:
            return jsonify({'success': False, 'message': 'El horario seleccionado no está disponible'}), 400
        
        # Actualizar la cita con la nueva fecha y hora
        cursor.execute("""
            UPDATE citas 
            SET fecha = %s, hora = %s 
            WHERE id_cita = %s
        """, (nueva_fecha, nueva_hora, cita_id))
        
        conn.commit()

        # ==================== ENVÍO DE CORREO DE REPROGRAMACIÓN ====================
        try:
            # Obtener información completa de la cita para el correo
            cursor.execute("""
                SELECT 
                    c.*,
                    u.nombre_completo,
                    u.correo,
                    v.marca,
                    v.modelo,
                    v.placas,
                    s.nombre as servicio_nombre,
                    s.precio as servicio_precio,
                    s.duracion as servicio_duracion
                FROM citas c
                JOIN clientes cl ON c.id_cliente = cl.id_cliente
                JOIN usuarios u ON cl.id_usuario = u.id_usuario
                JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
                LEFT JOIN cita_servicios cs ON c.id_cita = cs.id_cita
                LEFT JOIN servicios s ON cs.id_servicio = s.id_servicio
                WHERE c.id_cita = %s
            """, (cita_id,))
            
            cita_info = cursor.fetchall()
            
            if cita_info and cita_info[0]['correo']:
                # Preparar datos para el correo
                datos_cita_correo = {
                    'nombre_cliente': cita_info[0]['nombre_completo'],
                    'fecha': nueva_fecha,
                    'hora': nueva_hora,
                    'vehiculo': f"{cita_info[0]['marca']} {cita_info[0]['modelo']} ({cita_info[0]['placas']})",
                    'duracion': cita_info[0]['duracion_total'],
                    'estado': 'Reprogramada',
                    'total': float(cita_info[0]['total']),
                    'servicios': [{
                        'nombre': item['servicio_nombre'],
                        'precio': float(item['servicio_precio']),
                        'duracion': item['servicio_duracion']
                    } for item in cita_info if item['servicio_nombre']]
                }
                
                # Generar el contenido del correo
                mensaje_html = plantilla_confirmacion_cita(datos_cita_correo)
                
                # Enviar el correo
                resultado_correo = enviar_correo(
                    destinatario=cita_info[0]['correo'],
                    asunto=f"🔄 Cita Reprogramada - Autolavado - {nueva_fecha}",
                    mensaje_html=mensaje_html
                )
                
                print(f"📧 Resultado envío de correo (reprogramación): {resultado_correo}")
                
        except Exception as e:
            print(f"❌ Error al enviar correo de reprogramación: {str(e)}")
            # No interrumpimos el flujo si falla el correo
        # ==================== FIN ENVÍO DE CORREO ====================
        
        return jsonify({
            'success': True, 
            'message': 'Cita reprogramada correctamente'
        })
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

# ==================== APIs adicionales ====================
@client_bp.route('/api/verificar-disponibilidad')
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
    
    return jsonify({'disponible': disponible, 'success': True})

# ==================== 💰 Ruta de Pago del Cliente ====================
@client_bp.route('/pagos/<int:id_cita>', methods=['GET', 'POST'])
def pago_cliente(id_cita):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute("""
            SELECT
                c.id_cita,
                c.fecha,
                c.hora,
                COALESCE(c.total, SUM(cs.precio)) AS total,
                c.estado,
                v.marca,
                v.modelo,
                v.placas
            FROM citas c
            JOIN clientes cl ON c.id_cliente = cl.id_cliente
            JOIN usuarios u ON cl.id_usuario = u.id_usuario
            LEFT JOIN vehiculos v ON c.id_vehiculo = v.id_vehiculo
            LEFT JOIN cita_servicios cs ON cs.id_cita = c.id_cita
            WHERE c.id_cita = %s
              AND u.id_usuario = %s
            GROUP BY c.id_cita, c.fecha, c.hora, c.estado, v.marca, v.modelo, v.placas
        """, (id_cita, session['user_id']))
        cita = cur.fetchone()

        if not cita:
            flash("No se encontró la cita o no tienes permiso para verla.", "danger")
            return redirect(url_for('client.citas'))

        if request.method == 'POST':
            metodo = (request.form.get('metodo_pago') or '').lower().strip()
            if metodo not in ('efectivo', 'paypal'):
                flash('Método de pago inválido.', 'warning')
                return redirect(url_for('client.pago_cliente', id_cita=id_cita))

            monto = float(cita['total'] or 0)

            if metodo == 'efectivo':
                cur.execute("""
                    INSERT INTO pagos (id_cita, monto, metodo_pago, estado, fecha_pago)
                    VALUES (%s, %s, 'Efectivo', 'pendiente', NOW())
                """, (id_cita, monto))
                flash('Pago en efectivo registrado. Se validará al presentarte en el establecimiento.', 'info')

            elif metodo == 'paypal':
                cur.execute("""
                    INSERT INTO pagos (id_cita, monto, metodo_pago, estado, fecha_pago)
                    VALUES (%s, %s, 'PayPal', 'completado', NOW())
                """, (id_cita, monto))
                flash('Pago completado con PayPal.', 'success')

            conn.commit()
            return redirect(url_for('client.citas'))

        return render_template('pagos/seleccionar_pago.html', cita=cita)

    except Exception as e:
        conn.rollback()
        flash(f"Error al procesar el pago: {e}", "danger")
        return redirect(url_for('client.citas'))

    finally:
        cur.close()
        conn.close()
