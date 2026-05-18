from flask import Blueprint, request, jsonify
from models.database import db
from models.usuario import Usuario
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime

# Definimos el Blueprint que el app.py está intentando importar
auth_bp = Blueprint('auth', __name__)

# Esta clave debe ser la misma que usas en el resto de la app
JWT_SECRET = "pizzeria_secret_key_fixed_2026_super_safe"

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    # Robustez total: Intentamos JSON forzado, luego Formulario
    datos = request.get_json(force=True, silent=True)
    if not datos:
        datos = request.form.to_dict()

    if not datos:
        return jsonify({'error': 'No se enviaron datos válidos en la petición'}), 400

    # Intentamos obtener el email de varias formas comunes
    email = str(datos.get('email') or datos.get('username') or '').strip().lower()
    
    # Intentamos obtener la contraseña buscando nombres comunes que usa Angular
    password = datos.get('password') or datos.get('contrasena') or datos.get('password_usuario')

    # Debug logs para el usuario (se verán en az webapp log tail)
    print(f"DEBUG LOGIN: email='{email}' | password_present={bool(password)}")

    if not email or not password:
        return jsonify({
            'error': 'Email y contraseña son obligatorios',
            'debug': f'email_recibido: {bool(email)}, password_recibida: {bool(password)}'
        }), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and check_password_hash(usuario.contrasena_hash, password):
        token = jwt.encode({
            'id': usuario.id,
            'rol': usuario.rol,
            'email': usuario.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        # LA CLAVE ESTÁ AQUÍ: Usamos 'access_token' y 'usuario'
        return jsonify({
            'access_token': token,  # <--- Antes decía 'token'
            'usuario': usuario.serializar() # Asegúrate que esto coincida con el modelo Usuario
        }), 200

    return jsonify({'error': 'Correo o contraseña incorrectos'}), 401

@auth_bp.route('/registro', methods=['POST', 'OPTIONS'])
def registro():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    datos = request.get_json(force=True, silent=True)
    if not datos:
        datos = request.form.to_dict()

    if not datos:
        return jsonify({'error': 'No se enviaron datos válidos en la petición'}), 400

    nombre = str(datos.get('nombre') or '').strip()
    email = str(datos.get('email') or '').strip().lower()
    password = datos.get('contrasena') or datos.get('password')

    if not nombre or not email or not password:
        return jsonify({'error': 'Nombre, email y contraseña son obligatorios'}), 400

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({'error': 'El correo ya está registrado'}), 409

    nuevo_usuario = Usuario(
        nombre=nombre,
        email=email,
        contrasena_hash=generate_password_hash(password),
        rol='cliente'
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()

    token = jwt.encode({
        'id': nuevo_usuario.id,
        'rol': nuevo_usuario.rol,
        'email': nuevo_usuario.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, JWT_SECRET, algorithm='HS256')

    return jsonify({
        'access_token': token,
        'usuario': nuevo_usuario.serializar()
    }), 201