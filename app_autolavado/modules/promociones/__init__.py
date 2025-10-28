from flask import Blueprint

promociones_bp = Blueprint(
    'promociones',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes
