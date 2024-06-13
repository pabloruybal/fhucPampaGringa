import os
import requests
from flask import Flask, render_template, redirect, url_for
import psycopg2
import base64
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='pampaPrueba',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

# Configuración del log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_image_as_bytea(url):
    """Fetch an image from the given URL and return it as a byte array."""
    try:
        image_response = requests.get(url)
        image_response.raise_for_status()  # Ensure we notice bad responses
        logging.info(f'Imagen descargada correctamente desde: {url}')
        return image_response.content
    except Exception as e:
        logging.error(f"Error fetching image from {url}: {e}")
        return None

def get_full_url(base_url, url):
    """Return full URL for a potentially relative URL."""
    return urljoin(base_url, url)

def process_colonia(nombre, colonia_url, departamento):
    logging.info(f"Procesando colonia: {nombre}")

    if colonia_url:
        try:
            logging.info(f'Obteniendo contenido de la colonia desde: {colonia_url}')
            colonia_response = requests.get(colonia_url)
            colonia_response.raise_for_status()  # Ensure we notice bad responses
            colonia_soup = BeautifulSoup(colonia_response.content, 'html.parser')

            nombre_colonia_tag = colonia_soup.find('h3')
            nombre_colonia = nombre_colonia_tag.text.strip() if nombre_colonia_tag else nombre
            logging.info(f"Nombre de la colonia: {nombre_colonia}")

            descripcion_tag = colonia_soup.find('p')
            descripcion = descripcion_tag.text.strip() if descripcion_tag else None
            logging.info(f"Descripción: {descripcion}")

            ubicacion = f"{departamento}, Santa Fe, Argentina"
            
            # Obtener imagen principal
            imagen_tag = colonia_soup.find('img')
            imagen_principal_url = get_full_url(colonia_url, imagen_tag['src']) if imagen_tag else None
            imagen_principal = fetch_image_as_bytea(imagen_principal_url) if imagen_principal_url else None
            logging.info(f"URL de la imagen principal: {imagen_principal_url}")
            logging.info(f"Imagen principal: {'Cargada' if imagen_principal else 'No disponible'}")

            # Insertar colonia en la base de datos
            cur.execute("""
            INSERT INTO colonia (nombre, descripcion, ubicacion)
            VALUES (%s, %s, %s) RETURNING id
            """, (nombre_colonia, descripcion, ubicacion))
            colonia_id = cur.fetchone()[0]
            conn.commit()
            logging.info(f"Colonia {nombre_colonia} insertada con ID {colonia_id}")

            # Insertar imagen principal
            if imagen_principal:
                cur.execute("""
                INSERT INTO colonia_imagen (colonia_id, imagen)
                VALUES (%s, %s)
                """, (colonia_id, imagen_principal))
                conn.commit()
                logging.info(f"Imagen principal de la colonia {nombre_colonia} insertada")

            # Insertar imágenes adicionales
            imagenes_adicionales = colonia_soup.find_all('img')[1:]
            for img in imagenes_adicionales:
                imagen_adicional_url = get_full_url(colonia_url, img['src'])
                imagen_adicional = fetch_image_as_bytea(imagen_adicional_url)
                if imagen_adicional:
                    cur.execute("""
                    INSERT INTO colonia_imagen (colonia_id, imagen)
                    VALUES (%s, %s)
                    """, (colonia_id, imagen_adicional))
                    logging.info(f"Imagen adicional insertada desde: {imagen_adicional_url}")
            conn.commit()
            logging.info(f"Imágenes adicionales de la colonia {nombre_colonia} insertadas")
        except Exception as e:
            logging.error(f"Error procesando la colonia {nombre}: {e}")
            conn.rollback()  # Revertir transacciones en caso de error
    else:
        # No tiene descripción ni imágenes
        descripcion = None
        ubicacion = f"Departamento {departamento}, Santa Fe, Argentina"

        logging.info(f"Colonia sin enlace: {nombre}")

        # Insertar colonia en la base de datos
        try:
            cur.execute("""
            INSERT INTO colonia (nombre, descripcion, ubicacion)
            VALUES (%s, %s, %s)
            """, (nombre, descripcion, ubicacion))
            conn.commit()
            logging.info(f"Colonia {nombre} insertada sin enlace")
        except Exception as e:
            logging.error(f"Error insertando la colonia {nombre} sin enlace: {e}")
            conn.rollback()  # Revertir transacciones en caso de error

def main(base_url):
    # Crear tablas si no existen
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

    # Obtener contenido de la página principal
    logging.info(f'Obteniendo contenido de la página principal: {base_url}')
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Obtener el nombre del departamento
    departamento_tag = soup.find('h1')
    if departamento_tag and departamento_tag.find('a'):
        departamento = departamento_tag.find('a').text.strip()
        logging.info(f'Nombre del departamento encontrado: {departamento}')
    else:
        logging.warning("No se pudo encontrar el nombre del departamento.")
        departamento = "Desconocido"

    # Obtener la lista de colonias
    colonias_header = soup.find('h2', string='Pueblos y Colonias')
    if not colonias_header:
        logging.warning("No se pudo encontrar la lista de colonias.")
        colonias = []
    else:
        colonias_list = colonias_header.find_next('p')
        colonias = colonias_list.find_all('a') if colonias_list else []
        logging.info(f'Número de colonias encontradas: {len(colonias)}')

    # Procesar cada colonia
    for colonia in colonias:
        nombre = colonia.text.strip()
        colonia_url = get_full_url(base_url, colonia['href']) if 'href' in colonia.attrs else None
        process_colonia(nombre, colonia_url, departamento)

if __name__ == "__main__":
    base_url = "https://www.fhuc.unl.edu.ar/portalgringo/crear/gringa/mapa_general_lopez.html"
    main(base_url)

    # Cerrar la conexión
    cur.close()
    conn.close()
    logging.info('Conexión a la base de datos cerrada')
