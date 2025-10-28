from flask import Flask, render_template
import sys, os
from config.db_connection import get_db_connection
from modules.admin import admin_bp
from modules.client import client_bp
from modules.services import services_bp
from modules.citas import citas_bp
from modules.auth import auth_bp
from modules.pagos import pagos_bp
from modules.promociones import promociones_bp
from modules.usuarios import usuarios_bp


# Configuración UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Crear app Flask
def create_app():
    app = Flask(__name__)
    app.secret_key = "clave_segura_autolavado_2025"

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(citas_bp, url_prefix='/citas')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(pagos_bp, url_prefix='/pagos')
    app.register_blueprint(promociones_bp, url_prefix='/promociones')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')


    # Página principal → login
    @app.route('/')
    def home():
        return render_template('auth/iniciar_sesion.html')

    return app


# Ejecutar servidor
if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
