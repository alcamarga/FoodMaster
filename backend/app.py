import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models.database import db

# 1. IMPORTAR MODELOS
from models.usuario import Usuario
from models.insumo import Insumo
from models.producto import Producto
from models.receta import Receta

# 2. IMPORTAR RUTAS
from routes.pedido_routes import pedidos_blueprint
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de CORS temporalmente abierta para validación en Azure
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    "expose_headers": ["Content-Type", "Authorization"]
}}, supports_credentials=True)

db.init_app(app)

# Registramos los blueprints
app.register_blueprint(pedidos_blueprint, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')

@app.route('/')
def index():
    return "<h1>¡PizzaOS con Postgres Funcionando!</h1><p>Sistema Modular Activo</p>"

@app.route('/api/seed', methods=['GET'])
def trigger_seed():
    try:
        from werkzeug.security import generate_password_hash
        print("🚀 Iniciando Seed desde endpoint...")
        
        # 1. Crear tablas si no existen
        db.create_all()
        
        # 2. Crear Admin si no existe
        admin_email = 'admin@pizzeria.com'
        if not Usuario.query.filter_by(email=admin_email).first():
            admin = Usuario(
                nombre='Admin Azure',
                email=admin_email,
                contrasena_hash=generate_password_hash('admin123'),
                rol='admin'
            )
            db.session.add(admin)
            
        # 3. Productos básicos para prueba
        if not Producto.query.filter_by(nombre='Pizza Tradicional').first():
            p1 = Producto(nombre='Pizza Tradicional', descripcion='Clásica Azure', categoria='Pizza', precio_base=20000, precio_pequena=20000)
            db.session.add(p1)
            
        db.session.commit()
        return jsonify({"status": "success", "message": "¡Base de datos de Azure inicializada con éxito!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        # Crear todas las tablas que Flask "conoce" gracias a los imports de arriba
        print("🛠️ [DB] Creando tablas...")
        db.create_all()
        
        from werkzeug.security import generate_password_hash
        
        # Lógica del Administrador
        admin_email = 'admin@pizzeria.com'
        admin_existente = Usuario.query.filter_by(email=admin_email).first()
        
        if not admin_existente:
            nuevo_admin = Usuario(
                nombre='Administrador',
                email=admin_email,
                contrasena_hash=generate_password_hash('admin123'),
                rol='admin'
            )
            db.session.add(nuevo_admin)
            db.session.commit()
            print("✅ [DB] Usuario administrador creado: admin@pizzeria.com / admin123")
        else:
            admin_existente.contrasena_hash = generate_password_hash('admin123')
            db.session.commit()
            print("✅ [DB] Usuario administrador verificado.")

    app.run(debug=True, host='0.0.0.0', port=5000)