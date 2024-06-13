import psycopg2
from psycopg2 import sql, Error

# Parámetros de conexión
dbname = 'pampaPrueba'
user = 'postgres'
password = '1234'
host = 'localhost'
port = '5432'

# Depuración de los parámetros de conexión
print(f"Conectando a la base de datos '{dbname}' en el host '{host}:{port}' con el usuario '{user}'")

try:
    # Conexión a la base de datos PostgreSQL
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()

    # Identificar duplicados
    cur.execute("""
    WITH duplicated AS (
        SELECT id, 
        nombre, 
        descripcion, 
        ubicacion, 
        ROW_NUMBER() OVER (PARTITION BY nombre, descripcion, ubicacion ORDER BY id) as row_num
        FROM colonia
    )
    SELECT id
    FROM duplicated
    WHERE row_num > 1
    """)
    duplicated_ids = cur.fetchall()

    if duplicated_ids:
        duplicated_ids = [id[0] for id in duplicated_ids]

        # Eliminar registros relacionados en colonia_imagen
        cur.execute("""
        DELETE FROM colonia_imagen
        WHERE colonia_id = ANY(%s)
        """, (duplicated_ids,))

        # Eliminar duplicados en colonia
        cur.execute("""
        DELETE FROM colonia
        WHERE id = ANY(%s)
        """, (duplicated_ids,))

        conn.commit()
        print("Duplicados eliminados con éxito.")

    # Cerrar la conexión
    cur.close()
    conn.close()

except Error as e:
    print(f"Ocurrió un error al conectar o interactuar con la base de datos: {e}")
