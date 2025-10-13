from flask_mail import Mail

mail = Mail()

def init_mail(app):
    app.config.update(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME="tu_correo@gmail.com",
        MAIL_PASSWORD="tu_contraseña_o_app_password",
        MAIL_DEFAULT_SENDER=("Autolavado", "tu_correo@gmail.com")
    )
    mail.init_app(app)
