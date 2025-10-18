from flask import render_template, redirect, url_for, request, flash, jsonify
import bcrypt, string, random
from . import admin_bp
from config.db_connection import get_db_connection


# ------------------------------------------------------------
# 📊 DASHBOARD
# ------------------------------------------------------------
@admin_bp.route('/')
def admin_index():
    return redirect(url_for('admin.inicio'))


@admin_bp.route('/inicio')
def inicio():
    return render_template('admin/dashboard.html')


# ------------------------------------------------------------
# 👥 LISTAR USUARIOS (solo datos clave)
# ------------------------------------------------------------
@admin_bp.route('/usuarios')
def usuarios():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            u.id_usuario,
            u.username,
            u.nombre_completo,
            u.correo,
            u.turno,
            u.estado,
            r.nombre AS rol_nombre
        FROM usuarios u
        LEFT JOIN roles r ON u.id_rol = r.id_rol
        ORDER BY u.id_usuario ASC
    """)
    datos_usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/usuarios.html', datos_usuarios=datos_usuarios)


# ------------------------------------------------------------
# 👁️ DETALLE DE USUARIO (con estado y rol)
# ------------------------------------------------------------
@admin_bp.route('/detalle-usuario/<int:id_usuario>')
def detalle_usuario(id_usuario):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            u.id_usuario, 
            u.username, 
            u.nombre_completo, 
            u.correo, 
            u.telefono, 
            u.turno, 
            u.salario, 
            u.fecha_contratacion, 
            u.estado,
            r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.id_usuario = %s
    """, (id_usuario,))
    data = cur.fetchone()
    cur.close()
    conn.close()

    if not data:
        return jsonify({"message": "Usuario no encontrado"}), 404
    return jsonify(data), 200


# ------------------------------------------------------------
# ➕ FORMULARIO NUEVO USUARIO
# ------------------------------------------------------------
@admin_bp.route('/agregar-usuario')
def agregar_usuario():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM roles WHERE id_rol > 1")  # Excluimos al administrador
    datos_roles = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin/agregar_usuario.html', datos_roles=datos_roles)


# ------------------------------------------------------------
# 💾 GUARDAR NUEVO USUARIO
# ------------------------------------------------------------
@admin_bp.route('/frm-usuarios', methods=["POST"])
def frm_usuarios():
    try:
        campos_requeridos = ('inpUsuario', 'inpNombre', 'inpCorreo', 'inpTelefono', 'slcRol')
        if not all(k in request.form for k in campos_requeridos):
            flash(('danger', 'Faltan datos obligatorios'))
            return redirect(url_for('admin.agregar_usuario'))

        inpUsuario = request.form['inpUsuario']
        inpNombre = request.form['inpNombre']
        inpCorreo = request.form['inpCorreo']
        inpTelefono = request.form['inpTelefono']
        slcRol = request.form['slcRol']
        fecha_contratacion = request.form.get('fecha_contratacion') or None
        salario = request.form.get('salario') or None
        turno = request.form.get('turno') or 'matutino'
        estado = request.form.get('estado') or 'activo'

        # Generar contraseña aleatoria segura
        longitud = 8
        caracteres = string.ascii_letters + string.digits
        psw = ''.join(random.choices(caracteres, k=longitud))
        password = psw.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO usuarios 
                (username, password_hash, nombre_completo, correo, telefono, id_rol,
                 fecha_contratacion, salario, turno, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (inpUsuario, hashed_password, inpNombre, inpCorreo, inpTelefono,
              slcRol, fecha_contratacion, salario, turno, estado))
        conn.commit()

        flash(('success', f'Usuario "{inpNombre}" registrado correctamente ✅'))
        return redirect(url_for('admin.usuarios'))

    except Exception as e:
        print("❌ Error al registrar usuario:", e)
        flash(('danger', 'Hubo un error al registrar el usuario'))
        return redirect(url_for('admin.agregar_usuario'))

    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


# ------------------------------------------------------------
# ✏️ EDITAR USUARIO
# ------------------------------------------------------------
@admin_bp.route('/editar-usuario/<int:id_usuario>', methods=["GET", "POST"])
def editar_usuario(id_usuario):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        inpUsuario = request.form['inpUsuario']
        inpNombre = request.form['inpNombre']
        inpCorreo = request.form['inpCorreo']
        inpTelefono = request.form['inpTelefono']
        slcRol = request.form['slcRol']
        fecha_contratacion = request.form.get('fecha_contratacion')
        salario = request.form.get('salario')
        turno = request.form.get('turno')
        estado = request.form.get('estado') or 'activo'

        cur.execute("""
            UPDATE usuarios 
            SET username=%s, nombre_completo=%s, correo=%s, telefono=%s, id_rol=%s,
                fecha_contratacion=%s, salario=%s, turno=%s, estado=%s
            WHERE id_usuario=%s
        """, (inpUsuario, inpNombre, inpCorreo, inpTelefono, slcRol,
              fecha_contratacion, salario, turno, estado, id_usuario))
        conn.commit()

        flash(('success', 'Datos actualizados correctamente ✅'))
        cur.close()
        conn.close()
        return redirect(url_for('admin.usuarios'))

    # Si es GET → cargar datos del usuario
    cur.execute("""
        SELECT u.*, r.id_rol, r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.id_usuario = %s
    """, (id_usuario,))
    usuario = cur.fetchone()

    cur.execute("SELECT * FROM roles WHERE id_rol > 1")
    datos_roles = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("admin/editar_usuario.html", usuario=usuario, datos_roles=datos_roles)


# ------------------------------------------------------------
# 🗑️ ELIMINAR USUARIO
# ------------------------------------------------------------
@admin_bp.route('/eliminar-usuario', methods=["POST"])
def eliminar_usuario():
    try:
        data = request.json
        id_usuario = data.get('id_usuario')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
        conn.commit()

        return jsonify({"message": "OK"}), 200

    except Exception as e:
        print("❌ Error al eliminar usuario:", e)
        return jsonify({"message": "ERROR"}), 500

    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


# ------------------------------------------------------------
# 🧾 SERVICIOS (Placeholder)
# ------------------------------------------------------------
@admin_bp.route('/services')
def services():
    servicios = []
    return render_template('admin/services.html', servicios=servicios)
