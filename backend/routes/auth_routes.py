from flask import Blueprint, request, jsonify
from models.database import db
from models.usuario import Usuario
from werkzeug.security import check_password_hash
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

    datos = request.get_json()
    if not datos:
        return jsonify({'error': 'No se enviaron datos'}), 400

    # Intentamos obtener el email de varias formas comunes
    email = str(datos.get('email') or datos.get('username') or '').strip().lower()
    
    # Intentamos obtener la contraseña buscando nombres comunes que usa Angular
    password = datos.get('password') or datos.get('contrasena') or datos.get('password_usuario')

    # Imprimimos en la terminal para que TÚ veas qué está llegando realmente
    print(f"DEBUG: Intentando login para: {email} | Password recibida: {'***' if password else 'VACÍA'}")

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son obligatorios'}), 400

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