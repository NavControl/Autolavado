from flask import render_template, request, redirect, url_for, flash, jsonify
from config.db_connection import get_db_connection
from . import pagos_bp
import os
import smtplib
import traceback
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config.email_templates import plantilla_ticket_pago
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# ======================================================
# 📧 Configuración SMTP
# ======================================================
SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.starcode.com.mx")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "soporte@starcode.com.mx")
SMTP_PASS = os.getenv("SMTP_PASS", "HM#K?QN,SK")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Autolavado")

# ======================================================
# 📋 LISTAR PAGOS
# ======================================================
@pagos_bp.route('/')
def lista_pagos():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT 
            p.id_pago,
            u.nombre_completo AS cliente,
            s.nombre AS servicio,
            p.metodo,
            p.monto,
            p.estado,
            p.codigo_referencia,
            p.fecha_pago
        FROM pagos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        LEFT JOIN servicios s ON p.id_reserva = s.id_servicio
        ORDER BY p.id_pago DESC
    """)
    pagos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('lista_pagos.html', pagos=pagos)

# ======================================================
# 🔍 BÚSQUEDA DINÁMICA DE CLIENTES (AJAX)
# ======================================================
@pagos_bp.route('/buscar_cliente')
def buscar_cliente():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id_usuario AS id, nombre_completo AS nombre
        FROM usuarios
        WHERE nombre_completo LIKE %s
        LIMIT 10
    """, (f"%{query}%",))
    clientes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(clientes)

# ======================================================
# 💰 OBTENER PRECIO DE SERVICIO (AJAX)
# ======================================================
@pagos_bp.route('/precio_servicio')
def precio_servicio():
    id_reserva = request.args.get('id_reserva')
    if not id_reserva:
        return jsonify({"precio": 0})

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT precio FROM servicios WHERE id_servicio = %s", (id_reserva,))
    servicio = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({"precio": servicio['precio'] if servicio else 0})

# ======================================================
# 🔎 VALIDAR CÓDIGO PAYPAL (AJAX)
# ======================================================
@pagos_bp.route('/validar_codigo_paypal')
def validar_codigo_paypal():
    codigo = request.args.get('codigo', '').strip()
    if not codigo:
        return jsonify({"valido": False, "mensaje": "Código vacío."})

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS total FROM pagos WHERE codigo_referencia = %s", (codigo,))
    existe = cur.fetchone()['total'] > 0
    cur.close()
    conn.close()

    if existe:
        return jsonify({"valido": False, "mensaje": "⚠️ Este código ya fue usado."})
    return jsonify({"valido": True, "mensaje": "✅ Código disponible."})

# ======================================================
# 🧾 REGISTRAR NUEVO PAGO
# ======================================================
@pagos_bp.route('/nuevo', methods=['GET', 'POST'])
def registrar_pago():
    if request.method == 'POST':
        try:
            id_usuario = request.form.get('id_usuario')
            id_reserva = request.form.get('id_reserva')
            metodo = request.form.get('metodo')
            monto = request.form.get('monto')
            codigo_referencia = request.form.get('codigo_referencia', '').strip() or None
            estado = "pendiente"

            # Validaciones iniciales
            if not id_usuario or not id_reserva or not metodo or not monto:
                flash("Todos los campos son obligatorios.", "danger")
                return redirect(url_for('pagos_bp.registrar_pago'))

            monto = float(monto)
            if monto <= 0:
                flash("El monto debe ser mayor a 0.", "danger")
                return redirect(url_for('pagos_bp.registrar_pago'))

            # ⚠️ Obtener el precio real del servicio
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT precio FROM servicios WHERE id_servicio = %s", (id_reserva,))
            servicio = cur.fetchone()
            cur.close()
            conn.close()

            if not servicio:
                flash("El servicio seleccionado no existe.", "danger")
                return redirect(url_for('pagos_bp.registrar_pago'))

            precio_real = float(servicio['precio'])

            # ⚠️ Validar que el monto coincida si es PayPal
            if metodo == "paypal" and monto != precio_real:
                flash(f"El monto ingresado (${monto:.2f}) no coincide con el precio real del servicio (${precio_real:.2f}).", "danger")
                return redirect(url_for('pagos_bp.registrar_pago'))

            # ⚠️ Validar código PayPal obligatorio y único
            if metodo == "paypal" and not codigo_referencia:
                flash("Debe ingresar el código de referencia de PayPal.", "danger")
                return redirect(url_for('pagos_bp.registrar_pago'))

            if metodo == "paypal":
                conn = get_db_connection()
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id_pago FROM pagos WHERE codigo_referencia = %s", (codigo_referencia,))
                if cur.fetchone():
                    cur.close()
                    conn.close()
                    flash("El código PayPal ya fue registrado anteriormente.", "danger")
                    return redirect(url_for('pagos_bp.registrar_pago'))
                cur.close()
                conn.close()

            # ✅ Insertar el pago
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO pagos (id_reserva, id_usuario, metodo, monto, codigo_referencia, estado, fecha_pago)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (id_reserva, id_usuario, metodo, monto, codigo_referencia, estado))
            conn.commit()
            id_pago = cur.lastrowid
            cur.close()
            conn.close()

            # ✅ Enviar ticket
            enviar_ticket_email(id_pago)

            # ✅ Mensaje distinto según método
            if metodo == "paypal":
                flash("Pago con PayPal registrado y ticket enviado al cliente ✅", "success")
            else:
                flash("Pago en efectivo registrado correctamente ✅", "success")

            return redirect(url_for('pagos_bp.lista_pagos'))

        except Exception as e:
            print("❌ Error al registrar pago:", e)
            traceback.print_exc()
            flash("Error al registrar el pago.", "danger")

    # Cargar servicios
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_servicio AS id_reserva, nombre FROM servicios")
    reservas = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('registrar_pago.html', reservas=reservas)

# ======================================================
# ✏️ EDITAR PAGO
# ======================================================
@pagos_bp.route('/editar/<int:id_pago>', methods=['GET', 'POST'])
def editar_pago(id_pago):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            metodo = request.form['metodo']
            monto = request.form['monto']
            estado = request.form['estado']

            cur.execute("""
                UPDATE pagos SET metodo=%s, monto=%s, estado=%s WHERE id_pago=%s
            """, (metodo, monto, estado, id_pago))
            conn.commit()
            flash("Pago actualizado correctamente ✅", "success")
            return redirect(url_for('pagos_bp.lista_pagos'))
        except Exception as e:
            print("❌ Error al actualizar pago:", e)
            traceback.print_exc()
            flash("Error al actualizar el pago.", "danger")

    cur.execute("""
        SELECT p.*, u.nombre_completo AS cliente, s.nombre AS servicio
        FROM pagos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        LEFT JOIN servicios s ON p.id_reserva = s.id_servicio
        WHERE p.id_pago = %s
    """, (id_pago,))
    pago = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('editar_pago.html', pago=pago)

# ======================================================
# 🗑️ ELIMINAR PAGO
# ======================================================
@pagos_bp.route('/eliminar/<int:id_pago>', methods=['POST'])
def eliminar_pago(id_pago):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pagos WHERE id_pago=%s", (id_pago,))
        conn.commit()
        flash("Pago eliminado correctamente 🗑️", "success")
    except Exception as e:
        print("❌ Error al eliminar pago:", e)
        flash("Error al eliminar el pago.", "danger")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('pagos_bp.lista_pagos'))

# ======================================================
# 👁️ VER DETALLE DEL PAGO
# ======================================================
@pagos_bp.route('/ver/<int:id_pago>')
def ver_pago(id_pago):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.nombre_completo, u.correo, s.nombre AS servicio
        FROM pagos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        LEFT JOIN servicios s ON s.id_servicio = p.id_reserva
        WHERE p.id_pago = %s
    """, (id_pago,))
    pago = cur.fetchone()
    cur.close()
    conn.close()

    if not pago:
        flash("No se encontró el pago solicitado.", "danger")
        return redirect(url_for('pagos_bp.lista_pagos'))

    return render_template('ver_pago.html', pago=pago)

# ======================================================
# 💌 REENVIAR TICKET POR CORREO
# ======================================================
@pagos_bp.route('/reenviar_ticket/<int:id_pago>', methods=['POST'])
def reenviar_ticket(id_pago):
    try:
        enviar_ticket_email(id_pago)
        flash("Ticket reenviado correctamente al cliente 💌", "success")
    except Exception as e:
        print("❌ Error al reenviar ticket:", e)
        traceback.print_exc()
        flash("No se pudo reenviar el ticket.", "danger")

    return redirect(url_for('pagos_bp.ver_pago', id_pago=id_pago))

# ======================================================
# 📤 ENVIAR TICKET POR CORREO (PDF en memoria)
# ======================================================
def enviar_ticket_email(id_pago):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.correo, u.nombre_completo
        FROM pagos p
        JOIN usuarios u ON u.id_usuario = p.id_usuario
        WHERE p.id_pago = %s
    """, (id_pago,))
    data = cur.fetchone()
    cur.close()
    conn.close()

    html_body = plantilla_ticket_pago(
        nombre_usuario=data['nombre_completo'],
        id_pago=data['id_pago'],
        metodo_pago=data['metodo'],
        monto=f"{float(data['monto']):.2f}",
        fecha_pago=str(data['fecha_pago'] or "")
    )

    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 750, "Ticket de Pago - Autolavado")
    c.setFont("Helvetica", 11)
    c.drawString(72, 720, f"Cliente: {data['nombre_completo']}")
    c.drawString(72, 700, f"Método: {data['metodo']}")
    c.drawString(72, 680, f"Monto: ${float(data['monto']):.2f}")
    c.drawString(72, 660, f"Estado: {data['estado']}")
    if data.get("codigo_referencia"):
        c.drawString(72, 640, f"Referencia PayPal: {data['codigo_referencia']}")
    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    msg = MIMEMultipart()
    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
    msg['To'] = data['correo']
    msg['Subject'] = "Ticket de Pago - Autolavado"
    msg.attach(MIMEText(html_body, "html"))

    adj = MIMEApplication(pdf_buffer.read(), _subtype="pdf")
    adj.add_header('Content-Disposition', 'attachment', filename=f"ticket_{id_pago}.pdf")
    msg.attach(adj)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    try:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, [data['correo']], msg.as_string())
    finally:
        server.quit()
