from flask import Blueprint

#  Nombre unificado: services_bp
services_bp = Blueprint('services', __name__,
                        template_folder='templates',
                        static_folder='static')

from . import routes
