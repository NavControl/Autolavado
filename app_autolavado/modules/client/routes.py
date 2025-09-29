from flask import render_template
from . import cliente_bp

@cliente_bp.route('/')
def cliente_inicio():

    return render_template('cliente/clientes.html')

@cliente_bp.route('/registrar')
def registrar():

    return render_template('cliente/agregar_clientes.html')