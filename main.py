import requests
from bs4 import BeautifulSoup
import psycopg2

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='pampaPrueba',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

# Crear tablas
cur.execute("""
CREATE TABLE IF NOT EXISTS colonia (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    descripcion TEXT,
    ubicacion VARCHAR(255)
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS colonia_imagen (
    id SERIAL PRIMARY KEY,
    colonia_id INTEGER REFERENCES colonia(id),
    imagen BYTEA
)
""")
conn.commit()

# URL ingresada por el usuario
page_url = input("Por favor, ingresa la URL de la página con las colonias: ")

# Obtener contenido de la página principal
response = requests.get(page_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Obtener el nombre del departamento
departamento_tag = soup.find('h1')
if departamento_tag and departamento_tag.find('a'):
    departamento = departamento_tag.find('a').text.strip()
else:
    print("No se pudo encontrar el nombre del departamento.")
    departamento = "Desconocido"

# Obtener la lista de colonias
colonias_header = soup.find('h2', string='Pueblos y Colonias')
if not colonias_header:
    print("No se pudo encontrar la lista de colonias.")
    colonias = []
else:
    colonias_list = colonias_header.find_next('p')
    colonias = colonias_list.find_all('a') if colonias_list else []

for colonia in colonias:
    nombre = colonia.text.strip()
    print(f"Procesando colonia: {nombre}")

    if 'href' in colonia.attrs:
        # Es un enlace, por lo tanto tiene una descripción
        colonia_url = colonia['href']
        colonia_response = requests.get(colonia_url)
        colonia_soup = BeautifulSoup(colonia_response.content, 'html.parser')

        nombre_colonia_tag = colonia_soup.find('h3')
        nombre_colonia = nombre_colonia_tag.text.strip() if nombre_colonia_tag else nombre
        print(f"Nombre de la colonia: {nombre_colonia}")

        descripcion_tag = colonia_soup.find('p')
        descripcion = descripcion_tag.text.strip() if descripcion_tag else None
        print(f"Descripción: {descripcion}")

        ubicacion = f"{departamento}, Santa Fe, Argentina"

        # Insertar colonia en la base de datos
        cur.execute("""
        INSERT INTO colonia (nombre, descripcion, ubicacion)
        VALUES (%s, %s, %s) RETURNING id
        """, (nombre_colonia, descripcion, ubicacion))
        colonia_id = cur.fetchone()[0]
        conn.commit()

    else:
        # No tiene descripción
        descripcion = None
        ubicacion = f"{departamento}, Santa Fe, Argentina"

        print(f"Colonia sin enlace: {nombre}")

        # Insertar colonia en la base de datos
        cur.execute("""
        INSERT INTO colonia (nombre, descripcion, ubicacion)
        VALUES (%s, %s, %s)
        """, (nombre, descripcion, ubicacion))
        conn.commit()

# Cerrar la conexión
cur.close()
conn.close()
