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