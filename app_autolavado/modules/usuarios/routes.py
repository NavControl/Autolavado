from flask import render_template, redirect, url_for, request, flash, session, jsonify
from config.db_connection import get_db_connection
import bcrypt, random, string
from functools import wraps
from . import usuarios_bp

# Requiere sesión de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') != 'Administrador':
            flash('No tienes permisos para acceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Listar usuarios
@usuarios_bp.route('/')
@admin_required
def lista_usuarios():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_usuario, username, nombre_completo, correo, telefono, rol FROM usuarios")
    datos_usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('usuarios/usuario.html', datos_usuarios=datos_usuarios)

# Agregar usuario (formulario)
@usuarios_bp.route('/agregar')
@admin_required
def agregar_usuario():
    roles_disponibles = ['Administrador', 'Recepcionista', 'Lavador', 'Cliente']
    return render_template('usuarios/agregar_usuario.html', roles=roles_disponibles)

# Guardar nuevo usuario
@usuarios_bp.route('/guardar', methods=['POST'])
@admin_required
def guardar_usuario():
    try:
        inpUsuario = request.form.get('inpUsuario')
        inpNombre = request.form.get('inpNombre')
        inpCorreo = request.form.get('inpCorreo')
        inpTelefono = request.form.get('inpTelefono')
        slcRol = request.form.get('slcRol')

        psw = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = bcrypt.hashpw(psw.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO usuarios (username, password_hash, nombre_completo, correo, telefono, rol)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (inpUsuario, hashed_password, inpNombre, inpCorreo, inpTelefono, slcRol))
        conn.commit()
        cur.close()
        conn.close()

        flash(f'Usuario registrado correctamente. Contraseña generada: {psw}', 'success')
        return redirect(url_for('users.lista_usuarios'))
    except Exception as e:
        flash(f'Error al registrar usuario: {str(e)}', 'danger')
        return redirect(url_for('users.lista_usuarios'))

# Eliminar usuario
@usuarios_bp.route('/eliminar/<int:id_usuario>', methods=['DELETE'])
@admin_required
def eliminar_usuario(id_usuario):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"message": "Error al eliminar usuario", "error": str(e)}), 500
