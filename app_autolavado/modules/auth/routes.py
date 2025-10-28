from flask import render_template, redirect, url_for, request, session
from datetime import datetime
import bcrypt, random
from . import auth_bp
from config.db_connection import get_db_connection
from config.email_templates import *

# Redirección base
@auth_bp.route('/')
def auth_index():
    return redirect(url_for('auth.login'))

# Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = request.args.get('mensaje')
    tipo_mensaje = request.args.get('tipo_mensaje')
    if mensaje:
        session['mensaje'] = mensaje
        session['tipo_mensaje'] = tipo_mensaje
        return redirect(url_for('auth.login'))
    mensaje = session.pop('mensaje', None)
    tipo_mensaje = session.pop('tipo_mensaje', None)
    username = session.get('username_rem', None)
    return render_template('auth/iniciar_sesion.html', mensaje=mensaje, tipo_mensaje=tipo_mensaje, username=username)

@auth_bp.route('/frm-login', methods=["POST"])
def do_login():
    if 'username' not in request.form or 'password' not in request.form:
        mensaje = "Favor de introducir tus credenciales para iniciar sesión"
        return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='danger'))

    username = request.form.get('username')
    password = request.form.get('password')
    public_ip = request.form.get('public_ip')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_usuario, nombre_completo, password_hash, rol FROM usuarios WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        mensaje = "Usuario y/o contraseña incorrectas"
        return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='danger'))

    hashed_password = user['password_hash'].encode('utf-8')
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        id_usuario = user['id_usuario']
        nombre = user['nombre_completo']
        rol = user['rol']

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("INSERT INTO sesiones (direccion_ip, id_usuario) VALUES (%s, %s)", (public_ip, id_usuario))
        conn.commit()
        cur.close()
        conn.close()

        session['user_id'] = id_usuario
        session['rol'] = rol
        session['nombre'] = nombre
        session['user_type'] = 'client' if rol == 'Cliente' else 'admin'

        if 'remember_me' in request.form:
            session['username_rem'] = username
        else:
            session.pop('username_rem', None)

        if rol == 'Administrador':
            return redirect(url_for('admin.inicio'))
        elif rol == 'Recepcionista':
            return redirect(url_for('admin.usuarios'))
        elif rol == 'Lavador':
            return redirect(url_for('admin.clientes'))
        else:
            return redirect(url_for('client.cliente_inicio'))

    mensaje = "Usuario y/o contraseña incorrectas"
    return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='danger'))

# Restablecer contraseña
@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    session.pop('email_reset_psw', None)
    mensaje = request.args.get('mensaje')
    tipo_mensaje = request.args.get('tipo_mensaje')
    if mensaje:
        session['mensaje'] = mensaje
        session['tipo_mensaje'] = tipo_mensaje
        return redirect(url_for('auth.reset_password'))
    mensaje = session.pop('mensaje', None)
    tipo_mensaje = session.pop('tipo_mensaje', None)
    return render_template('auth/restablecer_contrasenia.html', mensaje=mensaje, tipo_mensaje=tipo_mensaje)

@auth_bp.route('/frm-send-code', methods=["POST"])
def frm_send_code():
    if 'inpEmail' not in request.form:
        mensaje = 'Favor de introducir un correo válido'
        return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))

    inpEmail = request.form.get('inpEmail')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_usuario, COUNT(*) AS NumeroUsuarios, nombre_completo FROM usuarios WHERE correo = %s", (inpEmail,))
    datos_usuarios = cur.fetchone()
    cur.close()
    conn.close()

    if datos_usuarios['NumeroUsuarios'] > 0:
        nombre_usuario = datos_usuarios['nombre_completo']
        id_usuario = datos_usuarios["id_usuario"]
        codigo_verificacion = ''.join(str(random.randint(0, 9)) for _ in range(6))
        descripcion_codigo = "Restablecimiento de contraseña por correo"

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("INSERT INTO codigo_verificacion (codigo_verificacion, descripcion, id_usuario) VALUES (%s, %s, %s)", (codigo_verificacion, descripcion_codigo, id_usuario))
        conn.commit()
        cur.close()
        conn.close()

        asunto = "Tu código de verificación para Autolavado"
        plantilla_correo = plantilla_enviar_codigo_verificacion(nombre_usuario, codigo_verificacion)
        enviar_correo(inpEmail, asunto, plantilla_correo)
        session['email_reset_psw'] = inpEmail
        return redirect(url_for('auth.verify_code'))

    mensaje = 'El correo electrónico no está asociado a ninguna cuenta.'
    return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))

# Verificar código
@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    email_reset_psw = session.get('email_reset_psw')
    if not email_reset_psw:
        mensaje = 'Favor de introducir un correo válido'
        return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))
    mensaje = request.args.get('mensaje')
    tipo_mensaje = request.args.get('tipo_mensaje')
    reenviar_codigo = request.args.get('reenviar_codigo')
    if mensaje:
        session['mensaje'] = mensaje
        session['tipo_mensaje'] = tipo_mensaje
        session['reenviar_codigo'] = reenviar_codigo
        return redirect(url_for('auth.verify_code'))
    mensaje = session.pop('mensaje', None)
    tipo_mensaje = session.pop('tipo_mensaje', None)
    reenviar_codigo = session.pop('reenviar_codigo', None)
    return render_template('auth/verificar_codigo.html', mensaje=mensaje, tipo_mensaje=tipo_mensaje, correo_verificacion=email_reset_psw, reenviar_codigo=reenviar_codigo)

# Cambiar contraseña
@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    email_reset_psw = session.get('email_reset_psw')
    if not email_reset_psw:
        mensaje = 'Favor de introducir un correo válido'
        return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))
    mensaje = request.args.get('mensaje')
    tipo_mensaje = request.args.get('tipo_mensaje')
    if mensaje:
        session['mensaje'] = mensaje
        session['tipo_mensaje'] = tipo_mensaje
        return redirect(url_for('auth.change_password'))
    mensaje = session.pop('mensaje', None)
    tipo_mensaje = session.pop('tipo_mensaje', None)
    return render_template('auth/cambiar_contrasenia.html', mensaje=mensaje, tipo_mensaje=tipo_mensaje)

@auth_bp.route('/frm-change-password', methods=['POST'])
def frm_change_password():
    email_reset_psw = session.get('email_reset_psw')
    if not email_reset_psw:
        mensaje = 'Favor de introducir un correo válido'
        return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))
    if 'inpPsw1' in request.form and 'inpPsw2' in request.form:
        inpPsw1 = request.form.get('inpPsw1')
        inpPsw2 = request.form.get('inpPsw2')
        if inpPsw1 != inpPsw2:
            mensaje = 'Las contraseñas no coinciden'
            return redirect(url_for('auth.change_password', mensaje=mensaje, tipo_mensaje='danger'))
        password = inpPsw1.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("UPDATE usuarios SET password_hash = %s, fecha_cambio_psw = %s WHERE correo = %s", (hashed_password, fecha_actual, email_reset_psw))
        cur.execute("SELECT nombre_completo FROM usuarios WHERE correo = %s", (email_reset_psw,))
        nombre_usuario = cur.fetchone()["nombre_completo"]
        conn.commit()
        cur.close()
        conn.close()
        session.pop('email_reset_psw', None)
        asunto = "Contraseña actualizada"
        plantilla_correo = plantilla_cambio_password(nombre_usuario)
        enviar_correo(email_reset_psw, asunto, plantilla_correo)
        mensaje = "La contraseña fue cambiada correctamente, inicie sesión"
        return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='success'))
    mensaje = 'Las contraseñas no coinciden'
    return redirect(url_for('auth.change_password', mensaje=mensaje, tipo_mensaje='danger'))

# Salir
@auth_bp.route('/salir')
def salir():
    session.clear()
    mensaje = "Has cerrado sesión correctamente"
    return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='success'))
