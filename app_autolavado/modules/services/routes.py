from flask import render_template
from . import servicio_bp

@servicio_bp.route('/')
def servicio_inicio():

    return render_template('servicios/servicios.html')

@servicio_bp.route('/registrar')
def registrar():

    return render_template('cliente/agregar_clientes.html')