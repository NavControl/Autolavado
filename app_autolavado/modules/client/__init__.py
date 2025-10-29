from flask import Blueprint

# Crea un Blueprint
client_bp = Blueprint(
    'client',
    __name__,
    url_prefix='/client',
    template_folder='templates',
    static_folder='static'
)

# Importa las rutas desde el archivo routes.py para que se registren
from . import routes