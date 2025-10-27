from flask import Flask, render_template
import sys

# Codificar UTF-8 en la consola
sys.stdout.reconfigure(encoding='utf-8')

# Importamos la conecion a la BD
from config.db_connection import get_db_connection
from modules.admin import admin_bp
from modules.client import client_bp
from modules.services import servicio_bp
from modules.citas import citas_bp
from modules.auth import auth_bp
from modules.pagos import pagos_bp           # ✅ Módulo de pagos
from modules.promociones import promociones_bp   # ✅ Nuevo módulo de promociones


def create_app():
    app = Flask(__name__)
    
    # Registramos el Blueprint del módulo 'inicio de sesión'
    app.register_blueprint(auth_bp, url_prefix='/auth')
    # Registramos el Blueprint del módulo 'admin'
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # Registramos el Blueprint del módulo 'cliente'
    app.register_blueprint(client_bp, url_prefix='/client')
    # Registramos el Blueprint del módulo 'servicios'
    app.register_blueprint(servicio_bp, url_prefix='/services')
    # Registramos el Blueprint del módulo 'citas'
    app.register_blueprint(citas_bp, url_prefix='/citas')
    app.register_blueprint(pagos_bp, url_prefix='/admin/pagos')     # Módulo pagos
    app.register_blueprint(promociones_bp, url_prefix='/admin/promociones')  # 🟢 Nuevo módulo promociones

    app.secret_key = "app_autolavado"

    @app.route('/')
    def home():
        return render_template('auth/iniciar_sesion.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)