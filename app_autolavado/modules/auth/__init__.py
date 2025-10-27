from flask import Blueprint

# Crea un Blueprint
auth_bp = Blueprint('auth', __name__, 
                    template_folder='templates',
                    static_folder='static')

# Importa las rutas desde el archivo routes.py para que se registren
from . import routes