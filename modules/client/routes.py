from flask import render_template, request, redirect, url_for, flash, session
from . import client_bp
from config.db_connection import get_db_connection

# Ruta principal del cliente (dashboard)
@client_bp.route('/inicio')
def cliente_inicio():

        
    return render_template('client/clientes.html')
