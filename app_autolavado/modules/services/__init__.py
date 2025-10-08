from flask import Blueprint

# Crea un Blueprint
servicio_bp = Blueprint('services', __name__, 
                    template_folder='templates',
                    static_folder='static')

# Importa las rutas desde el archivo routes.py para que se registren
from . import routes