# app.py
# Punto de entrada del servidor web Flask.
# Ejecutar con: python app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from database import inicializar_db
import productos as prod

# Creamos la aplicación Flask
app = Flask(__name__)

# SECRET_KEY es necesaria para que Flask pueda usar flash() (mensajes de éxito/error)
app.secret_key = "talento_tech_inventario_2026"


# ══════════════════════════════════════════════════════════════════════════════
# RUTA PRINCIPAL — Ver todos los productos
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Página principal: muestra todos los productos en una tabla."""
    productos = prod.obtener_todos()
    return render_template("index.html", productos=productos)


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRAR PRODUCTO
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    """
    GET  → muestra el formulario vacío.
    POST → procesa los datos del formulario y guarda el producto.
    """
    if request.method == "POST":
        nombre      = request.form.get("nombre", "").strip().title()
        descripcion = request.form.get("descripcion", "").strip()
        categoria   = request.form.get("categoria", "").strip().title()

        try:
            cantidad = int(request.form.get("cantidad", ""))
            precio   = float(request.form.get("precio", ""))

            if not nombre:
                flash("El nombre no puede estar vacío.", "danger")
                return redirect(url_for("registrar"))
            if cantidad < 0 or precio < 0:
                flash("Cantidad y precio deben ser valores positivos.", "danger")
                return redirect(url_for("registrar"))

            prod.insertar_producto(nombre, descripcion, cantidad, precio, categoria)
            flash(f"Producto '{nombre}' registrado con éxito.", "success")
            return redirect(url_for("index"))

        except ValueError:
            flash("Cantidad debe ser entero y precio debe ser número válido.", "danger")
            return redirect(url_for("registrar"))

    return render_template("registrar.html")


# ══════════════════════════════════════════════════════════════════════════════
# ACTUALIZAR PRODUCTO
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/actualizar/<int:id_producto>", methods=["GET", "POST"])
def actualizar(id_producto):
    """
    GET  → muestra el formulario con los datos actuales del producto.
    POST → guarda los cambios en la base de datos.
    """
    producto = prod.obtener_por_id(id_producto)

    if producto is None:
        flash(f"No se encontró el producto con ID {id_producto}.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        nombre      = request.form.get("nombre", "").strip().title()
        descripcion = request.form.get("descripcion", "").strip()
        categoria   = request.form.get("categoria", "").strip().title()

        try:
            cantidad = int(request.form.get("cantidad", ""))
            precio   = float(request.form.get("precio", ""))

            if not nombre:
                flash("El nombre no puede estar vacío.", "danger")
                return redirect(url_for("actualizar", id_producto=id_producto))
            if cantidad < 0 or precio < 0:
                flash("Cantidad y precio deben ser valores positivos.", "danger")
                return redirect(url_for("actualizar", id_producto=id_producto))

            prod.actualizar_producto_web(id_producto, nombre, descripcion, cantidad, precio, categoria)
            flash(f"Producto '{nombre}' actualizado con éxito.", "success")
            return redirect(url_for("index"))

        except ValueError:
            flash("Cantidad debe ser entero y precio debe ser número válido.", "danger")
            return redirect(url_for("actualizar", id_producto=id_producto))

    return render_template("actualizar.html", producto=producto)


# ══════════════════════════════════════════════════════════════════════════════
# ELIMINAR PRODUCTO
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/eliminar/<int:id_producto>", methods=["POST"])
def eliminar(id_producto):
    """
    Elimina un producto por su ID.
    Solo acepta POST para evitar eliminaciones accidentales por URL.
    La confirmación se maneja con un modal de Bootstrap en el HTML.
    """
    producto = prod.obtener_por_id(id_producto)

    if producto is None:
        flash(f"No se encontró el producto con ID {id_producto}.", "danger")
    else:
        prod.eliminar_producto_web(id_producto)
        flash(f"Producto '{producto[1]}' eliminado correctamente.", "success")

    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════════════════════
# REPORTE DE BAJO STOCK
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/bajo-stock", methods=["GET", "POST"])
def bajo_stock():
    """
    GET  → muestra el formulario para ingresar el límite.
    POST → genera el reporte con el límite ingresado.
    """
    productos_riesgo = []
    limite = None

    if request.method == "POST":
        try:
            limite = int(request.form.get("limite", ""))
            if limite < 0:
                flash("El límite debe ser un número positivo.", "danger")
            else:
                productos_riesgo = prod.obtener_bajo_stock(limite)
        except ValueError:
            flash("Ingresá un número entero válido como límite.", "danger")

    return render_template("bajo_stock.html", productos=productos_riesgo, limite=limite)


# ══════════════════════════════════════════════════════════════════════════════
# BÚSQUEDA
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/buscar")
def buscar():
    """Búsqueda por nombre o categoría usando parámetros de la URL."""
    termino = request.args.get("q", "").strip()
    resultados = prod.buscar_productos_web(termino) if termino else []
    return render_template("index.html", productos=resultados, busqueda=termino)


# ══════════════════════════════════════════════════════════════════════════════
# ARRANQUE DEL SERVIDOR
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    inicializar_db()                  # Crea la tabla si no existe
    app.run(debug=True)               # debug=True recarga el servidor al guardar