from flask import Flask, request, render_template, redirect, url_for, send_file, jsonify
import os
import psycopg2
import psycopg2.extras
import base64
from psycopg2 import extras
from werkzeug.utils import secure_filename
from io import BytesIO
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/imagenes'

# Configuración de la base de datos
DB_HOST = "localhost"
DB_NAME = "pampaPrueba"
DB_USER = "postgres"
DB_PASS = "1234"

# Configuración de la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname='pampaPrueba',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

# Función para obtener la conexión a la base de datos
def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Ruta para mostrar el índice de secciones con botones
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para mostrar el formulario de subir colonia
# @app.route('/subir_colonia')
# def subir_colonia_form():
#     return render_template('subir_colonia.html')

# # Ruta para manejar la subida de la colonia
# @app.route('/subir_colonia', methods=['POST'])
# def subir_colonia():
#     nombre = request.form['nombre']
#     descripcion = request.form['descripcion']
#     ubicacion = request.form['ubicacion']
#     departamento = ubicacion.split(',')[1]  # Asume que la ubicación está en el formato 'Ciudad, Departamento'
#     imagenes = request.files.getlist('imagenes')

#     conn = get_db_connection()
#     cur = conn.cursor()

#     # Insertar los datos de la colonia en la tabla 'colonia'
#     cur.execute("INSERT INTO colonia (nombre, descripcion, ubicacion) VALUES (%s, %s, %s) RETURNING id",
#                 (nombre, descripcion, ubicacion))
#     colonia_id = cur.fetchone()[0]

#     # Guardar las imágenes en la tabla 'colonia_imagen'
#     if imagenes and imagenes[0].filename != '':
#         for img in imagenes:
#             nombre_imagen = secure_filename(img.filename)
#             img.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))
#             with open(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen), 'rb') as file:
#                 img_data = file.read()
#             cur.execute("INSERT INTO colonia_imagen (colonia_id, imagen) VALUES (%s, %s)",
#                         (colonia_id, img_data))

#     conn.commit()
#     cur.close()
#     conn.close()

#     return redirect(url_for('listar_colonias'))

# @app.route('/subir_colonias', methods=['POST'])
# def subir_colonias():
#     colonias = request.form.getlist('nombre')
#     descripciones = request.form.getlist('descripcion')
#     ubicaciones = request.form.getlist('ubicacion')
#     imagenes = request.files.getlist('imagenes')

#     conn = get_db_connection()
#     cur = conn.cursor()

#     for i in range(len(colonias)):
#         nombre = colonias[i]
#         descripcion = descripciones[i]
#         ubicacion = ubicaciones[i]

#         # Insertar los datos de la colonia en la tabla 'colonia'
#         cur.execute("INSERT INTO colonia (nombre, descripcion, ubicacion) VALUES (%s, %s, %s) RETURNING id",
#                     (nombre, descripcion, ubicacion))
#         colonia_id = cur.fetchone()[0]

#         # Guardar las imágenes en la tabla 'colonia_imagen'
#         for img in imagenes:
#             if img.filename != '':
#                 nombre_imagen = secure_filename(img.filename)
#                 img.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))
#                 with open(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen), 'rb') as file:
#                     img_data = file.read()
#                 cur.execute("INSERT INTO colonia_imagen (colonia_id, imagen) VALUES (%s, %s)",
#                             (colonia_id, img_data))

#     conn.commit()
#     cur.close()
#     conn.close()

#     return redirect(url_for('listar_colonias'))

# # Ruta para mostrar el listado de colonias y sus imágenes
# @app.route('/colonias')
# def listar_colonias():
#     conn = get_db_connection()
#     cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     cur.execute("""
#         SELECT c.id, c.nombre, c.descripcion, c.ubicacion, ci.imagen, ci.id as imagen_id
#         FROM colonia c
#         LEFT JOIN colonia_imagen ci ON c.id = ci.colonia_id
#         ORDER BY c.id ASC
#     """)
#     colonias = cur.fetchall()
#     cur.close()
#     conn.close()

#     # Agrupar las imágenes por colonia
#     colonias_dict = {}
#     for row in colonias:
#         colonia_id = row['id']
#         if colonia_id not in colonias_dict:
#             colonias_dict[colonia_id] = {
#                 'id': colonia_id,
#                 'nombre': row['nombre'],
#                 'descripcion': row['descripcion'],
#                 'ubicacion': row['ubicacion'],
#                 'imagenes': []
#             }
#         if row['imagen']:
#             colonias_dict[colonia_id]['imagenes'].append({'id': row['imagen_id'], 'imagen': row['imagen']})

#     return render_template('listar_colonias.html', colonias=colonias_dict.values())

@app.route('/obtener_imagen/<int:imagen_id>')
def obtener_imagen(imagen_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT imagen FROM colonia_imagen WHERE id = %s", (imagen_id,))
    imagen_data = cur.fetchone()[0]
    cur.close()
    conn.close()
    return send_file(BytesIO(imagen_data), mimetype='image/jpeg')  # Ajusta el mimetype según el tipo de imagen que estés almacenando

@app.route('/deletear')
def deletear():
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
    return redirect(url_for('deletear'))

@app.route('/editar_colonia/<int:colonia_id>', methods=['POST'])
def editar_colonia(colonia_id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    ubicacion = request.form['ubicacion']
    imagenes_a_eliminar = request.form.get('imagenes_a_eliminar')
    nuevas_imagenes = request.files.getlist('nuevas_imagenes')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Actualizar los detalles de la colonia
    cur.execute("UPDATE colonia SET nombre = %s, descripcion = %s, ubicacion = %s WHERE id = %s",
                (nombre, descripcion, ubicacion, colonia_id))
    
    # Eliminar las imágenes marcadas para eliminación
    if imagenes_a_eliminar:
        imagenes_a_eliminar = json.loads(imagenes_a_eliminar)
        for imagen_id in imagenes_a_eliminar:
            cur.execute("DELETE FROM colonia_imagen WHERE id = %s", (imagen_id,))
    
    # Subir nuevas imágenes
    if nuevas_imagenes and nuevas_imagenes[0].filename != '':
        for img in nuevas_imagenes:
            nombre_imagen = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen))
            with open(os.path.join(app.config['UPLOAD_FOLDER'], nombre_imagen), 'rb') as file:
                img_data = file.read()
            cur.execute("INSERT INTO colonia_imagen (colonia_id, imagen) VALUES (%s, %s)", (colonia_id, img_data))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return redirect(url_for('editar_colonia_form'))



@app.route('/editar_colonia_form')
def editar_colonia_form():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT * FROM colonia")
    colonias = cur.fetchall()
    
    # Agrupar colonias por ubicación y ordenarlas alfabéticamente
    colonias_por_ubicacion = {}
    for colonia in colonias:
        ubicacion = colonia['ubicacion']
        if ubicacion not in colonias_por_ubicacion:
            colonias_por_ubicacion[ubicacion] = []
        colonias_por_ubicacion[ubicacion].append(colonia)
    
    # Ordenar ubicaciones alfabéticamente
    ubicaciones_ordenadas = sorted(colonias_por_ubicacion.keys())
    
    # Ordenar colonias dentro de cada ubicación alfabéticamente
    for ubicacion in colonias_por_ubicacion:
        colonias_por_ubicacion[ubicacion].sort(key=lambda x: x['nombre'])
    
    # Enumerar las ubicaciones y las colonias
    ubicaciones_enumeradas = []
    for idx, ubicacion in enumerate(ubicaciones_ordenadas, start=1):
        colonias_enumeradas = [
            {"index": i+1, **colonia} for i, colonia in enumerate(colonias_por_ubicacion[ubicacion])
        ]
        ubicaciones_enumeradas.append({
            "index": idx,
            "ubicacion": ubicacion,
            "colonias": colonias_enumeradas
        })
    
    cur.close()
    conn.close()

    return render_template('editarColonia.html', ubicaciones_enumeradas=ubicaciones_enumeradas)

@app.route('/obtener_imagenes/<int:colonia_id>')
def obtener_imagenes(colonia_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id, imagen FROM colonia_imagen WHERE colonia_id = %s", (colonia_id,))
    imagenes = cur.fetchall()
    cur.close()
    conn.close()

    imagenes_base64 = [{'id': img['id'], 'imagen_base64': base64.b64encode(img['imagen']).decode('utf-8')} for img in imagenes]
    return jsonify({'imagenes': imagenes_base64})

@app.route('/eliminar_imagen/<int:imagen_id>', methods=['DELETE'])
def eliminar_imagen(imagen_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM colonia_imagen WHERE id = %s", (imagen_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/eliminar_imagenes', methods=['POST'])
def eliminar_imagenes():
    imagenes_a_eliminar = request.form.get('imagenes_a_eliminar')
    if imagenes_a_eliminar:
        imagenes_a_eliminar = json.loads(imagenes_a_eliminar)
        conn = get_db_connection()
        cur = conn.cursor()
        for imagen_id in imagenes_a_eliminar:
            cur.execute("DELETE FROM colonia_imagen WHERE id = %s", (imagen_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True}), 200
    return jsonify({'error': 'No hay imágenes para eliminar'}), 400

@app.route('/buscar_colonias', methods=['GET'])
def buscar_colonias():
    query = request.args.get('query', '')
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if query:
        cur.execute("SELECT c.id, c.nombre, c.descripcion, ci.imagen FROM colonia c LEFT JOIN colonia_imagen ci ON c.id = ci.colonia_id WHERE c.nombre ILIKE %s", ('%' + query + '%',))
    else:
        cur.execute("SELECT c.id, c.nombre, c.descripcion, ci.imagen FROM colonia c LEFT JOIN colonia_imagen ci ON c.id = ci.colonia_id")

    colonias = cur.fetchall()
    cur.close()
    conn.close()

    colonias_data = [{'id': colonia['id'], 'nombre': colonia['nombre'], 'descripcion': colonia['descripcion'], 'imagen': base64.b64encode(colonia['imagen']).decode('utf-8') if colonia['imagen'] else None} for colonia in colonias]

    return render_template('buscarColonias.html', colonias=colonias_data)

@app.route('/buscar_colonias_live', methods=['GET'])
def buscar_colonias_live():
    query = request.args.get('query', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if query:
        cur.execute("""
            SELECT c.id, c.nombre, c.descripcion, ci.imagen 
            FROM colonia c 
            LEFT JOIN colonia_imagen ci ON c.id = ci.colonia_id 
            WHERE c.nombre ILIKE %s
            LIMIT %s OFFSET %s
        """, ('%' + query + '%', per_page, offset))
    else:
        cur.execute("""
            SELECT c.id, c.nombre, c.descripcion, ci.imagen 
            FROM colonia c 
            LEFT JOIN colonia_imagen ci ON c.id = ci.colonia_id
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    colonias = cur.fetchall()
    cur.close()
    conn.close()

    colonias_data = [{'id': colonia['id'], 'nombre': colonia['nombre'], 'descripcion': colonia['descripcion'], 'imagen': base64.b64encode(colonia['imagen']).decode('utf-8') if colonia['imagen'] else None} for colonia in colonias]

    return jsonify({'colonias': colonias_data})


@app.route('/colonia/<int:colonia_id>', methods=['GET'])
def mostrar_colonia(colonia_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT c.id, c.nombre, c.descripcion, ci.imagen FROM colonia c LEFT JOIN colonia_imagen ci ON c.id = ci.colonia_id WHERE c.id = %s", (colonia_id,))
    colonia = cur.fetchone()
    
    if colonia:
        cur.execute("SELECT imagen FROM colonia_imagen WHERE colonia_id = %s", (colonia_id,))
        imagenes = cur.fetchall()
        cur.close()
        conn.close()
        
        colonia_data = {
            'id': colonia['id'],
            'nombre': colonia['nombre'],
            'descripcion': colonia['descripcion'],
            'imagenes': [base64.b64encode(imagen['imagen']).decode('utf-8') for imagen in imagenes if imagen['imagen']]
        }
        return render_template('colonia.html', colonia=colonia_data)
    else:
        cur.close()
        conn.close()
        return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
