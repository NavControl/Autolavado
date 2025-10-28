from flask import Blueprint

# Blueprint del módulo de pagos
pagos_bp = Blueprint(
    'pagos',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# Importa rutas para registrarlas
from . import routes  # noqa: F401
