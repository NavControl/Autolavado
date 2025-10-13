from flask import render_template, request, redirect, url_for, flash, send_from_directory
from config.db_connection import get_db_connection
from . import pagos_bp
import os
import smtplib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from config.paypal_config import paypalrestsdk
from config.email_templates import plantilla_ticket_pago
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Carpeta de tickets PDF
TICKETS_DIR = os.path.join(os.getcwd(), "tickets")
os.makedirs(TICKETS_DIR, exist_ok=True)

# Config SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.starcode.com.mx")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "soporte@starcode.com.mx")
SMTP_PASS = os.getenv("SMTP_PASS", "HM#K?QN,SK")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Autolavado")

# ------------------------------------------------------------
# 📋 LISTAR PAGOS
# ------------------------------------------------------------
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
            p.transaccion_id,
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

# ------------------------------------------------------------
# 🧾 REGISTRAR NUEVO PAGO
# ------------------------------------------------------------
@pagos_bp.route('/nuevo', methods=['GET', 'POST'])
def registrar_pago():
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        id_reserva = request.form.get('id_reserva')
        metodo = request.form.get('metodo')
        monto = request.form.get('monto')
        estado = "pendiente"

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO pagos (id_reserva, id_usuario, metodo, monto, estado)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_reserva, id_usuario, metodo, monto, estado))
        conn.commit()
        id_pago = cur.lastrowid
        cur.close()
        conn.close()

        flash(f"Pago registrado correctamente ({metodo} - ${monto})", "success")

        if metodo.lower() == "efectivo":
            generar_ticket_pdf(id_pago)
            enviar_ticket_email(id_pago)
            flash("Ticket generado y enviado por correo.", "info")

        return redirect(url_for('pagos_bp.lista_pagos'))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id_usuario, nombre_completo FROM usuarios")
    usuarios = cur.fetchall()
    cur.execute("SELECT id_servicio AS id_reserva, nombre FROM servicios")
    reservas = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('registrar_pago.html', usuarios=usuarios, reservas=reservas)

# ------------------------------------------------------------
# 🧾 GENERAR TICKET PDF
# ------------------------------------------------------------
def generar_ticket_pdf(id_pago):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT p.*, u.nombre_completo
        FROM pagos p
        JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE p.id_pago = %s
    """, (id_pago,))
    data = cur.fetchone()
    cur.close()
    conn.close()

    path = os.path.join(TICKETS_DIR, f"ticket_{id_pago}.pdf")
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 750, "Ticket de Pago - Autolavado")
    c.setFont("Helvetica", 11)
    c.drawString(72, 720, f"Cliente: {data['nombre_completo']}")
    c.drawString(72, 700, f"Método: {data['metodo']}")
    c.drawString(72, 680, f"Monto: ${float(data['monto']):.2f}")
    c.drawString(72, 660, f"Estado: {data['estado']}")
    if data.get("transaccion_id"):
        c.drawString(72, 640, f"Transacción: {data['transaccion_id']}")
    c.showPage()
    c.save()
    return path

# ------------------------------------------------------------
# 📤 ENVIAR TICKET POR CORREO
# ------------------------------------------------------------
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

    pdf_path = os.path.join(TICKETS_DIR, f"ticket_{id_pago}.pdf")
    if not os.path.exists(pdf_path):
        generar_ticket_pdf(id_pago)

    msg = MIMEMultipart()
    msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
    msg['To'] = data['correo']
    msg['Subject'] = "Ticket de Pago - Autolavado"
    msg.attach(MIMEText(html_body, "html"))

    with open(pdf_path, "rb") as f:
        adj = MIMEApplication(f.read(), _subtype="pdf")
        adj.add_header('Content-Disposition', 'attachment', filename=f"ticket_{id_pago}.pdf")
        msg.attach(adj)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    try:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_FROM, [data['correo']], msg.as_string())
    finally:
        server.quit()
