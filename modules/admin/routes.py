from flask import render_template, redirect, url_for, request, flash, session, jsonify
import bcrypt, string, random
from functools import wraps
from . import admin_bp

# Importamos la conecion a la BD
from config.db_connection import get_db_connection

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('id_rol') != 1:
            flash('No tienes permisos para acceder a esta página.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required 
def admin_index():
    return redirect(url_for('admin.inicio'))

@admin_bp.route('/inicio')
def inicio():
    return render_template('admin/dashboard.html')


@admin_bp.route('/usuarios')
def usuarios():

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    query="""
        SELECT
            *
        FROM
            usuarios
    """
    cur.execute(query)
    datos_usuarios = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin/usuarios.html', datos_usuarios=datos_usuarios)



@admin_bp.route('/agregar-usuario')
def agregar_usuario():

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    query="""
        SELECT
            *
        FROM
            roles
    """
    cur.execute(query)
    datos_roles = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('admin/agregar_usuario.html', datos_roles=datos_roles)



@admin_bp.route('/frm-usuarios', methods=["POST", "GET"])
def frm_usuarios():

    if request.method == 'POST' and 'inpUsuario' in request.form and 'inpNombre' in request.form and 'inpCorreo' in request.form and 'inpTelefono' in request.form and 'slcRol' in request.form :
        inpUsuario = request.form.get('inpUsuario')
        inpNombre = request.form.get('inpNombre')
        inpCorreo = request.form.get('inpCorreo')
        inpTelefono = request.form.get('inpTelefono')
        slcRol = request.form.get('slcRol')

        longitud = 8
        caracteres = string.ascii_letters + string.digits 
        psw = ''.join(random.choices(caracteres, k=longitud))
        print("Tu contraseña es: ==========================================")
        print(psw)
        password = psw.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query="""
            INSERT INTO usuarios (username, password_hash, nombre_completo, correo, telefono, id_rol) VALUES(%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (inpUsuario, hashed_password, inpNombre, inpCorreo, inpTelefono, slcRol))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('admin.usuarios'))
    

@admin_bp.route('/eliminar-usuario', methods=["POST", "GET"])
def eliminar_usuario():

    try:
        data = request.json
        id_usuario = data.get('id_usuario')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query="""
            DELETE FROM usuarios WHERE id_usuario = %s
        """
        cur.execute(query, (id_usuario,))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "OK"}), 200
    except Exception as e:
        return jsonify({"message": "ERROR"}), 500


@admin_bp.route('/editar-usuario/<int:id_usuario>', methods=["GET", "POST"])
def editar_usuario(id_usuario):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        inpUsuario = request.form.get('inpUsuario')
        inpNombre = request.form.get('inpNombre')
        inpCorreo = request.form.get('inpCorreo')
        inpTelefono = request.form.get('inpTelefono')
        slcRol = request.form.get('slcRol')

        query = """
            UPDATE usuarios 
            SET username=%s, nombre_completo=%s, correo=%s, telefono=%s, id_rol=%s
            WHERE id_usuario=%s
        """
        cur.execute(query, (inpUsuario, inpNombre, inpCorreo, inpTelefono, slcRol, id_usuario))
        conn.commit()
        cur.close()
        conn.close()

        flash(('success', 'Datos actualizados correctamente'))
        return redirect(url_for('admin.usuarios'))

    # Si es GET → mostrar datos actuales
    query = """
        SELECT u.*, r.id_rol, r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.id_usuario = %s
    """
    cur.execute(query, (id_usuario,))
    usuario = cur.fetchone()

    # Traemos roles para el select
    cur.execute("SELECT * FROM roles")
    datos_roles = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin/editar_usuario.html", usuario=usuario, datos_roles=datos_roles)




@admin_bp.route('/services')
def services():
    servicios = []  # Para probar la interfaz sin base de datos
    return render_template('admin/services.html', servicios=servicios)


