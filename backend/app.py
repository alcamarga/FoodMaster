import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config
from models.database import db

# 1. IMPORTAR MODELOS
from models.usuario import Usuario
from models.insumo import Insumo
from models.producto import Producto
from models.receta import Receta
from models.mesa import Mesa
from models.comanda import Comanda
from models.grupo_producto import GrupoProducto

# 2. IMPORTAR RUTAS
from routes.pedido_routes import pedidos_blueprint
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp
from routes.mesa_routes import mesa_bp
from routes.grupo_producto_routes import grupo_producto_bp, verificar_esquema_grupo, sembrar_grupos
from routes.caja_routes import caja_bp
from routes.delivery_routes import delivery_bp

app = Flask(__name__)
app.config.from_object(Config)

# Español: servir archivos estáticos (imágenes subidas) | English: serve static files (uploaded images)
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

@app.route('/static/uploads/<path:filename>')
def servir_imagen(filename):
    return send_from_directory(os.path.join(STATIC_FOLDER, 'uploads'), filename)

# Español: configuración de CORS — orígenes desde Config (por defecto '*' para Azure) | English: CORS config — origins from Config (default '*' for Azure)
cors_origins = app.config.get('CORS_ORIGINS', '*')
if cors_origins != '*':
    # Español: si es una lista separada por comas, conviértela | English: if comma-separated list, parse it
    cors_origins = [o.strip() for o in cors_origins.split(',')]

CORS(app, resources={r"/api/*": {
    "origins": cors_origins,
    "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
    "expose_headers": ["Content-Type", "Authorization"]
}}, supports_credentials=True)

db.init_app(app)

# Registramos los blueprints
app.register_blueprint(pedidos_blueprint, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(mesa_bp, url_prefix='/api')
app.register_blueprint(grupo_producto_bp, url_prefix='/api')
app.register_blueprint(caja_bp, url_prefix='/api')
app.register_blueprint(delivery_bp, url_prefix='/api')

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
        
        # 2. Verificar esquema y sembrar grupos por defecto | Verify schema and seed default groups
        verificar_esquema_grupo()
        sembrar_grupos()
        
        # 3. Crear Admin si no existe
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

        # Verificar esquema y migrar columnas faltantes | Verify schema and migrate missing columns
        verificar_esquema_grupo()

        # Español: migrar columnas de delivery en la tabla pedido | English: migrate delivery columns on pedido table
        from routes.delivery_routes import migrar_columnas_delivery
        migrar_columnas_delivery()

        # Sembrar grupos por defecto | Seed default groups
        sembrar_grupos()

    app.run(debug=True, host='0.0.0.0', port=5000)