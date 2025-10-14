from flask import Blueprint
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

promociones_bp = Blueprint(
    'promociones_bp',
    __name__,
    url_prefix='/admin/promociones',
    template_folder='templates/promociones',
    static_folder='static'
)

from . import routes
