# Importar librerias para envio de correo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, asunto, mensaje_html, smtp_server="mail.starcode.com.mx", smtp_port=587, 
                  email_user="soporte@starcode.com.mx", email_password="HM#K?QN,SK"):
    try:
        # Crear la conexión SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Habilitar TLS
        server.login(email_user, email_password)
        
        # Crear el mensaje
        mensaje = MIMEMultipart()
        mensaje['From'] = email_user
        mensaje['To'] = destinatario
        mensaje['Subject'] = asunto
        mensaje.attach(MIMEText(mensaje_html, "html"))
        
        # Enviar el correo
        server.sendmail(email_user, destinatario, mensaje.as_string())
        return {"status": "success", "message": f"Correo enviado a {destinatario}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        server.quit()

def plantilla_base(titulo, cuerpo_html):
    nombre_aplicacion = "Autolavado"

    contenido_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    width: 100%;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #f9f9f9;
                }}
                .header {{
                    text-align: center;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                    margin-bottom: 20px;
                }}
                .code-block {{
                    background-color: #f5dbd0;
                    padding: 15px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    letter-spacing: 5px;
                    border-radius: 5px;
                    margin: 20px 0;
                    color: #E46027;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="color: #E46027;">{titulo} - {nombre_aplicacion}</h2>
                </div>
                <div>
                    {cuerpo_html}
                </div>
                <div class="footer">
                    <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                </div>
            </div>
        </body>
        </html>
    """
    return contenido_html

def plantilla_enviar_codigo_verificacion(nombre_usuario, codigo_verificacion):
    nombre_aplicacion = "Autolavado"
    titulo = "Verificación de Cuenta"
    tiempo_validez_minutos = 30
    cuerpo_html = f"""
        <p>Hola {nombre_usuario},</p>
        <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en <strong>{nombre_aplicacion}</strong>.</p>
        <p>Tu código de verificación es:</p>
        <div class="code-block">
            {codigo_verificacion}
        </div>
        <p>Por favor, introduce este código en la página de restablecimiento de contraseña para continuar.</p>
        <p>Este código es válido por **{tiempo_validez_minutos} minutos**.</p>
        <p>Si no solicitaste este cambio, puedes ignorar este correo electrónico. Tu contraseña actual no se modificará a menos que uses este código.</p>
        <p>Gracias,</p>
        <p>El equipo de {nombre_aplicacion}</p>
    """
    return plantilla_base(titulo, cuerpo_html)


def plantilla_cambio_password(nombre_usuario):
    nombre_aplicacion = "Autolavado"
    titulo = "Contraseña actualizada"
    cuerpo_html = f"""
        <p>Hola {nombre_usuario},</p>
        <p>Solo queremos confirmarte que tu contraseña para <strong>{nombre_aplicacion}</strong> ha sido restablecida exitosamente.</p>
        <p>Si no fuiste tú quien realizó este cambio, por favor, ponte en contacto con nuestro equipo de soporte inmediatamente.</p>
        <p>Gracias,</p>
        <p>El equipo de {nombre_aplicacion}</p>
    """
    return plantilla_base(titulo, cuerpo_html)

def plantilla_ticket_pago(datos_pago):
    """
    Genera el HTML para el ticket de pago
    """
    try:
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Ticket de Pago - Autolavado</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .ticket {{ border: 2px solid #333; padding: 20px; max-width: 500px; margin: 0 auto; }}
                .header {{ text-align: center; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                .detalles {{ margin: 15px 0; }}
                .fila {{ display: flex; justify-content: space-between; margin: 8px 0; }}
                .total {{ font-weight: bold; border-top: 2px solid #333; padding-top: 10px; }}
                .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="ticket">
                <div class="header">
                    <h1>AUTOLAVADO</h1>
                    <h2>COMPROBANTE DE PAGO</h2>
                </div>
                
                <div class="detalles">
                    <div class="fila">
                        <span><strong>Cliente:</strong></span>
                        <span>{datos_pago.get('nombre_cliente', 'N/A')}</span>
                    </div>
                    <div class="fila">
                        <span><strong>Vehículo:</strong></span>
                        <span>{datos_pago.get('vehiculo', 'N/A')}</span>
                    </div>
                    <div class="fila">
                        <span><strong>Servicio:</strong></span>
                        <span>{datos_pago.get('servicio', 'N/A')}</span>
                    </div>
                    <div class="fila">
                        <span><strong>Fecha:</strong></span>
                        <span>{datos_pago.get('fecha', 'N/A')}</span>
                    </div>
                    <div class="fila">
                        <span><strong>Hora:</strong></span>
                        <span>{datos_pago.get('hora', 'N/A')}</span>
                    </div>
                </div>
                
                <div class="total">
                    <div class="fila">
                        <span><strong>TOTAL:</strong></span>
                        <span>${datos_pago.get('total', 0):.2f}</span>
                    </div>
                </div>
                
                <div class="footer">
                    <p>¡Gracias por su preferencia!</p>
                    <p>Tel: (123) 456-7890</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template
    except Exception as e:
        # Template de emergencia si hay error
        return f"""
        <html>
        <body>
            <h2>Ticket de Pago</h2>
            <p>Cliente: {datos_pago.get('nombre_cliente', 'N/A')}</p>
            <p>Servicio: {datos_pago.get('servicio', 'N/A')}</p>
            <p>Total: ${datos_pago.get('total', 0):.2f}</p>
        </body>
        </html>
        """
def plantilla_confirmacion_cita(datos_cita):
    """
    Genera el HTML para la confirmación de cita
    """
    try:
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Confirmación de Cita - Autolavado</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    margin: 0;
                    padding: 0;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .header {{ 
                    text-align: center; 
                    padding: 20px 0;
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .detalles {{ 
                    margin: 25px 0; 
                    border: 1px solid #eaeaea;
                    border-radius: 8px;
                    overflow: hidden;
                }}
                .fila {{ 
                    display: flex; 
                    justify-content: space-between; 
                    padding: 15px;
                    border-bottom: 1px solid #f1f3f4;
                }}
                .fila:last-child {{
                    border-bottom: none;
                }}
                .fila:nth-child(even) {{
                    background-color: #f8fafc;
                }}
                .total {{ 
                    font-weight: bold; 
                    border-top: 2px solid #3498db; 
                    padding-top: 15px;
                    margin-top: 20px;
                    background-color: #f0f8ff;
                }}
                .footer {{ 
                    text-align: center; 
                    margin-top: 30px; 
                    padding-top: 20px; 
                    border-top: 1px solid #eee; 
                    font-size: 14px; 
                    color: #777;
                }}
                .badge {{
                    display: inline-block;
                    padding: 5px 12px;
                    background: #27ae60;
                    color: white;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                }}
                .servicios-lista {{
                    list-style: none;
                    padding: 0;
                }}
                .servicios-lista li {{
                    padding: 8px 0;
                    border-bottom: 1px solid #f1f3f4;
                }}
                .servicios-lista li:last-child {{
                    border-bottom: none;
                }}
                .info-box {{
                    background: #e8f4fd;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">🚗 Autolavado</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px; opacity: 0.9;">Confirmación de Cita</p>
                </div>
                
                <div class="content">
                    <p>Hola <strong>{datos_cita.get('nombre_cliente', 'Cliente')}</strong>,</p>
                    <p>Tu cita ha sido agendada exitosamente. Aquí tienes los detalles:</p>
                    
                    <div class="detalles">
                        <div class="fila">
                            <span><strong>📅 Fecha:</strong></span>
                            <span>{datos_cita.get('fecha', 'N/A')}</span>
                        </div>
                        <div class="fila">
                            <span><strong>⏰ Hora:</strong></span>
                            <span>{datos_cita.get('hora', 'N/A')}</span>
                        </div>
                        <div class="fila">
                            <span><strong>🚙 Vehículo:</strong></span>
                            <span>{datos_cita.get('vehiculo', 'N/A')}</span>
                        </div>
                        <div class="fila">
                            <span><strong>⏱️ Duración estimada:</strong></span>
                            <span>{datos_cita.get('duracion', 'N/A')} minutos</span>
                        </div>
                        <div class="fila">
                            <span><strong>📋 Estado:</strong></span>
                            <span class="badge">{datos_cita.get('estado', 'Pendiente')}</span>
                        </div>
                    </div>

                    <div class="info-box">
                        <h4 style="margin-top: 0; color: #2c3e50;">📋 Servicios Agendados</h4>
                        <ul class="servicios-lista">
        """
        
        # Agregar servicios dinámicamente
        servicios = datos_cita.get('servicios', [])
        for servicio in servicios:
            html_template += f"""
                            <li>
                                <strong>{servicio.get('nombre', 'Servicio')}</strong>
                                <span style="float: right;">
                                    ${servicio.get('precio', 0):.2f} - {servicio.get('duracion', 0)} min
                                </span>
                            </li>
            """
        
        html_template += f"""
                        </ul>
                    </div>
                    
                    <div class="total">
                        <div class="fila">
                            <span><strong>💰 TOTAL:</strong></span>
                            <span style="font-size: 18px; color: #27ae60;">${datos_cita.get('total', 0):.2f}</span>
                        </div>
                    </div>
                    
                    <div class="info-box">
                        <h4 style="margin-top: 0; color: #2c3e50;">📍 Información Importante</h4>
                        <p>• Por favor llega 5 minutos antes de tu cita</p>
                        <p>• Trae tu vehículo limpio por dentro (retira objetos personales)</p>
                        <p>• Duración aproximada: {datos_cita.get('duracion', 'N/A')} minutos</p>
                        <p>• Cancelaciones con al menos 2 horas de anticipación</p>
                    </div>
                    
                    <p>Si necesitas modificar o cancelar tu cita, puedes hacerlo desde tu cuenta en nuestro sistema.</p>
                    
                    <div class="footer">
                        <p>¡Gracias por confiar en nosotros!</p>
                        <p><strong>Autolavado</strong></p>
                        <p>📞 Teléfono: (123) 456-7890</p>
                        <p>🕒 Horario: Lunes a Sábado 8:00 AM - 6:00 PM</p>
                        <p style="font-size: 12px; color: #999; margin-top: 20px;">
                            Este es un correo automático, por favor no respondas a este mensaje.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template
    except Exception as e:
        # Template de emergencia si hay error
        return f"""
        <html>
        <body>
            <h2>Confirmación de Cita - Autolavado</h2>
            <p>Hola {datos_cita.get('nombre_cliente', 'Cliente')},</p>
            <p>Tu cita ha sido agendada exitosamente.</p>
            <p><strong>Fecha:</strong> {datos_cita.get('fecha', 'N/A')}</p>
            <p><strong>Hora:</strong> {datos_cita.get('hora', 'N/A')}</p>
            <p><strong>Servicios:</strong> {', '.join([s.get('nombre', '') for s in datos_cita.get('servicios', [])])}</p>
            <p><strong>Total:</strong> ${datos_cita.get('total', 0):.2f}</p>
            <p>¡Gracias por tu preferencia!</p>
        </body>
        </html>
        """