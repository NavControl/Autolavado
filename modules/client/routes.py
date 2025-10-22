from flask import render_template, request, jsonify, session, redirect, url_for, flash
from config.db_connection import get_db_connection
from . import client_bp
import re

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
            nombre = request.form['nombre']
            email = request.form['email']
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
                SET nombre = %s, email = %s, telefono = %s 
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
        return render_template('client/perfil.html', cliente=None)
    
    finally:
        cursor.close()
        conn.close()

# ==================== Gestión de Citas ====================
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
            return redirect(url_for('client.dashboard'))
        
        # Obtener todas las citas del cliente
        cursor.execute("""
            SELECT c.*, s.nombre as servicio_nombre, s.precio, s.duracion,
                   v.marca, v.modelo, v.placas
            FROM citas c 
            JOIN servicios s ON c.servicio_id = s.id 
            LEFT JOIN vehiculos v ON c.vehiculo_id = v.id_vehiculo
            WHERE c.cliente_id = %s 
            ORDER BY c.fecha_hora DESC
        """, (cliente['id_cliente'],))
        citas = cursor.fetchall()
        
        # Obtener servicios disponibles para agendar nuevas citas
        cursor.execute("SELECT * FROM servicios WHERE activo = 1")
        servicios = cursor.fetchall()
        
        return render_template('client/citas.html', citas=citas, servicios=servicios)
    
    except Exception as e:
        flash('Error al cargar las citas: ' + str(e), 'error')
        return render_template('client/citas.html', citas=[], servicios=[])
    
    finally:
        cursor.close()
        conn.close()
@client_bp.route('/nueva-cita')
def nueva_cita():
    return render_template('citas/nueva_cita.html')

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
            return redirect(url_for('client.dashboard'))
        
        # Obtener historial de servicios completados
        cursor.execute("""
            SELECT 
                s.nombre as servicio_nombre, 
                s.precio, 
                c.fecha_hora, 
                c.estado,
                v.marca,
                v.modelo,
                v.placas,
                p.monto as total_pagado,
                p.metodo_pago
            FROM citas c 
            JOIN servicios s ON c.servicio_id = s.id 
            LEFT JOIN vehiculos v ON c.vehiculo_id = v.id_vehiculo
            LEFT JOIN pagos p ON c.id_cita = p.cita_id
            WHERE c.cliente_id = %s AND c.estado = 'completado'
            ORDER BY c.fecha_hora DESC
        """, (cliente['id_cliente'],))
        historial = cursor.fetchall()
        
        # Calcular total gastado
        total_gastado = sum(item['total_pagado'] or item['precio'] for item in historial)
        
        return render_template('client/historial.html', 
                             historial=historial, 
                             total_gastado=total_gastado)
    
    except Exception as e:
        flash('Error al cargar el historial: ' + str(e), 'error')
        return render_template('client/historial.html', historial=[], total_gastado=0)
    
    finally:
        cursor.close()
        conn.close()

# ==================== API para Agendar Cita ====================
@client_bp.route('/agendar_cita', methods=['POST'])
def agendar_cita():
    """API para agendar una nueva cita"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        servicio_id = data.get('servicio_id')
        fecha_hora = data.get('fecha_hora')
        vehiculo_id = data.get('vehiculo_id')
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Obtener id_cliente
        cursor.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (user_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404
        
        # Insertar nueva cita
        cursor.execute("""
            INSERT INTO citas (cliente_id, servicio_id, vehiculo_id, fecha_hora, estado)
            VALUES (%s, %s, %s, %s, 'pendiente')
        """, (cliente['id_cliente'], servicio_id, vehiculo_id, fecha_hora))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Cita agendada correctamente'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

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
            SELECT c.* FROM citas c
            JOIN clientes cl ON c.cliente_id = cl.id_cliente
            WHERE c.id_cita = %s AND cl.id_usuario = %s
        """, (cita_id, user_id))
        
        cita = cursor.fetchone()
        
        if not cita:
            return jsonify({'success': False, 'message': 'Cita no encontrada'}), 404
        
        # Actualizar estado de la cita
        cursor.execute("""
            UPDATE citas SET estado = 'cancelada' WHERE id_cita = %s
        """, (cita_id,))
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Cita cancelada correctamente'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()