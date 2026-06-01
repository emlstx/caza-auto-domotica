import os
from flask import Flask, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# 1. Cargar el archivo .env con tus credenciales de Neon Tech
load_dotenv()

app = Flask(__name__)

# 2. Configurar la URL de la base de datos (Si falla el .env, aquí tienes tu respaldo directo)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL',
                                                  'postgresql://neondb_owner:npg_E9PBj0XGSJci@ep-weathered-unit-ap0nmej0-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# 3. Definir el modelo de la base de datos
class Cuarto3D(db.Model):
    # Forzamos explícitamente el nombre de la tabla para evitar confusiones
    __tablename__ = 'cuarto3d'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Boolean, default=False)
    precio_total = db.Column(db.Float, default=0.0)
    detalles = db.Column(db.String(200), default='')


# 4. Crear las tablas de forma segura ANTES de hacer cualquier consulta
with app.app_context():
    db.create_all()  # Esto viaja a Neon y crea la tabla 'cuarto3d' si no existe

    # Comprobamos si la tabla está vacía para meter los primeros datos
    if Cuarto3D.query.count() == 0:
        cuartos_iniciales = [
            Cuarto3D(nombre='Sala Principal', estado=True, precio_total=1200.0, detalles='Automatización completa'),
            Cuarto3D(nombre='Cocina', estado=False, precio_total=800.0, detalles='Sensores de gas activos'),
            Cuarto3D(nombre='Recámara 1', estado=True, precio_total=950.0, detalles='Luces y clima'),
            Cuarto3D(nombre='Recámara 2', estado=False, precio_total=950.0, detalles='Luces y clima'),
            Cuarto3D(nombre='Baño', estado=False, precio_total=500.0, detalles='Sensor de humedad'),
            Cuarto3D(nombre='Garaje', estado=True, precio_total=1500.0, detalles='Puerta automática')
        ]
        db.session.add_all(cuartos_iniciales)
        db.session.commit()


# 5. Rutas de tu panel táctico
@app.route('/')
def home():
    cuartos = Cuarto3D.query.all()
    return render_template('index.html', cuartos=cuartos)


@app.route('/conmutar/<int:id>')
def conmutar(id):
    cuarto = Cuarto3D.query.get_or_404(id)
    cuarto.estado = not cuarto.estado
    db.session.commit()
    return jsonify({
        'id': cuarto.id,
        'estado': cuarto.estado,
        'precio_total': cuarto.precio_total
    })


if __name__ == '__main__':
    # Le pide al servidor en la nube el puerto que tenga libre; si no encuentra, usa el 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
