from flask import render_template, request, redirect, url_for, flash
from config.db_connection import get_db_connection
from . import promociones_bp
import traceback


# ------------------------------------------------------------
# 📋 LISTAR CÓDIGOS DE DESCUENTO
# ------------------------------------------------------------
@promociones_bp.route('/')
def lista_codigos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM codigos_descuento ORDER BY id_codigo DESC")
        codigos = cur.fetchall()
    except Exception as e:
        print("❌ Error al listar códigos:", e)
        traceback.print_exc()
        flash("Error al cargar los códigos de descuento.", "danger")
        codigos = []
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return render_template('lista_codigos.html', codigos=codigos)


# ------------------------------------------------------------
# ➕ REGISTRAR NUEVO CÓDIGO
# ------------------------------------------------------------
@promociones_bp.route('/nuevo', methods=['GET', 'POST'])
def registrar_codigo():
    if request.method == 'POST':
        try:
            codigo = request.form['codigo']
            tipo = request.form['tipo']
            valor = request.form['valor']
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']
            estado = 'activo'

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO codigos_descuento 
                (codigo, tipo, valor, fecha_inicio, fecha_fin, estado)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (codigo, tipo, valor, fecha_inicio, fecha_fin, estado))
            conn.commit()

            flash(f"Código '{codigo}' registrado correctamente ✅", "success")
            return redirect(url_for('promociones_bp.lista_codigos'))

        except Exception as e:
            print("❌ Error al registrar código:", e)
            traceback.print_exc()
            flash("Hubo un error al registrar el código.", "danger")

        finally:
            if cur: cur.close()
            if conn: conn.close()

    return render_template('registrar_codigo.html')


# ------------------------------------------------------------
# ✏️ EDITAR CÓDIGO EXISTENTE
# ------------------------------------------------------------
@promociones_bp.route('/editar/<int:id_codigo>', methods=['GET', 'POST'])
def editar_codigo(id_codigo):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        if request.method == 'POST':
            codigo = request.form['codigo']
            tipo = request.form['tipo']
            valor = request.form['valor']
            fecha_inicio = request.form['fecha_inicio']
            fecha_fin = request.form['fecha_fin']
            estado = request.form['estado']

            cur.execute("""
                UPDATE codigos_descuento
                SET codigo=%s, tipo=%s, valor=%s, fecha_inicio=%s, fecha_fin=%s, estado=%s
                WHERE id_codigo=%s
            """, (codigo, tipo, valor, fecha_inicio, fecha_fin, estado, id_codigo))
            conn.commit()
            flash(f"Código '{codigo}' actualizado correctamente ✅", "success")
            return redirect(url_for('promociones_bp.lista_codigos'))

        # Si es solo una vista GET
        cur.execute("SELECT * FROM codigos_descuento WHERE id_codigo=%s", (id_codigo,))
        codigo = cur.fetchone()

        if not codigo:
            flash("Código no encontrado ⚠️", "warning")
            return redirect(url_for('promociones_bp.lista_codigos'))

        return render_template('editar_codigo.html', codigo=codigo)

    except Exception as e:
        print("❌ Error al editar código:", e)
        traceback.print_exc()
        flash("Error al editar el código.", "danger")

    finally:
        if cur: cur.close()
        if conn: conn.close()


# ------------------------------------------------------------
# 🗑️ ELIMINAR CÓDIGO
# ------------------------------------------------------------
@promociones_bp.route('/eliminar/<int:id_codigo>')
def eliminar_codigo(id_codigo):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM codigos_descuento WHERE id_codigo=%s", (id_codigo,))
        conn.commit()
        flash("Código eliminado correctamente 🗑️", "success")
    except Exception as e:
        print("❌ Error al eliminar código:", e)
        traceback.print_exc()
        flash("Hubo un error al eliminar el código.", "danger")
    finally:
        if cur: cur.close()
        if conn: conn.close()

    return redirect(url_for('promociones_bp.lista_codigos'))
