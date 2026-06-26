# productos.py
# Módulo con todas las funciones CRUD y reportes del sistema de inventario.

import sqlite3
from database import crear_conexion  # Importamos la función que ya construimos


# ==============================================================================
# SECCIÓN 1 — REGISTRAR PRODUCTO (Create)
# ==============================================================================

def registrar_producto():
    """
    Solicita los datos de un nuevo producto al usuario y lo guarda en la BD.
    Valida que cantidad sea un número entero y precio un número decimal.
    """
    print("\n--- REGISTRAR NUEVO PRODUCTO ---")

    # --- Entrada de datos con validación de texto ---
    # .strip() elimina espacios accidentales al principio y al final 
    # El bucle while garantiza que el usuario no deje el campo vacío 

    nombre = ""
    while nombre == "":
        nombre = input("Nombre del producto: ").strip()
        if nombre == "":
            print("[AVISO] El nombre no puede estar vacío.")

    descripcion = input("Descripción (opcional, Enter para omitir): ").strip()

    categoria = input("Categoría (opcional, Enter para omitir): ").strip()

    # --- Entrada y validación de cantidad (debe ser entero positivo) ---
    cantidad = None
    while cantidad is None:
        try:
            cantidad = int(input("Cantidad disponible: "))
            if cantidad < 0:
                print("[AVISO] La cantidad no puede ser negativa.")
                cantidad = None
        except ValueError:
            # ValueError ocurre si el usuario escribe letras donde va un número
            print("[ERROR] Ingresá un número entero válido para la cantidad.")

    # --- Entrada y validación de precio (debe ser número positivo) ---
    precio = None
    while precio is None:
        try:
            precio = float(input("Precio unitario: "))
            if precio < 0:
                print("[AVISO] El precio no puede ser negativo.")
                precio = None
        except ValueError:
            print("[ERROR] Ingresá un número válido para el precio (ej: 150.99).")

    # --- Normalización del texto antes de guardar (Clase 3 y 4) ---
    # .title() pone en mayúscula la primera letra de cada palabra
    nombre     = nombre.title()
    categoria  = categoria.title()

    # --- Conexión e inserción en la base de datos ---
    conexion = crear_conexion()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Consulta parametrizada con '?' para prevenir inyección SQL (Clase 14)
        # NUNCA se deben concatenar strings directamente en consultas SQL
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, descripcion, cantidad, precio, categoria))

        conexion.commit()
        print(f"\n[OK] Producto '{nombre}' registrado con éxito.")

    except sqlite3.Error as e:
        # Si algo falla, rollback() deshace cualquier cambio parcial 
        conexion.rollback()
        print(f"[ERROR] No se pudo registrar el producto: {e}")

    finally:
        conexion.close()






# ==============================================================================
# SECCIÓN 2 — VISUALIZAR PRODUCTOS (Read)
# ==============================================================================

def visualizar_productos():
    """
    Recupera todos los productos de la base de datos y los muestra
    en formato de tabla por consola, ordenados por nombre.
    """
    conexion = crear_conexion()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # ORDER BY nombre ordena los resultados alfabéticamente
        cursor.execute("SELECT * FROM productos ORDER BY nombre")

        # fetchall() retorna una lista de tuplas con todos los registros 
        productos = cursor.fetchall()

        # Si la lista está vacía, avisamos y salimos de la función
        if len(productos) == 0:
            print("\n[AVISO] No hay productos registrados en el inventario.")
            return

        # --- Encabezado de la tabla ---
        print("\n" + "=" * 70)
        print(f"{'ID':<5} {'NOMBRE':<20} {'CATEGORÍA':<15} {'CANTIDAD':<10} {'PRECIO':<10} {'DESCRIPCIÓN'}")
        print("=" * 70)

        # --- Iteramos la lista de tuplas para mostrar cada fila ---
        # Cada 'producto' es una tupla: (id, nombre, descripcion, cantidad, precio, categoria)
        for producto in productos:
            id_p        = producto[0]
            nombre      = producto[1]
            descripcion = producto[2] if producto[2] else "-"  # Si es None, mostramos "-"
            cantidad    = producto[3]
            precio      = producto[4]
            categoria   = producto[5] if producto[5] else "-"

            # f-String con alineación de columnas para formato tabla
            # :<N significa alinear a la izquierda ocupando N caracteres
            print(f"{id_p:<5} {nombre:<20} {categoria:<15} {cantidad:<10} ${precio:<9.2f} {descripcion}")

        print("=" * 70)
        print(f"  Total de productos registrados: {len(productos)}")
        print("=" * 70)

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo obtener los productos: {e}")

    finally:
        conexion.close()        




# ==============================================================================
# SECCIÓN 3 — ACTUALIZAR PRODUCTO (Update)
# ==============================================================================

def actualizar_producto():
    """
    Busca un producto por su ID y permite modificar sus datos.
    El usuario elige qué campo actualizar. Usa consultas parametrizadas.
    """
    print("\n--- ACTUALIZAR PRODUCTO ---")

    # --- Pedimos el ID del producto a modificar ---
    id_producto = None
    while id_producto is None:
        try:
            id_producto = int(input("Ingresá el ID del producto a actualizar: "))
        except ValueError:
            print("[ERROR] El ID debe ser un número entero.")

    conexion = crear_conexion()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Primero verificamos que el producto con ese ID realmente existe
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()  # fetchone() trae solo un registro o None

        if producto is None:
            print(f"[AVISO] No se encontró ningún producto con ID {id_producto}.")
            return

        # Mostramos el producto encontrado antes de modificarlo
        print(f"\nProducto encontrado:")
        print(f"  Nombre    : {producto[1]}")
        print(f"  Descripción: {producto[2]}")
        print(f"  Cantidad  : {producto[3]}")
        print(f"  Precio    : ${producto[4]:.2f}")
        print(f"  Categoría : {producto[5]}")

        # --- Menú de campos a actualizar usando match ---
        print("\n¿Qué campo deseas actualizar?")
        print("  1. Nombre")
        print("  2. Descripción")
        print("  3. Cantidad")
        print("  4. Precio")
        print("  5. Categoría")

        opcion = input("\nElegí una opción (1-5): ").strip()

        # Usamos match para elegir qué campo y valor actualizar (Clase 4)
        campo = None
        nuevo_valor = None

        match opcion:
            case "1":
                campo = "nombre"
                nuevo_valor = input("Nuevo nombre: ").strip().title()
                while nuevo_valor == "":
                    print("[AVISO] El nombre no puede estar vacío.")
                    nuevo_valor = input("Nuevo nombre: ").strip().title()

            case "2":
                campo = "descripcion"
                nuevo_valor = input("Nueva descripción: ").strip()

            case "3":
                campo = "cantidad"
                nuevo_valor = None
                while nuevo_valor is None:
                    try:
                        nuevo_valor = int(input("Nueva cantidad: "))
                        if nuevo_valor < 0:
                            print("[AVISO] La cantidad no puede ser negativa.")
                            nuevo_valor = None
                    except ValueError:
                        print("[ERROR] Ingresá un número entero válido.")

            case "4":
                campo = "precio"
                nuevo_valor = None
                while nuevo_valor is None:
                    try:
                        nuevo_valor = float(input("Nuevo precio: "))
                        if nuevo_valor < 0:
                            print("[AVISO] El precio no puede ser negativo.")
                            nuevo_valor = None
                    except ValueError:
                        print("[ERROR] Ingresá un número válido (ej: 150.99).")

            case "5":
                campo = "categoria"
                nuevo_valor = input("Nueva categoría: ").strip().title()

            case _:
                print("[ERROR] Opción no válida. Volvé al menú principal.")
                return

        # --- Ejecutamos el UPDATE con el campo elegido ---
        # Usamos f-string SOLO para el nombre del campo (no es input del usuario)
        # El valor sigue siendo parametrizado con '?' por seguridad 
        cursor.execute(
            f"UPDATE productos SET {campo} = ? WHERE id = ?",
            (nuevo_valor, id_producto)
        )

        conexion.commit()
        print(f"\n[OK] Campo '{campo}' actualizado correctamente.")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] No se pudo actualizar el producto: {e}")

    finally:
        conexion.close()


# ==============================================================================
# SECCIÓN 4 — ELIMINAR PRODUCTO (Delete)
# ==============================================================================

def eliminar_producto():
    """
    Busca un producto por su ID y lo elimina de la base de datos.
    Solicita confirmación explícita al usuario antes de ejecutar el DELETE.
    Esta confirmación es un requisito de seguridad obligatorio del TFI.
    """
    print("\n--- ELIMINAR PRODUCTO ---")

    # --- Pedimos el ID del producto a eliminar ---
    id_producto = None
    while id_producto is None:
        try:
            id_producto = int(input("Ingresá el ID del producto a eliminar: "))
        except ValueError:
            print("[ERROR] El ID debe ser un número entero.")

    conexion = crear_conexion()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Verificamos que el producto existe antes de intentar borrarlo
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
        producto = cursor.fetchone()

        if producto is None:
            print(f"[AVISO] No se encontró ningún producto con ID {id_producto}.")
            return

        # Mostramos los datos del producto que se va a eliminar
        print(f"\nEstás por eliminar el siguiente producto:")
        print(f"  ID        : {producto[0]}")
        print(f"  Nombre    : {producto[1]}")
        print(f"  Categoría : {producto[5] if producto[5] else '-'}")
        print(f"  Cantidad  : {producto[3]}")
        print(f"  Precio    : ${producto[4]:.2f}")

        # --- Confirmación obligatoria antes de eliminar ---
        # Normalizamos la respuesta con .strip().lower() para aceptar
        # "S", "s", "SI", "si", "Sí" como respuesta válida 
        print("\n¡ATENCIÓN! Esta acción no se puede deshacer.")
        confirmacion = input("¿Confirmás la eliminación? (s/n): ").strip().lower()

        if confirmacion not in ("s", "si", "sí"):
            print("[INFO] Eliminación cancelada por el usuario.")
            return

        # --- Ejecutamos el DELETE solo si el usuario confirmó ---
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
        print(f"\n[OK] Producto '{producto[1]}' (ID: {id_producto}) eliminado correctamente.")

    except sqlite3.Error as e:
        conexion.rollback()
        print(f"[ERROR] No se pudo eliminar el producto: {e}")

    finally:
        conexion.close()

# ==============================================================================
# SECCIÓN 5 — BUSCAR PRODUCTO (Search)
# ==============================================================================

def buscar_producto():
    """
    Permite buscar productos por tres criterios: ID, nombre o categoría.
    La búsqueda por nombre y categoría es parcial (no necesita ser exacta).
    """
    print("\n--- BUSCAR PRODUCTO ---")

    # --- Menú de criterios de búsqueda ---
    print("¿Cómo querés buscar?")
    print("  1. Por ID")
    print("  2. Por nombre")
    print("  3. Por categoría")

    opcion = input("\nElegí una opción (1-3): ").strip()

    conexion = crear_conexion()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()
        productos = []  # Lista vacía que vamos a llenar con los resultados

        match opcion:
            case "1":
                # Búsqueda exacta por ID numérico
                id_producto = None
                while id_producto is None:
                    try:
                        id_producto = int(input("Ingresá el ID a buscar: "))
                    except ValueError:
                        print("[ERROR] El ID debe ser un número entero.")

                cursor.execute(
                    "SELECT * FROM productos WHERE id = ?",
                    (id_producto,)
                )
                # fetchone() porque el ID es único, solo puede haber uno
                resultado = cursor.fetchone()
                if resultado:
                    productos.append(resultado)  # Lo agregamos a la lista 

            case "2":
                # Búsqueda parcial por nombre usando LIKE 
                # Los % son comodines de SQL: %texto% encuentra cualquier
                # cadena que CONTENGA ese texto en cualquier posición
                termino = input("Ingresá el nombre (o parte del nombre): ").strip()
                cursor.execute(
                    "SELECT * FROM productos WHERE nombre LIKE ?",
                    (f"%{termino}%",)
                )
                productos = cursor.fetchall()

            case "3":
                # Búsqueda parcial por categoría usando LIKE
                termino = input("Ingresá la categoría (o parte de la categoría): ").strip()
                cursor.execute(
                    "SELECT * FROM productos WHERE categoria LIKE ?",
                    (f"%{termino}%",)
                )
                productos = cursor.fetchall()

            case _:
                print("[ERROR] Opción no válida.")
                return

        # --- Mostramos los resultados ---
        if len(productos) == 0:
            print("\n[AVISO] No se encontraron productos con ese criterio.")
            return

        # Reutilizamos el mismo formato de tabla que visualizar_productos()
        print(f"\n{len(productos)} resultado(s) encontrado(s):")
        print("=" * 70)
        print(f"{'ID':<5} {'NOMBRE':<20} {'CATEGORÍA':<15} {'CANTIDAD':<10} {'PRECIO':<10} {'DESCRIPCIÓN'}")
        print("=" * 70)

        for producto in productos:
            id_p        = producto[0]
            nombre      = producto[1]
            descripcion = producto[2] if producto[2] else "-"
            cantidad    = producto[3]
            precio      = producto[4]
            categoria   = producto[5] if producto[5] else "-"

            print(f"{id_p:<5} {nombre:<20} {categoria:<15} {cantidad:<10} ${precio:<9.2f} {descripcion}")

        print("=" * 70)

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo realizar la búsqueda: {e}")

    finally:
        conexion.close()




# ==============================================================================
# SECCIÓN 6 — REPORTE DE BAJO STOCK (Report)
# ==============================================================================

def reporte_bajo_stock():
    """
    Solicita al usuario un límite numérico y lista todos los productos
    cuya cantidad sea igual o inferior a ese límite, ordenados de menor
    a mayor cantidad para identificar los más críticos primero.
    """
    print("\n--- REPORTE DE BAJO STOCK ---")

    # --- El límite es definido dinámicamente por el usuario (requisito del TFI) ---
    limite = None
    while limite is None:
        try:
            limite = int(input("Ingresá el límite de stock (ej: 5): "))
            if limite < 0:
                print("[AVISO] El límite no puede ser negativo.")
                limite = None
        except ValueError:
            print("[ERROR] Ingresá un número entero válido.")

    conexion = crear_conexion()
    if conexion is None:
        return

    try:
        cursor = conexion.cursor()

        # Filtramos con WHERE cantidad <= limite
        # ORDER BY cantidad ASC muestra primero los más críticos (menos stock)
        cursor.execute("""
            SELECT * FROM productos
            WHERE cantidad <= ?
            ORDER BY cantidad ASC
        """, (limite,))

        productos = cursor.fetchall()

        # --- Encabezado del reporte ---
        print(f"\n{'=' * 70}")
        print(f"  REPORTE: Productos con stock igual o inferior a {limite} unidades")
        print(f"{'=' * 70}")

        if len(productos) == 0:
            print(f"  [OK] No hay productos con stock igual o inferior a {limite}.")
            print(f"{'=' * 70}")
            return

        # Encabezado de columnas
        print(f"{'ID':<5} {'NOMBRE':<20} {'CATEGORÍA':<15} {'CANTIDAD':<10} {'PRECIO'}")
        print("-" * 70)

        # --- Acumulador para calcular el total de unidades en riesgo ---
        total_unidades = 0

        for producto in productos:
            id_p      = producto[0]
            nombre    = producto[1]
            cantidad  = producto[3]
            precio    = producto[4]
            categoria = producto[5] if producto[5] else "-"

            # Acumulamos la cantidad de cada producto en riesgo
            total_unidades += cantidad

            # Indicador visual para stock en cero
            alerta = " ⚠ SIN STOCK" if cantidad == 0 else ""

            print(f"{id_p:<5} {nombre:<20} {categoria:<15} {cantidad:<10} ${precio:<9.2f}{alerta}")

        # --- Resumen final del reporte ---
        print("-" * 70)
        print(f"  Productos en situación de bajo stock : {len(productos)}")
        print(f"  Total de unidades restantes en riesgo: {total_unidades}")
        print(f"{'=' * 70}")

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo generar el reporte: {e}")

    finally:
        conexion.close()

 # ==============================================================================
# FUNCIONES PARA LA VERSIÓN WEB (retornan datos, no imprimen)
# ==============================================================================

def obtener_todos():
    """Retorna lista de todos los productos ordenados por nombre."""
    conexion = crear_conexion()
    if conexion is None:
        return []
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY nombre")
        return cursor.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conexion.close()


def obtener_por_id(id_producto):
    """Retorna un producto por su ID o None si no existe."""
    conexion = crear_conexion()
    if conexion is None:
        return None
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
        return cursor.fetchone()
    except sqlite3.Error:
        return None
    finally:
        conexion.close()


def insertar_producto(nombre, descripcion, cantidad, precio, categoria):
    """Inserta un nuevo producto en la base de datos."""
    conexion = crear_conexion()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, descripcion, cantidad, precio, categoria))
        conexion.commit()
    except sqlite3.Error as e:
        conexion.rollback()
        raise e
    finally:
        conexion.close()


def actualizar_producto_web(id_producto, nombre, descripcion, cantidad, precio, categoria):
    """Actualiza todos los campos de un producto existente."""
    conexion = crear_conexion()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos
            SET nombre=?, descripcion=?, cantidad=?, precio=?, categoria=?
            WHERE id=?
        """, (nombre, descripcion, cantidad, precio, categoria, id_producto))
        conexion.commit()
    except sqlite3.Error as e:
        conexion.rollback()
        raise e
    finally:
        conexion.close()


def eliminar_producto_web(id_producto):
    """Elimina un producto por su ID."""
    conexion = crear_conexion()
    if conexion is None:
        return
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
    except sqlite3.Error as e:
        conexion.rollback()
        raise e
    finally:
        conexion.close()


def obtener_bajo_stock(limite):
    """Retorna productos con cantidad <= limite, ordenados por cantidad ASC."""
    conexion = crear_conexion()
    if conexion is None:
        return []
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT * FROM productos WHERE cantidad <= ?
            ORDER BY cantidad ASC
        """, (limite,))
        return cursor.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conexion.close()


def buscar_productos_web(termino):
    """Búsqueda parcial por nombre o categoría usando LIKE."""
    conexion = crear_conexion()
    if conexion is None:
        return []
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT * FROM productos
            WHERE nombre LIKE ? OR categoria LIKE ?
            ORDER BY nombre
        """, (f"%{termino}%", f"%{termino}%"))
        return cursor.fetchall()
    except sqlite3.Error:
        return []
    finally:
        conexion.close()       