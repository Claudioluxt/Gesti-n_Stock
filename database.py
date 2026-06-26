# database.py
# Módulo encargado de la conexión y la inicialización de la base de datos.

import sqlite3  # Módulo nativo de Python - no necesita instalarse (Clase 13)

# Constante con el nombre del archivo de la base de datos.
# Usamos una variable global en MAYÚSCULAS por convención para indicar que es una constante.
NOMBRE_DB = "inventario.db"


def crear_conexion():
    """
    Crea y retorna una conexión al archivo de base de datos SQLite.
    Si el archivo 'inventario.db' no existe, SQLite lo crea automáticamente.
    
    Returns:
        conexion: objeto de conexión a la base de datos, o None si hay error.
    """
    try:
        conexion = sqlite3.connect(NOMBRE_DB)
        return conexion
    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        return None


def inicializar_db():
    """
    Crea la tabla 'productos' en la base de datos si todavía no existe.
    Esta función se llama UNA SOLA VEZ al arrancar el programa desde main.py.
    """
    conexion = crear_conexion()

    # Solo continuamos si la conexión fue exitosa
    if conexion is None:
        return

    try:
        # cursor es el objeto que nos permite ejecutar sentencias SQL
        cursor = conexion.cursor()

        # CREATE TABLE IF NOT EXISTS evita un error si la tabla ya fue creada antes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT    NOT NULL,
                descripcion TEXT,
                cantidad    INTEGER NOT NULL,
                precio      REAL    NOT NULL,
                categoria   TEXT
            )
        """)

        # commit() confirma y guarda los cambios en el archivo .db (Clase 14)
        conexion.commit()
        print("[OK] Base de datos inicializada correctamente.")

    except sqlite3.Error as e:
        print(f"[ERROR] No se pudo crear la tabla: {e}")

    finally:
        # finally se ejecuta SIEMPRE, haya error o no.
        # Es la forma correcta de asegurarse de cerrar la conexión.
        conexion.close()