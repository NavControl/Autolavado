from flask import Blueprint

usuarios_bp = Blueprint(
    'users', __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes
