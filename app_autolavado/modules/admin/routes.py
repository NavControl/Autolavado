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

# ========================= CLIENTES =========================
@admin_bp.route('/clientes')
@admin_required
def clientes():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    query = """
        SELECT 
            u.id_usuario,
            u.username,
            u.nombre_completo,
            u.correo,
            u.telefono,
            u.fecha_registro,
            c.id_cliente,
            c.folio,
            c.curp,
            c.rfc,
            c.fecha_nacimiento
        FROM 
            usuarios u
        LEFT JOIN 
            clientes c ON u.id_usuario = c.id_usuario
        WHERE 
            u.id_rol = 2
    """
    cur.execute(query)
    datos_clientes = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin/clientes.html', datos_clientes=datos_clientes)

@admin_bp.route('/eliminar-cliente', methods=["POST"])
@admin_required
def eliminar_cliente():
    try:
        data = request.json
        id_usuario = data.get('id_usuario')

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # 1. Primero, encontramos todas las tablas que tienen claves foráneas hacia usuarios
        query_find_fk = """
            SELECT 
                TABLE_NAME, 
                COLUMN_NAME,
                CONSTRAINT_NAME
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE 
                REFERENCED_TABLE_NAME = 'usuarios' 
                AND REFERENCED_COLUMN_NAME = 'id_usuario'
        """
        
        cur.execute(query_find_fk)
        tablas_referenciadas = cur.fetchall()
        
        print(f"Tablas que referencian usuarios: {[tabla['TABLE_NAME'] for tabla in tablas_referenciadas]}")

        # 2. Eliminamos registros en todas las tablas que referencian usuarios
        for tabla in tablas_referenciadas:
            try:
                query_delete = f"DELETE FROM {tabla['TABLE_NAME']} WHERE {tabla['COLUMN_NAME']} = %s"
                cur.execute(query_delete, (id_usuario,))
                print(f"Eliminados registros de {tabla['TABLE_NAME']} para usuario {id_usuario}")
            except Exception as e:
                print(f"Error eliminando de {tabla['TABLE_NAME']}: {e}")

        # 3. Eliminamos en la tabla clientes (si no estaba en la lista anterior)
        try:
            query_delete_cliente = "DELETE FROM clientes WHERE id_usuario = %s"
            cur.execute(query_delete_cliente, (id_usuario,))
            print(f"Eliminado registro de clientes para usuario {id_usuario}")
        except Exception as e:
            print(f"Error eliminando de clientes: {e}")

        # 4. Finalmente eliminamos en la tabla usuarios
        query_delete_usuario = "DELETE FROM usuarios WHERE id_usuario = %s"
        cur.execute(query_delete_usuario, (id_usuario,))
        print(f"Eliminado usuario {id_usuario}")

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Cliente eliminado correctamente"}), 200
        
    except Exception as e:
        # En caso de error, hacemos rollback
        if 'conn' in locals():
            conn.rollback()
            cur.close()
            conn.close()
        return jsonify({"message": "ERROR", "error": str(e)}), 500

@admin_bp.route('/agregar-cliente', methods=['POST'])
@admin_required
def agregar_cliente():
    if request.method == 'POST':
        # Recogemos los datos del formulario
        inpUsuario = request.form.get('inpUsuario')
        inpNombre = request.form.get('inpNombre')
        inpCorreo = request.form.get('inpCorreo')
        inpTelefono = request.form.get('inpTelefono')
        slcRol = 2  # Rol de cliente
        inpFolio = request.form.get('inpFolio')
        inpCURP = request.form.get('inpCURP')
        inpRFC = request.form.get('inpRFC')
        inpFechaNacimiento = request.form.get('inpFechaNacimiento')

        # Generamos una contraseña aleatoria
        longitud = 8
        caracteres = string.ascii_letters + string.digits 
        psw = ''.join(random.choices(caracteres, k=longitud))
        print("Contraseña generada:", psw)
        password = psw.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        try:
            # Insertamos en la tabla usuarios
            query_usuario = """
                INSERT INTO usuarios (username, password_hash, nombre_completo, correo, telefono, id_rol) 
                VALUES(%s, %s, %s, %s, %s, %s)
            """
            cur.execute(query_usuario, (inpUsuario, hashed_password, inpNombre, inpCorreo, inpTelefono, slcRol))
            id_usuario = cur.lastrowid

            # Insertamos en la tabla clientes
            query_cliente = """
                INSERT INTO clientes (curp, rfc, folio, fecha_nacimiento, id_usuario) 
                VALUES(%s, %s, %s, %s, %s)
            """
            cur.execute(query_cliente, (inpCURP, inpRFC, inpFolio, inpFechaNacimiento, id_usuario))

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

@admin_bp.route('/editar-cliente/<int:id_usuario>', methods=['GET', 'POST'])
@admin_required
def editar_cliente(id_usuario):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        inpUsuario = request.form.get('inpUsuario')
        inpNombre = request.form.get('inpNombre')
        inpCorreo = request.form.get('inpCorreo')
        inpTelefono = request.form.get('inpTelefono')
        inpFolio = request.form.get('inpFolio')
        inpCURP = request.form.get('inpCURP')
        inpRFC = request.form.get('inpRFC')
        inpFechaNacimiento = request.form.get('inpFechaNacimiento')

        try:
            # Actualizar tabla usuarios
            query_usuario = """
                UPDATE usuarios 
                SET username=%s, nombre_completo=%s, correo=%s, telefono=%s
                WHERE id_usuario=%s
            """
            cur.execute(query_usuario, (inpUsuario, inpNombre, inpCorreo, inpTelefono, id_usuario))

            # Verificar si ya existe en la tabla clientes
            cur.execute("SELECT * FROM clientes WHERE id_usuario = %s", (id_usuario,))
            cliente_existente = cur.fetchone()

            if cliente_existente:
                # Actualizar tabla clientes
                query_cliente = """
                    UPDATE clientes 
                    SET curp=%s, rfc=%s, folio=%s, fecha_nacimiento=%s
                    WHERE id_usuario=%s
                """
                cur.execute(query_cliente, (inpCURP, inpRFC, inpFolio, inpFechaNacimiento, id_usuario))
            else:
                # Insertar en tabla clientes
                query_cliente = """
                    INSERT INTO clientes (curp, rfc, folio, fecha_nacimiento, id_usuario) 
                    VALUES(%s, %s, %s, %s, %s)
                """
                cur.execute(query_cliente, (inpCURP, inpRFC, inpFolio, inpFechaNacimiento, id_usuario))

            conn.commit()
            cur.close()
            conn.close()

            flash('Cliente actualizado correctamente', 'success')
            return redirect(url_for('admin.clientes'))

        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            flash(f'Error al actualizar el cliente: {str(e)}', 'error')
            return redirect(url_for('admin.editar_cliente', id_usuario=id_usuario))

    # Si es GET → mostrar datos actuales
    query = """
        SELECT 
            u.*,
            c.id_cliente,
            c.folio,
            c.curp,
            c.rfc,
            c.fecha_nacimiento
        FROM usuarios u
        LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
        WHERE u.id_usuario = %s
    """
    cur.execute(query, (id_usuario,))
    cliente = cur.fetchone()

    cur.close()
    conn.close()

    if not cliente:
        flash('Cliente no encontrado', 'error')
        return redirect(url_for('admin.clientes'))

    return render_template("admin/editar_cliente.html", cliente=cliente)

@admin_bp.route('/obtener-cliente/<int:id_usuario>')
@admin_required
def obtener_cliente(id_usuario):
    try:
        print(f"🔍 Solicitando datos del cliente ID: {id_usuario}")
        
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                u.id_usuario,
                u.username,
                u.nombre_completo,
                u.correo,
                u.telefono,
                c.folio,
                c.curp,
                c.rfc,
                c.fecha_nacimiento
            FROM usuarios u
            LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
            WHERE u.id_usuario = %s
        """
        cur.execute(query, (id_usuario,))
        cliente = cur.fetchone()
        
        print(f"📊 Datos obtenidos: {cliente}")
        
        cur.close()
        conn.close()
        
        if not cliente:
            print("❌ Cliente no encontrado")
            return jsonify({"error": "Cliente no encontrado"}), 404
        
        # Convertir TODOS los objetos de fecha/datetime a string
        import datetime
        
        for key, value in cliente.items():
            if isinstance(value, (datetime.date, datetime.datetime)):
                cliente[key] = value.strftime('%Y-%m-%d')
            elif value is None:
                cliente[key] = None
        
        print("✅ Datos enviados correctamente")
        return jsonify(cliente)
        
    except Exception as e:
        print(f"❌ Error en obtener_cliente: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500