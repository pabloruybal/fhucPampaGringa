import os
from flask import Flask, render_template, redirect, url_for
import psycopg2
import base64

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

@app.route('/')
def index():
    # Obtener todas las imágenes de la base de datos junto con el nombre y la ubicación de la colonia
    cur.execute("""
        SELECT colonia_imagen.id, colonia.nombre, colonia.ubicacion, colonia_imagen.imagen 
        FROM colonia_imagen 
        INNER JOIN colonia ON colonia_imagen.colonia_id = colonia.id
        ORDER BY colonia.ubicacion
    """)
    imagenes = cur.fetchall()
    
    # Convertir las imágenes a base64 para mostrarlas en HTML
    imagenes_base64 = [(id, nombre, ubicacion, base64.b64encode(imagen.tobytes()).decode('utf-8')) for id, nombre, ubicacion, imagen in imagenes]
    
    # Agrupar las imágenes por ubicación
    imagenes_por_ubicacion = {}
    for id, nombre, ubicacion, imagen in imagenes_base64:
        if ubicacion not in imagenes_por_ubicacion:
            imagenes_por_ubicacion[ubicacion] = []
        imagenes_por_ubicacion[ubicacion].append((id, nombre, imagen))
    
    return render_template('fotosExtra.html', imagenes_por_ubicacion=imagenes_por_ubicacion)

@app.route('/delete/<int:imagen_id>')
def delete(imagen_id):
    # Eliminar imagen de la base de datos
    cur.execute("DELETE FROM colonia_imagen WHERE id = %s", (imagen_id,))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

# Cerrar la conexión al finalizar la aplicación
@app.teardown_appcontext
def close_db(error):
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
