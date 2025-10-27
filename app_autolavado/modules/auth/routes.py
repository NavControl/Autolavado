from flask import render_template, redirect, url_for, request, flash, session
from datetime import datetime, date, timedelta
import bcrypt, random, threading, time
from . import auth_bp

# Importamos la conecion a la BD
from config.db_connection import get_db_connection
#importamos las plantillas de los correos
from config.email_templates import *

@auth_bp.route('/')
def auth_index():
    return redirect(url_for('auth.login'))

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
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        public_ip = request.form.get('public_ip')

        #Busca el usuario existente en la BD
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query="""
            SELECT
                u.id_usuario,
                u.nombre_completo,
                u.password_hash,
                u.id_rol,
                r.nombre as nombre_rol
            FROM
                usuarios u,
                roles r
            WHERE
                u.id_rol = r.id_rol
                AND u.username = %s
        """
        cur.execute(query, (username,))
        datos_usuarios = cur.fetchall()
        cur.close()
        conn.close()

        if datos_usuarios:
            hashed_password = datos_usuarios[0]['password_hash'].encode('utf-8')
            id_user_bd = datos_usuarios[0]['id_usuario']
            password_bytes = password.encode('utf-8')

            # Valida la contraseña
            if bcrypt.checkpw(password_bytes, hashed_password):
                id_rol_user = datos_usuarios[0]["id_rol"]

                #Guardar información en la tabla de sesiones
                conn = get_db_connection()
                cur = conn.cursor(dictionary=True)
                query_session = """
                    INSERT INTO 
                        sesiones (direccion_ip, id_usuario) 
                    VALUES 
                        (%s,%s)
                """
                cur.execute(query_session, (public_ip, id_user_bd))
                conn.commit()
                cur.close()
                conn.close()

                #Guardar el usuario en una sesión
                if 'remember_me' in request.form:
                    session['username_rem'] = username
                else:
                    session.pop('username_rem', None)

                #Redirecciona dependiendo del rol
                if id_rol_user == 1: #Administrador
                    return redirect(url_for('admin.inicio'))
                print("OK")


            else:
                mensaje = "Usuario y/o contraseña incorrectas"
                return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='danger'))
        else:
            mensaje = "Usuario y/o contraseña incorrectas"
            return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='danger'))
    
    mensaje = "Favor de introducir tus credenciales para inciar sesión"
    return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='danger'))


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

    #Validar que en el formulario traiga los datos requeridos
    if request.method == 'POST' and 'inpEmail' in request.form:
        inpEmail = request.form.get('inpEmail')

        #Busca el usuario existente en la BD
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query="""
            SELECT
                id_usuario,
                COUNT(*) AS NumeroUsuarios,
                nombre_completo
            FROM
                usuarios
            WHERE
                correo = %s
        """
        cur.execute(query, (inpEmail,))
        datos_usuarios = cur.fetchone()
        cur.close()
        conn.close()

        if datos_usuarios['NumeroUsuarios'] > 0:
            nombre_usuario = datos_usuarios['nombre_completo']
            id_usuario = datos_usuarios["id_usuario"]
            codigo_verificacion = ''.join(str(random.randint(0, 9)) for _ in range(6))
            descripcion_codigo = "Restablecimiento de contraseña por correo"

            #Registrar el la BD el código
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            query = """
                INSERT INTO
                    codigo_verificacion
                    (codigo_verificacion, descripcion, id_usuario)
                VALUES
                    (%s, %s, %s)
            """
            cur.execute(query, (codigo_verificacion, descripcion_codigo, id_usuario))
            conn.commit()
            cur.close()
            conn.close()

            asunto = f"Tu código de verificación para Autolavado"
            plantilla_correo = plantilla_enviar_codigo_verificacion(nombre_usuario, codigo_verificacion)
            enviar_correo(inpEmail, asunto, plantilla_correo)
            session['email_reset_psw'] = inpEmail

            return redirect(url_for('auth.verify_code'))

        else:
            mensaje = 'El correo electrónico que ingresaste no está asociado a ninguna cuenta. Por favor, verifica la dirección e inténtalo de nuevo.'
            return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))
    
    mensaje = 'Favor de introducir un correo electrónico válido'
    return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))


@auth_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    #Validar que el correo existe guardado en una variable de sesión
    email_reset_psw = session.get('email_reset_psw', None)
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
    return render_template('auth/verificar_codigo.html', 
                           mensaje=mensaje, 
                           tipo_mensaje=tipo_mensaje, 
                           correo_verificacion=email_reset_psw,
                           reenviar_codigo=reenviar_codigo)


@auth_bp.route('/frm-verify-code', methods=['GET', 'POST'])
def frm_verify_code():

    #Validar que el correo existe guardado en una variable de sesión
    email_reset_psw = session.get('email_reset_psw', None)
    if not email_reset_psw:
        mensaje = 'Favor de introducir un correo válido'
        return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))

    if request.method == 'POST' and 'inpCode' in request.form:
        inpCode = request.form.get('inpCode')

        #Verificar codigo en la BD
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT
                codigo_verificacion,
                fecha_registro
            FROM
                codigo_verificacion
            WHERE
                id_usuario = (SELECT id_usuario FROM usuarios WHERE correo = %s)
            AND
                estatus = 0
            ORDER BY id_codigo DESC
            LIMIT 1
        """
        cur.execute(query, (email_reset_psw,))
        datos_codigo = cur.fetchone()
        cur.close()
        conn.close()

        if datos_codigo:
            fecha = datetime.now()
            diez_minutos = timedelta(minutes=10)
            codigo_verificacion = datos_codigo["codigo_verificacion"]
            fecha_registro = datos_codigo["fecha_registro"]
            diferencia_minutos = fecha - fecha_registro

            if diferencia_minutos > diez_minutos:
                mensaje = 'El código de verificación ha caducado'
                return redirect(url_for('auth.verify_code', mensaje=mensaje, tipo_mensaje='danger', reenviar_codigo="SI"))
            else:
                if inpCode == codigo_verificacion:
                    return redirect(url_for('auth.change_password'))
                else:
                    mensaje = 'El código de verificación es incorrecto'
                    return redirect(url_for('auth.verify_code', mensaje=mensaje, tipo_mensaje='danger', reenviar_codigo="SI"))
        else:
            mensaje = 'El código de verificación es incorrecto'
            return redirect(url_for('auth.verify_code', mensaje=mensaje, tipo_mensaje='danger', reenviar_codigo="SI"))

    mensaje = 'El código de verificación es incorrecto'
    return redirect(url_for('auth.verify_code', mensaje=mensaje, tipo_mensaje='danger', reenviar_codigo="SI"))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():

    #Validar que el correo existe guardado en una variable de sesión
    email_reset_psw = session.get('email_reset_psw', None)
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
    return render_template('auth/cambiar_contrasenia.html', 
                           mensaje=mensaje, 
                           tipo_mensaje=tipo_mensaje)


@auth_bp.route('/frm-change-password', methods=['GET', 'POST'])
def frm_change_password():

    #Validar que el correo existe guardado en una variable de sesión
    email_reset_psw = session.get('email_reset_psw', None)
    if not email_reset_psw:
        mensaje = 'Favor de introducir un correo válido'
        return redirect(url_for('auth.reset_password', mensaje=mensaje, tipo_mensaje='danger'))

    if request.method == 'POST' and 'inpPsw1' in request.form and 'inpPsw2' in request.form:
        inpPsw1 = request.form.get('inpPsw1')
        inpPsw2 = request.form.get('inpPsw2')
        fecha = datetime.now()
        fecha_actual = fecha.strftime('%Y-%m-%d %H:%M:%S')

        if inpPsw1 != inpPsw2:
            mensaje = 'Las contraseñas no coinciden'
            return redirect(url_for('auth.change_password', mensaje=mensaje, tipo_mensaje='danger'))
        
        password = inpPsw1.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        #Verificar codigo en la BD
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        query = """
            UPDATE 
                usuarios
            SET
                password_hash = %s, fecha_cambio_psw = %s
            WHERE
                correo = %s
        """
        cur.execute(query, (hashed_password, fecha_actual, email_reset_psw))

        #Consultar usuario en la BD
        query_consulta = """
            SELECT
                nombre_completo
            FROM
                usuarios
            WHERE
                correo = %s
        """
        cur.execute(query_consulta, (email_reset_psw,))
        datos_usuario = cur.fetchone()
        nombre_usuario = datos_usuario["nombre_completo"]
        conn.commit()
        cur.close()
        conn.close()


        session.pop('email_reset_psw', None)
        asunto = f"Contraseña actualizada"
        plantilla_correo = plantilla_cambio_password(nombre_usuario)
        enviar_correo(email_reset_psw, asunto, plantilla_correo)

        mensaje = "La contraseña fue cambiado correctamente, inicie sesión"
        return redirect(url_for('auth.login', mensaje=mensaje, tipo_mensaje='success'))
        
    mensaje = 'Las contraseñas no coinciden'
    return redirect(url_for('auth.change_password', mensaje=mensaje, tipo_mensaje='danger'))