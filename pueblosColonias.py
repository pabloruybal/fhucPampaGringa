from flask import Flask, render_template, request, jsonify
from jinja2 import Environment, select_autoescape
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/pampaPrueba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def nl2br(value):
    return value.replace('\n', '<br>\n')

# Registro del filtro en Jinja2
app.jinja_env.filters['nl2br'] = nl2br

class Imagen(db.Model):
    __tablename__ = 'imagen'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    imagen = db.Column(db.LargeBinary)

class Departamento(db.Model):
    __tablename__ = 'departamento'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    imagen = db.Column(db.LargeBinary)

class Colonia(db.Model):
    __tablename__ = 'colonia'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'))

class ColoniaImagen(db.Model):
    __tablename__ = 'colonia_imagen'
    id = db.Column(db.Integer, primary_key=True)
    colonia_id = db.Column(db.Integer, db.ForeignKey('colonia.id'))
    imagen = db.Column(db.LargeBinary)

@app.route('/')
def index():
    imagen = Imagen.query.filter_by(id=1).first() # Mapa de Santa Fe
    imagen2 = Imagen.query.filter_by(id=3).first() # Lupa
    imagen3 = Imagen.query.filter_by(id=5).first() # Imagen de cabecera
    imagen4 = Imagen.query.filter_by(id=6).first() # Fondo
    imagen5 = Imagen.query.filter_by(id=7).first() # Fondo
    imagen_base64 = base64.b64encode(imagen.imagen).decode('utf-8') if imagen else None
    imagen2_base64 = base64.b64encode(imagen2.imagen).decode('utf-8') if imagen else None
    imagen3_base64 = base64.b64encode(imagen3.imagen).decode('utf-8') if imagen else None
    imagen4_base64 = base64.b64encode(imagen4.imagen).decode('utf-8') if imagen else None
    imagen5_base64 = base64.b64encode(imagen5.imagen).decode('utf-8') if imagen else None
    departamentos = Departamento.query.all()
    return render_template('index.html', imagen=imagen_base64, imagen2=imagen2_base64, imagen3=imagen3_base64, imagen4=imagen4_base64, imagen5=imagen5_base64, departamentos=departamentos)

@app.route('/buscar_colonias')
def buscar_colonias():
    return render_template('buscarColonias.html')

@app.route('/departamento/<int:departamento_id>')
def departamento(departamento_id):
    departamento = Departamento.query.filter_by(id=departamento_id).first()
    colonias = Colonia.query.filter_by(departamento_id=departamento_id).all()
    departamento_imagen = base64.b64encode(departamento.imagen).decode('utf-8') if departamento.imagen else None
    return render_template('departamento.html', departamento=departamento, colonias=colonias, departamento_imagen=departamento_imagen)

@app.route('/buscar_colonias_live')
def buscar_colonias_live():
    try:
        query = request.args.get('query', '')
        page = int(request.args.get('page', 1))
        per_page = 10
        
        pagination = Colonia.query.filter(Colonia.nombre.ilike(f'%{query}%')).paginate(page=page, per_page=per_page, error_out=False)
        colonias = pagination.items
        
        result = []
        for colonia in colonias:
            imagen = ColoniaImagen.query.filter_by(colonia_id=colonia.id).first()
            imagen_base64 = base64.b64encode(imagen.imagen).decode('utf-8') if imagen else None
            result.append({
                'id': colonia.id,
                'nombre': colonia.nombre,
                'descripcion': colonia.descripcion,
                'imagen': imagen_base64
            })
        return jsonify({'colonias': result})
    except Exception as e:
        app.logger.error(f"Error al buscar colonias: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/colonia/<int:colonia_id>')
def ver_colonia(colonia_id):
    colonia = Colonia.query.get_or_404(colonia_id)
    imagenes = ColoniaImagen.query.filter_by(colonia_id=colonia.id).all()
    imagenes_base64 = [base64.b64encode(imagen.imagen).decode('utf-8') for imagen in imagenes]
    return render_template('colonia.html', colonia=colonia, imagenes=imagenes_base64)

if __name__ == '__main__':
    app.run(debug=True)
