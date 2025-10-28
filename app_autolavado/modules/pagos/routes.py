from flask import (
    render_template, request, redirect, url_for,
    flash, jsonify, current_app, send_file
)
from datetime import datetime
from . import pagos_bp
from config.db_connection import get_db_connection
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# ============================================================
# LISTAR PAGOS
# ============================================================
@pagos_bp.route('/', methods=['GET'], endpoint='lista_pagos')
def lista_pagos():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.nombre_completo AS usuario_nombre
        FROM pagos p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.fecha_pago DESC
    """)
    pagos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('pagos/pagos_lista.html', pagos=pagos)


# ============================================================
# VER DETALLE DE PAGO
# ============================================================
@pagos_bp.route('/ver/<int:id_pago>', methods=['GET'], endpoint='ver_pago')
def ver_pago(id_pago):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.nombre_completo AS usuario_nombre
        FROM pagos p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE p.id_pago = %s
    """, (id_pago,))
    pago = cur.fetchone()
    cur.close()
    conn.close()

    if not pago:
        flash('Pago no encontrado.', 'danger')
        return redirect(url_for('pagos.lista_pagos'))

    return render_template('pagos/pagos_ver.html', pago=pago)


# ============================================================
# API: AUTOCOMPLETADO DE USUARIOS
# ============================================================
@pagos_bp.route('/api/usuarios', methods=['GET'], endpoint='api_usuarios')
def api_usuarios():
    q = request.args.get('q', '').strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id_usuario, nombre_completo
        FROM usuarios
        WHERE nombre_completo LIKE %s
        ORDER BY nombre_completo ASC
        LIMIT 15
    """, (f"%{q}%",))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)


# ============================================================
# API: SERVICIOS ACTIVOS
# ============================================================
@pagos_bp.route('/api/servicios', methods=['GET'], endpoint='api_servicios')
def api_servicios():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id_servicio AS id, nombre, precio
        FROM servicios
        WHERE activo = 1
        ORDER BY nombre ASC
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)


# ============================================================
# API: PAQUETES ACTIVOS
# ============================================================
@pagos_bp.route('/api/paquetes', methods=['GET'], endpoint='api_paquetes')
def api_paquetes():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id_paquete AS id, nombre, precio
        FROM paquetes
        WHERE activo = 1
        ORDER BY nombre ASC
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)


# ============================================================
# REGISTRAR PAGO
# ============================================================
@pagos_bp.route('/registrar', methods=['GET', 'POST'], endpoint='registrar_pago')
def registrar_pago():
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        metodo = request.form.get('metodo')
        codigo = request.form.get('codigo_referencia') or None
        descripcion = request.form.get('descripcion', '')
        tipo = request.form.get('tipo')
        id_item = request.form.get('id_item')

        if not id_usuario or not metodo or not tipo or not id_item:
            flash('Usuario, método y selección de servicio o paquete son obligatorios.', 'danger')
            return redirect(url_for('pagos.registrar_pago'))

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        try:
            # Obtener precio y nombre del servicio o paquete
            if tipo == 'servicio':
                cur.execute("SELECT precio, nombre FROM servicios WHERE id_servicio = %s AND activo = 1", (id_item,))
            else:
                cur.execute("SELECT precio, nombre FROM paquetes WHERE id_paquete = %s AND activo = 1", (id_item,))

            row = cur.fetchone()
            if not row:
                flash('No se pudo determinar el precio. Verifique la selección.', 'danger')
                cur.close()
                conn.close()
                return redirect(url_for('pagos.registrar_pago'))

            precio = float(row['precio'])
            nombre_item = row['nombre']
            estado = 'pagado' if metodo == 'efectivo' else 'pendiente'

            # Insertar el pago en la base de datos
            if tipo == 'servicio':
                cur.execute("""
                    INSERT INTO pagos (id_usuario, id_servicio, metodo, monto, codigo_referencia, estado, fecha_pago)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (id_usuario, id_item, metodo, precio, codigo, estado))
            else:
                cur.execute("""
                    INSERT INTO pagos (id_usuario, id_paquete, metodo, monto, codigo_referencia, estado, fecha_pago)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (id_usuario, id_item, metodo, precio, codigo, estado))

            conn.commit()
            id_pago = cur.lastrowid
            cur.close()
            conn.close()

            generar_recibo_pdf(id_pago, precio, metodo, descripcion, id_usuario, nombre_item)
            flash('Pago registrado correctamente.', 'success')
            return redirect(url_for('pagos.lista_pagos'))

        except Exception as e:
            current_app.logger.exception("Error al registrar pago")
            try:
                cur.close()
                conn.close()
            except Exception:
                pass
            flash(f'Error al registrar pago: {e}', 'danger')
            return redirect(url_for('pagos.registrar_pago'))

    return render_template('pagos/pagos_registrar.html')


# ============================================================
# EDITAR PAGO
# ============================================================
@pagos_bp.route('/editar/<int:id_pago>', methods=['GET', 'POST'], endpoint='editar_pago')
def editar_pago(id_pago):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            p.*, 
            u.nombre_completo AS usuario_nombre,
            COALESCE(s.precio, pa.precio) AS precio_servicio,
            COALESCE(s.nombre, pa.nombre) AS nombre_servicio
        FROM pagos p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        LEFT JOIN servicios s ON p.id_servicio = s.id_servicio
        LEFT JOIN paquetes pa ON p.id_paquete = pa.id_paquete
        WHERE p.id_pago = %s
    """, (id_pago,))
    pago = cur.fetchone()

    if not pago:
        cur.close()
        conn.close()
        flash('Pago no encontrado.', 'danger')
        return redirect(url_for('pagos.lista_pagos'))

    if request.method == 'POST':
        monto = request.form.get('monto')
        metodo = request.form.get('metodo')
        estado = request.form.get('estado')
        codigo = request.form.get('codigo_referencia', '')

        if not monto or not metodo or not estado:
            flash('Complete los campos obligatorios.', 'danger')
            return redirect(url_for('pagos.editar_pago', id_pago=id_pago))

        try:
            monto = float(monto)
            if monto <= 0:
                flash('El monto debe ser mayor a cero.', 'danger')
                return redirect(url_for('pagos.editar_pago', id_pago=id_pago))
        except ValueError:
            flash('Monto inválido.', 'danger')
            return redirect(url_for('pagos.editar_pago', id_pago=id_pago))

        try:
            cur.execute("""
                UPDATE pagos
                SET monto=%s, metodo=%s, estado=%s, codigo_referencia=%s
                WHERE id_pago=%s
            """, (monto, metodo, estado, codigo, id_pago))
            conn.commit()
            cur.close()
            conn.close()
            flash('Pago actualizado correctamente.', 'success')
            return redirect(url_for('pagos.lista_pagos'))
        except Exception as e:
            current_app.logger.exception("Error al editar pago")
            flash(f'Error al editar pago: {e}', 'danger')
            return redirect(url_for('pagos.editar_pago', id_pago=id_pago))

    cur.close()
    conn.close()
    return render_template('pagos/pagos_editar.html', pago=pago)


# ============================================================
# ELIMINAR PAGO
# ============================================================
@pagos_bp.route('/eliminar/<int:id_pago>', methods=['POST'], endpoint='eliminar_pago')
def eliminar_pago(id_pago):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pagos WHERE id_pago = %s", (id_pago,))
        conn.commit()
        cur.close()
        conn.close()
        flash('Pago eliminado correctamente.', 'success')
    except Exception as e:
        current_app.logger.exception("Error al eliminar pago")
        flash(f'Error al eliminar pago: {e}', 'danger')
    return redirect(url_for('pagos.lista_pagos'))


# ============================================================
# DESCARGAR RECIBO PDF
# ============================================================
@pagos_bp.route('/descargar/<int:id_pago>', methods=['GET'], endpoint='descargar_recibo')
def descargar_recibo(id_pago):
    carpeta = os.path.join(os.getcwd(), 'tickets')
    archivo = f"recibo_pago_{id_pago}.pdf"
    ruta_pdf = os.path.join(carpeta, archivo)

    if not os.path.exists(ruta_pdf):
        flash('El recibo no existe o fue eliminado.', 'warning')
        return redirect(url_for('pagos.lista_pagos'))

    return send_file(ruta_pdf, as_attachment=True)


# ============================================================
# GENERAR RECIBO PDF
# ============================================================
def generar_recibo_pdf(id_pago, monto, metodo, descripcion, id_usuario=None, item="N/A"):
    try:
        carpeta = os.path.join(os.getcwd(), 'tickets')
        os.makedirs(carpeta, exist_ok=True)
        ruta_pdf = os.path.join(carpeta, f"recibo_pago_{id_pago}.pdf")

        nombre_usuario = "Desconocido"
        if id_usuario:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT nombre_completo FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            row = cur.fetchone()
            if row:
                nombre_usuario = row["nombre_completo"]
            cur.close()
            conn.close()

        c = canvas.Canvas(ruta_pdf, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(50, 750, "Autolavado - Recibo de Pago")
        c.drawString(50, 730, f"ID de Pago: {id_pago}")
        c.drawString(50, 710, f"Cliente: {nombre_usuario}")
        c.drawString(50, 690, f"Servicio/Paquete: {item}")
        c.drawString(50, 670, f"Método: {metodo}")
        c.drawString(50, 650, f"Monto: ${monto:.2f}")
        c.drawString(50, 630, f"Descripción: {descripcion or '—'}")
        c.drawString(50, 610, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.save()
    except Exception as e:
        current_app.logger.warning(f"No se pudo generar el recibo PDF: {e}")
