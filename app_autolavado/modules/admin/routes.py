from flask import render_template, redirect, url_for, request, flash, session, jsonify
import bcrypt, string, random
from functools import wraps
from . import admin_bp
from config.db_connection import get_db_connection

# Requiere sesión de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') != 'Administrador':
            flash('No tienes permisos para acceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Dashboard principal
@admin_bp.route('/')
@admin_required 
def admin_index():
    return redirect(url_for('admin.inicio'))

@admin_bp.route('/inicio')
@admin_required
def inicio():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN fecha_pago >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN monto END), 0) AS total_30d,
                COALESCE(SUM(CASE WHEN estado = 'pendiente' THEN 1 END), 0) AS pendientes
            FROM pagos
        """)
        pagos_resumen = cur.fetchone()
        cur.close()
        conn.close()
    except Exception:
        pagos_resumen = {"total_30d": 0, "pendientes": 0}
    return render_template('admin/dashboard.html', pagos_resumen=pagos_resumen)

# Redirección de usuarios hacia el nuevo módulo
@admin_bp.route('/usuarios')
@admin_required
def usuarios():
    return redirect(url_for('users.lista_usuarios'))

# Gestión de clientes
@admin_bp.route('/clientes')
@admin_required
def clientes():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            u.id_usuario, u.username, u.nombre_completo, u.correo, u.telefono, u.fecha_registro,
            c.id_cliente, c.folio, c.curp, c.rfc, c.fecha_nacimiento
        FROM usuarios u
        LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
        WHERE u.rol = 'Cliente'
    """)
    datos_clientes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/clientes.html', datos_clientes=datos_clientes)

# Eliminar cliente
@admin_bp.route('/eliminar-cliente', methods=["POST"])
@admin_required
def eliminar_cliente():
    try:
        data = request.json
        id_usuario = data.get('id_usuario')
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE REFERENCED_TABLE_NAME = 'usuarios' 
              AND REFERENCED_COLUMN_NAME = 'id_usuario'
        """)
        tablas = cur.fetchall()
        for t in tablas:
            try:
                cur.execute(f"DELETE FROM {t['TABLE_NAME']} WHERE {t['COLUMN_NAME']} = %s", (id_usuario,))
            except Exception as e:
                print(f"Error eliminando de {t['TABLE_NAME']}: {e}")
        cur.execute("DELETE FROM clientes WHERE id_usuario = %s", (id_usuario,))
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Cliente eliminado correctamente"}), 200
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            cur.close()
            conn.close()
        return jsonify({"message": "ERROR", "error": str(e)}), 500

# Agregar cliente
@admin_bp.route('/agregar-cliente', methods=['POST'])
@admin_required
def agregar_cliente():
    inpUsuario = request.form.get('inpUsuario')
    inpNombre = request.form.get('inpNombre')
    inpCorreo = request.form.get('inpCorreo')
    inpTelefono = request.form.get('inpTelefono')
    inpFolio = request.form.get('inpFolio')
    inpCURP = request.form.get('inpCURP')
    inpRFC = request.form.get('inpRFC')
    inpFechaNacimiento = request.form.get('inpFechaNacimiento')
    psw = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_password = bcrypt.hashpw(psw.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, correo, telefono, rol) 
            VALUES(%s, %s, %s, %s, %s, 'Cliente')
        """, (inpUsuario, hashed_password, inpNombre, inpCorreo, inpTelefono))
        id_usuario = cur.lastrowid
        cur.execute("""
            INSERT INTO clientes (curp, rfc, folio, fecha_nacimiento, id_usuario) 
            VALUES(%s, %s, %s, %s, %s)
        """, (inpCURP, inpRFC, inpFolio, inpFechaNacimiento, id_usuario))
        conn.commit()
        cur.close()
        conn.close()
        flash('Cliente agregado correctamente', 'success')
        return redirect(url_for('admin.clientes'))
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        flash(f'Error al agregar el cliente: {str(e)}', 'error')
        return redirect(url_for('admin.clientes'))
