from flask import render_template, request, redirect, url_for, flash, jsonify
from config.db_connection import get_db_connection
from . import promociones_bp


# ==========================
# LISTAR TODAS LAS PROMOCIONES
# ==========================
@promociones_bp.route('/')
def lista_promociones():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM promociones ORDER BY fecha_creacion DESC")
        promociones = cur.fetchall()
        cur.close()
        conn.close()
        # 🔹 Ruta completa del template dentro del módulo
        return render_template('promociones/promociones.html', promociones=promociones)
    except Exception as e:
        flash(f"Error al cargar las promociones: {str(e)}", "danger")
        return render_template('promociones/promociones.html', promociones=[])


# ==========================
# AGREGAR NUEVA PROMOCIÓN
# ==========================
@promociones_bp.route('/agregar', methods=['GET', 'POST'])
def agregar_promocion():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        codigo = request.form.get('codigo')
        descuento = request.form.get('descuento')
        descripcion = request.form.get('descripcion')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        estado = request.form.get('estado')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO promociones (nombre, codigo, descuento, descripcion, fecha_inicio, fecha_fin, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre, codigo, descuento, descripcion, fecha_inicio, fecha_fin, estado))
            conn.commit()
            cur.close()
            conn.close()
            flash('Promoción agregada correctamente.', 'success')
            return redirect(url_for('promociones.lista_promociones'))
        except Exception as e:
            flash(f'Error al agregar promoción: {str(e)}', 'danger')
            return redirect(url_for('promociones.agregar_promocion'))

    # 🔹 Ruta correcta del template
    return render_template('promociones/agregar.html')


# ==========================
# EDITAR PROMOCIÓN EXISTENTE
# ==========================
@promociones_bp.route('/editar/<int:id_promocion>', methods=['GET', 'POST'])
def editar_promocion(id_promocion):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        codigo = request.form.get('codigo')
        descuento = request.form.get('descuento')
        descripcion = request.form.get('descripcion')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        estado = request.form.get('estado')

        try:
            cur.execute("""
                UPDATE promociones
                SET nombre=%s, codigo=%s, descuento=%s, descripcion=%s,
                    fecha_inicio=%s, fecha_fin=%s, estado=%s
                WHERE id_promocion=%s
            """, (nombre, codigo, descuento, descripcion, fecha_inicio, fecha_fin, estado, id_promocion))
            conn.commit()
            flash('Promoción actualizada correctamente.', 'success')
        except Exception as e:
            flash(f'Error al actualizar promoción: {str(e)}', 'danger')

        cur.close()
        conn.close()
        return redirect(url_for('promociones.lista_promociones'))

    cur.execute("SELECT * FROM promociones WHERE id_promocion = %s", (id_promocion,))
    promo = cur.fetchone()
    cur.close()
    conn.close()

    # 🔹 Ruta correcta del template
    return render_template('promociones/editar.html', promo=promo)


# ==========================
# ELIMINAR PROMOCIÓN
# ==========================
@promociones_bp.route('/eliminar/<int:id>', methods=['DELETE'])
def eliminar_promocion(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM promociones WHERE id_promocion = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
