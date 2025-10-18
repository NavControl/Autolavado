from flask import Blueprint
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pagos_bp = Blueprint(
    'pagos_bp',
    __name__,
    url_prefix="/admin/pagos",
    template_folder=os.path.join('templates', 'pagos'),
    static_folder='static'
)

from . import routes
