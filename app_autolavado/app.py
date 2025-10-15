from flask import Flask, render_template
import sys

# --- Configuración de la consola UTF-8 ---
sys.stdout.reconfigure(encoding='utf-8')

# --- Conexión a la base de datos ---
from config.db_connection import get_db_connection

# --- Importamos los módulos ---
from modules.admin import admin_bp
from modules.client import cliente_bp
from modules.services import servicio_bp
from modules.auth import auth_bp
from modules.pagos import pagos_bp           # ✅ Módulo de pagos
from modules.promociones import promociones_bp   # ✅ Nuevo módulo de promociones

# --- Función fábrica de la aplicación ---
def create_app():
    app = Flask(__name__)

    # Clave secreta para sesiones y mensajes flash
    app.secret_key = "app_autolavado"

    # --- Registro de Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/auth')             # Login / registro
    app.register_blueprint(admin_bp, url_prefix='/admin')           # Panel de administrador
    app.register_blueprint(cliente_bp, url_prefix='/client')        # Módulo cliente
    app.register_blueprint(servicio_bp, url_prefix='/services')     # Servicios
    app.register_blueprint(pagos_bp, url_prefix='/admin/pagos')     # Módulo pagos
    app.register_blueprint(promociones_bp, url_prefix='/admin/promociones')  # 🟢 Nuevo módulo promociones

    # --- Ruta principal ---
    @app.route('/')
    def home():
        return render_template('index.html')

    return app


# --- Punto de entrada principal ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
