## Creado por: Camilo Martinez
## Fecha: 10/04/2026
## Proyecto: Pizzería App Core
"""API REST Flask (SQLite + JWT + CORS)."""
''' AQUI ESTA TODO EL CODIGO VIEJO POR SI LO NECESITAMOS  
from __future__ import annotations
import os
import json
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Dict

import jwt as pyjwt
from flask import Flask, Response, g, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# --- Base de datos ---
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="cliente")
    fecha_registro = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def serializar(self) -> Dict[str, Any]:
        return {"id": self.id, "nombre": self.nombre, "email": self.email, "rol": self.rol, "fecha_registro": self.fecha_registro}

class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    fecha_hora = db.Column(db.String(20), nullable=False, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    iva = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    estado = db.Column(db.String(50), nullable=False, default="Pendiente")
    articulos = db.relationship("ItemPedido", backref="pedido_relacionado", lazy=True, cascade="all, delete-orphan")

    def serializar(self) -> Dict[str, Any]:
        return {
            "id": self.id, "usuario_id": self.usuario_id, "fecha_hora": self.fecha_hora,
            "articulos": [a.serializar() for a in self.articulos],
            "subtotal": round(self.subtotal, 2), "iva": round(self.iva, 2), "total": round(self.total, 2),
            "estado": self.estado
        }

class ItemPedido(db.Model):
    __tablename__ = "items_pedido"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=True) # Nuevo vínculo
    nombre = db.Column(db.String(100), nullable=False)
    tamano = db.Column(db.String(50), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio = db.Column(db.Float, nullable=False, default=0.0)
    ingredientes_extra = db.Column(db.Text, nullable=True)  # JSON string con ingredientes extra

    def serializar(self) -> Dict[str, Any]:
        extras = []
        if self.ingredientes_extra:
            try:
                extras = json.loads(self.ingredientes_extra)
            except:
                extras = []
        return {
            "id": self.id, 
            "pizza_id": self.pizza_id, 
            "nombre": self.nombre, 
            "tamano": self.tamano, 
            "cantidad": self.cantidad, 
            "precio": self.precio,
            "ingredientes_extra": extras
        }

class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
    cantidad_gastada = db.Column(db.Float, nullable=False, default=0.0)
    
    # Relaciones para facilitar consultas
    insumo = db.relationship("Insumo", backref="recetas_donde_participa")

    def to_dict(self):
        return {
            "id": self.id,
            "pizza_id": self.pizza_id,
            "insumo_id": self.insumo_id,
            "insumo_nombre": self.insumo.nombre if self.insumo else "Desconocido",
            "cantidad_gastada": self.cantidad_gastada,
            "unidad_medida": self.insumo.unidad_medida if self.insumo else ""
        }

class Insumo(db.Model):
    __tablename__ = 'insumos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad_actual = db.Column(db.Float, default=0.0)
    unidad_medida = db.Column(db.String(20), nullable=False)
    stock_minimo = db.Column(db.Float, default=10.0)

    def to_dict(self):
        return {
            "id": self.id, "nombre": self.nombre, "cantidad_actual": self.cantidad_actual,
            "unidad_medida": self.unidad_medida, "stock_minimo": self.stock_minimo
        }

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    categoria = db.Column(db.String(50), nullable=False, default='Pizza')
    precio_1 = db.Column(db.Float, nullable=False, default=0.0)
    precio_2 = db.Column(db.Float, nullable=True, default=0.0)
    precio_3 = db.Column(db.Float, nullable=True, default=0.0)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "precio_1": self.precio_1,
            "precio_2": self.precio_2,
            "precio_3": self.precio_3,
            "activo": self.activo
        }

# --- Aplicación ---
RUTA_DB: str = os.path.join(os.path.dirname(__file__), "pizzeria_core.db")
JWT_SECRET: str = "pizzeria_secret_key_fixed_2026_super_safe"
JWT_EXPIRACION_HORAS: int = 168 # Aumentado a 7 días por petición del usuario

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{RUTA_DB}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

@app.after_request
def agregar_headers_cors(respuesta: Response) -> Response:
    respuesta.headers["Access-Control-Allow-Origin"] = "*"
    respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return respuesta

# --- Helpers JWT ---
def _extraer_token_bearer() -> str | None:
    encabezado: str = request.headers.get("Authorization", "")
    print(f"[EXTREMO] Header Authorization completo: '{encabezado}'")
    partes: list[str] = encabezado.split()
    return partes[1] if len(partes) == 2 and partes[0].lower() == "bearer" else None

def _resolver_jwt():
    if request.method == "OPTIONS": return Response(status=204)
    token = _extraer_token_bearer()
    if token: token = token.strip()
    if not token:
        print("[JWT] No se encontró token en la petición")
        return jsonify({"error": "Token requerido"}), 401
    try:
        print(f"[JWT] Decodificando con secreto: {JWT_SECRET}")
        g.jwt = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"[JWT] Token decodificado para: {g.jwt.get('email')} (Rol: {g.jwt.get('rol')})")
    except pyjwt.ExpiredSignatureError:
        print("[JWT] Token expirado")
        return jsonify({"error": "Token expirado"}), 401
    except pyjwt.InvalidTokenError as e:
        print(f"[JWT] Token inválido: {e}")
        return jsonify({"error": f"Token inválido: {str(e)}"}), 401
    return None

def requiere_autenticacion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        fallo = _resolver_jwt()
        return fallo if fallo is not None else func(*args, **kwargs)
    return wrapper

def requiere_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        fallo = _resolver_jwt()
        if fallo: return fallo
        if g.jwt.get("rol") != "admin":
            return jsonify({"error": "Acceso restringido a administradores"}), 403
        return func(*args, **kwargs)
    return wrapper

def requiere_personal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        fallo = _resolver_jwt()
        if fallo: return fallo
        rol = g.jwt.get("rol")
        if rol not in ["admin", "cocinero", "domiciliario"]:
            return jsonify({"error": "Acceso restringido a personal autorizado"}), 403
        return func(*args, **kwargs)
    return wrapper

def _generar_token(usuario: Usuario) -> str:
    carga_util = {"sub": str(usuario.id), "nombre": usuario.nombre, "email": usuario.email, "rol": usuario.rol, "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRACION_HORAS)}
    return pyjwt.encode(carga_util, JWT_SECRET, algorithm="HS256")

# --- Inicialización de DB ---
with app.app_context():
    db.create_all()
    print(f"[INFO] Base de datos lista: {RUTA_DB}")

    # Migración manual pedidos
    try:
        with db.engine.connect() as conn:
            columnas = [fila[1] for fila in conn.exec_driver_sql("PRAGMA table_info(pedidos);").fetchall()]
            if "usuario_id" not in columnas:
                conn.exec_driver_sql("ALTER TABLE pedidos ADD COLUMN usuario_id INTEGER;")
                print("[INFO] Migracion aplicada: pedidos.usuario_id")
            if "estado" not in columnas:
                conn.exec_driver_sql("ALTER TABLE pedidos ADD COLUMN estado VARCHAR(50) DEFAULT 'Pendiente';")
                print("[INFO] Migracion aplicada: pedidos.estado")
            
            # Migracion ItemPedido.pizza_id
            columnas_items = [fila[1] for fila in conn.exec_driver_sql("PRAGMA table_info(items_pedido);").fetchall()]
            if "pizza_id" not in columnas_items:
                conn.exec_driver_sql("ALTER TABLE items_pedido ADD COLUMN pizza_id INTEGER;")
                print("[INFO] Migracion aplicada: items_pedido.pizza_id")
            
            # Migracion ItemPedido.ingredientes_extra
            if "ingredientes_extra" not in columnas_items:
                conn.exec_driver_sql("ALTER TABLE items_pedido ADD COLUMN ingredientes_extra TEXT;")
                print("[INFO] Migracion aplicada: items_pedido.ingredientes_extra")
    except Exception as exc: print(f"[WARN] No se pudo verificar migracion: {exc}")

    # Admin por defecto
    if not Usuario.query.filter_by(email="admin@pizzeria.com").first():
        admin = Usuario(nombre="Administrador", email="admin@pizzeria.com", contrasena_hash=generate_password_hash("admin1"), rol="admin")
        db.session.add(admin)
        db.session.commit()
        print("[INFO] Usuario admin creado")

    # Insumos por defecto
    if not Insumo.query.first():
        insumos = [
            Insumo(nombre="Harina", cantidad_actual=50.0, unidad_medida="kg", stock_minimo=10.0),
            Insumo(nombre="Queso Mozzarella", cantidad_actual=20.0, unidad_medida="kg", stock_minimo=5.0),
            Insumo(nombre="Salsa de Tomate", cantidad_actual=15.0, unidad_medida="litros", stock_minimo=3.0)
        ]
        db.session.add_all(insumos)
        db.session.commit()
        print("[INFO] Insumos iniciales creados")

    # Pizzas por defecto
    if not Pizza.query.first():
        pizzas_seed = [
            Pizza(nombre="Hawaiana", descripcion="Piña y jamón", categoria="Pizza", precio_1=20000, precio_2=30000, precio_3=40000),
            Pizza(nombre="Pepperoni", descripcion="Pepperoni clásico", categoria="Pizza", precio_1=22000, precio_2=32000, precio_3=42000),
            Pizza(nombre="Coca Cola", descripcion="Gaseosa refrescante", categoria="Gaseosa", precio_1=5000, precio_2=8000, precio_3=12000),
            Pizza(nombre="Lasaña de Carne", descripcion="Tradicional italiana", categoria="Lasaña", precio_1=25000, precio_2=35000, precio_3=None),
            Pizza(nombre="Palitos de Ajo", descripcion="Orden de 6 unidades", categoria="Otros", precio_1=15000, precio_2=None, precio_3=None)
        ]
        db.session.add_all(pizzas_seed)
        db.session.commit()
        print("[INFO] Productos iniciales creados")
    
    # Forzar activo=True para todas las pizzas existentes
    Pizza.query.update({Pizza.activo: True})
    db.session.commit()

    # Crear o forzar admin por defecto
    admin_piz = Usuario.query.filter_by(email="admin@pizzeria.com").first()
    if not admin_piz:
        admin_piz = Usuario(
            nombre="admin_pizzería",
            email="admin@pizzeria.com",
            contrasena_hash=generate_password_hash("admin123"),
            rol="admin"
        )
        db.session.add(admin_piz)
        db.session.commit()
        print("[INFO] Usuario admin creado: admin@pizzeria.com / admin123")
    else:
        if admin_piz.rol != "admin":
            admin_piz.rol = "admin"
            db.session.commit()
            print("[INFO] Rol de admin corregido para admin@pizzeria.com")

    # Recetas por defecto (Masa, Salsa, Queso)
    if not Receta.query.first():
        masa = Insumo.query.filter_by(nombre="Masa").first()
        if not masa:
            masa = Insumo(nombre="Masa", cantidad_actual=100.0, unidad_medida="unidades", stock_minimo=10.0)
            db.session.add(masa); db.session.commit()
        
        # Corregir o crear Salsa y Queso con nuevas unidades
        salsa = Insumo.query.filter_by(nombre="Salsa de Tomate").first()
        if salsa: salsa.unidad_medida = "ml"
        else:
            salsa = Insumo(nombre="Salsa de Tomate", cantidad_actual=5000.0, unidad_medida="ml", stock_minimo=500.0)
            db.session.add(salsa)
            
        queso = Insumo.query.filter_by(nombre="Queso Mozzarella").first()
        if queso: queso.unidad_medida = "gr"
        else:
            queso = Insumo(nombre="Queso Mozzarella", cantidad_actual=10000.0, unidad_medida="gr", stock_minimo=1000.0)
            db.session.add(queso)
        
        db.session.commit()
        
        todas_pizzas = Pizza.query.all()
        for p in todas_pizzas:
            db.session.add(Receta(pizza_id=p.id, insumo_id=masa.id, cantidad_gastada=1.0))
            db.session.add(Receta(pizza_id=p.id, insumo_id=salsa.id, cantidad_gastada=60.0))
            db.session.add(Receta(pizza_id=p.id, insumo_id=queso.id, cantidad_gastada=200.0))
        
        db.session.commit()
        print("[INFO] Recetas iniciales creadas con unidades métricas (gr/ml)")

# --- RUTAS API ---
@app.route("/api/auth/registro", methods=["POST"])
def registro():
    datos = request.get_json() or {}
    email = str(datos.get("email", "")).strip().lower()
    if Usuario.query.filter_by(email=email).first(): return jsonify({"error": "El email ya esta registrado"}), 409
    nuevo = Usuario(nombre=datos.get("nombre"), email=email, contrasena_hash=generate_password_hash(datos.get("contrasena")), rol="cliente")
    db.session.add(nuevo); db.session.commit()
    return jsonify({"access_token": _generar_token(nuevo), "usuario": nuevo.serializar()}), 201

@app.route("/api/auth/login", methods=["POST"])
def login():
    datos = request.get_json() or {}
    usuario = Usuario.query.filter_by(email=str(datos.get("email", "")).lower()).first()
    if not usuario or not check_password_hash(usuario.contrasena_hash, datos.get("contrasena")):
        print(f"[LOGIN] Intento fallido para: {datos.get('email')}")
        return jsonify({"error": "Credenciales incorrectas"}), 401
    
    # Asegurar rol en objeto antes de serializar
    if usuario.email == 'admin@pizzeria.com' and usuario.rol != 'admin':
        usuario.rol = 'admin'
        db.session.commit()
    
    token = _generar_token(usuario)
    print(f"[LOGIN] Enviando rol: {usuario.rol} para {usuario.email}")
    return jsonify({
        "access_token": token, 
        "rol": usuario.rol, 
        "email": usuario.email,
        "usuario": usuario.serializar()
    }), 200

@app.route("/api/usuarios", methods=["GET", "POST"])
@requiere_admin
def gestionar_usuarios():
    if request.method == "GET":
        usuarios = Usuario.query.all()
        return jsonify({"usuarios": [u.serializar() for u in usuarios]}), 200
    
    if request.method == "POST":
        datos = request.get_json() or {}
        email = str(datos.get("email", "")).strip().lower()
        if Usuario.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya está registrado"}), 409
        
        nuevo = Usuario(
            nombre=datos.get("nombre"),
            email=email,
            contrasena_hash=generate_password_hash(datos.get("contrasena", "pizzeria123")),
            rol=datos.get("rol", "cocinero")
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify(nuevo.serializar()), 201
@app.route("/api/usuarios/<int:id>", methods=["PUT", "DELETE"])
@requiere_admin
def gestionar_usuario_id(id):
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == "DELETE":
        if usuario.email == "admin@pizzeria.com":
            return jsonify({"error": "No se puede eliminar al administrador principal"}), 400
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario eliminado"}), 200
    
    if request.method == "PUT":
        datos = request.get_json() or {}
        usuario.nombre = datos.get("nombre", usuario.nombre)
        usuario.rol = datos.get("rol", usuario.rol)
        if datos.get("email"):
            usuario.email = str(datos.get("email")).strip().lower()
        if datos.get("contrasena"):
            usuario.contrasena_hash = generate_password_hash(datos.get("contrasena"))
        
        db.session.commit()
        return jsonify(usuario.serializar()), 200
@app.route("/api/pizzas", methods=["GET", "POST"])
def gestionar_pizzas():
    if request.method == "POST":
        fallo = _resolver_jwt()
        if fallo: return fallo
        if g.jwt.get("rol") != "admin":
            return jsonify({"error": "Acceso restringido a administradores"}), 403
        
        datos = request.get_json() or {}
        nueva = Pizza(
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            categoria=datos.get('categoria', 'Pizza'),
            precio_1=float(datos.get('precio_1', 0.0) or 0),
            precio_2=float(datos.get('precio_2') or 0) if datos.get('precio_2') else None,
            precio_3=float(datos.get('precio_3') or 0) if datos.get('precio_3') else None
        )
        db.session.add(nueva)
        db.session.commit()
        return jsonify({"status": "ok", "pizza": nueva.to_dict()}), 201
    
    # GET - Devuelve solo pizzas activas
    return jsonify({"pizzas": [p.to_dict() for p in Pizza.query.filter_by(activo=True).all()]})

@app.route("/api/pizzas/<int:id>", methods=["DELETE"])
@requiere_admin
def eliminar_pizza(id):
    pizza = Pizza.query.get_or_404(id)
    db.session.delete(pizza) # Hard delete
    db.session.commit()
    return jsonify({"status": "ok", "mensaje": "Pizza eliminada permanentemente"})

@app.route("/api/pizzas/<int:id>", methods=["PUT"])
@requiere_admin
def actualizar_pizza(id):
    pizza = Pizza.query.get_or_404(id)
    datos = request.get_json() or {}
    if 'nombre' in datos: pizza.nombre = datos['nombre']
    if 'descripcion' in datos: pizza.descripcion = datos['descripcion']
    if 'categoria' in datos: pizza.categoria = datos['categoria']
    if 'precio_1' in datos: pizza.precio_1 = float(datos['precio_1']) if datos['precio_1'] else None
    if 'precio_2' in datos: pizza.precio_2 = float(datos['precio_2']) if datos['precio_2'] else None
    if 'precio_3' in datos: pizza.precio_3 = float(datos['precio_3']) if datos['precio_3'] else None
    if 'activo' in datos: pizza.activo = bool(datos['activo'])
    db.session.commit()
    return jsonify({"status": "ok", "pizza": pizza.to_dict()})

@app.route('/api/insumos', methods=['GET'])
def get_insumos():
    return jsonify([i.to_dict() for i in Insumo.query.all()])

@app.route('/api/insumos', methods=['POST'])
def add_insumo():
    data = request.get_json()
    nuevo_insumo = Insumo(
        nombre=data['nombre'],
        cantidad_actual=data.get('cantidad_actual', 0.0),
        stock_minimo=data.get('stock_minimo', 0.0),
        unidad_medida=data.get('unidad_medida', 'kg')
    )
    db.session.add(nuevo_insumo)
    db.session.commit()
    return jsonify({"status": "ok", "insumo": nuevo_insumo.to_dict()}), 201

@app.route('/api/insumos/<int:id>', methods=['PUT'])
def update_insumo(id):
    data = request.get_json()
    insumo = Insumo.query.get_or_404(id)
    if 'cantidad_actual' in data: insumo.cantidad_actual = float(data['cantidad_actual'])
    db.session.commit()
    return jsonify(insumo.to_dict())

@app.route('/api/insumos/<int:id>', methods=['DELETE'])
def delete_insumo(id):
    insumo = Insumo.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    return jsonify({"status": "ok", "mensaje": "Insumo eliminado."})

@app.route("/api/pedidos", methods=["POST"])
def crear_pedido():
    """
    Crea un pedido con las siguientes mejoras:
    1. Calcula automáticamente el precio total sumando ingredientes extra
    2. Descuenta automáticamente los insumos del inventario
    3. Valida que haya suficiente stock antes de crear el pedido
    """
    datos = request.get_json() or {}
    try:
        usuario_id = datos.get("usuario_id")
        fecha_hora = datos.get("fecha_hora") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        articulos = datos.get("articulos", [])
        
        print(f"\n[PEDIDO] Iniciando creación de pedido para usuario {usuario_id}")
        
        # PASO 1: Calcular precio total y validar stock
        subtotal_calculado = 0.0
        items_procesados = []
        
        for item in articulos:
            # Obtener pizza_id
            id_catalogo = item.get("pizza_id")
            if id_catalogo is None:
                nombre_busqueda = item.get("nombre")
                pizza_encontrada = Pizza.query.filter_by(nombre=nombre_busqueda).first()
                if pizza_encontrada:
                    id_catalogo = pizza_encontrada.id
                    print(f"[PEDIDO] ID recuperado para '{nombre_busqueda}': {id_catalogo}")
            
            # Calcular precio con ingredientes extra
            precio_base = float(item.get("precio", 0.0))
            ingredientes_extra = item.get("ingredientes_extra", [])
            precio_extras = 0.0
            
            # Sumar precio de ingredientes extra (ejemplo: $2000 por ingrediente)
            PRECIO_POR_EXTRA = 2000.0
            if ingredientes_extra and len(ingredientes_extra) > 0:
                precio_extras = len(ingredientes_extra) * PRECIO_POR_EXTRA
                print(f"[PEDIDO] {len(ingredientes_extra)} ingredientes extra = ${precio_extras}")
            
            precio_total_item = precio_base + precio_extras
            cantidad = int(item.get("cantidad", 1))
            subtotal_item = precio_total_item * cantidad
            subtotal_calculado += subtotal_item
            
            print(f"[PEDIDO] Item: {item.get('nombre')} - Base: ${precio_base} + Extras: ${precio_extras} = ${precio_total_item} x {cantidad} = ${subtotal_item}")
            
            # Guardar item procesado
            items_procesados.append({
                "pizza_id": id_catalogo,
                "nombre": item.get("nombre"),
                "tamano": item.get("tamano"),
                "cantidad": cantidad,
                "precio": precio_total_item,
                "ingredientes_extra": ingredientes_extra
            })
            
            # VALIDAR STOCK: Verificar que hay suficientes insumos
            if id_catalogo:
                recetas = Receta.query.filter_by(pizza_id=id_catalogo).all()
                for receta in recetas:
                    insumo = Insumo.query.get(receta.insumo_id)
                    cantidad_necesaria = receta.cantidad_gastada * cantidad
                    
                    # Agregar cantidad extra si hay ingredientes extra del mismo tipo
                    if ingredientes_extra and insumo.nombre in ingredientes_extra:
                        # Duplicar la cantidad del insumo si está en extras
                        cantidad_necesaria *= 1.5
                    
                    if insumo.cantidad_actual < cantidad_necesaria:
                        return jsonify({
                            "error": f"Stock insuficiente de {insumo.nombre}. Disponible: {insumo.cantidad_actual} {insumo.unidad_medida}, Necesario: {cantidad_necesaria} {insumo.unidad_medida}"
                        }), 400
        
        # Calcular IVA y total
        iva_calculado = subtotal_calculado * 0.19
        total_calculado = subtotal_calculado + iva_calculado
        
        print(f"[PEDIDO] Subtotal: ${subtotal_calculado}, IVA: ${iva_calculado}, Total: ${total_calculado}")
        
        # PASO 2: Crear el pedido
        nuevo_pedido = Pedido(
            usuario_id=usuario_id,
            subtotal=subtotal_calculado,
            iva=iva_calculado,
            total=total_calculado,
            fecha_hora=fecha_hora,
            estado="Pendiente"
        )
        db.session.add(nuevo_pedido)
        db.session.flush()
        
        # PASO 3: Crear items y descontar inventario
        print(f"[PEDIDO] Descontando inventario...")
        for item_data in items_procesados:
            # Crear item del pedido
            nuevo_item = ItemPedido(
                pedido_id=nuevo_pedido.id,
                pizza_id=item_data["pizza_id"],
                nombre=item_data["nombre"],
                tamano=item_data["tamano"],
                cantidad=item_data["cantidad"],
                precio=item_data["precio"],
                ingredientes_extra=json.dumps(item_data["ingredientes_extra"]) if item_data["ingredientes_extra"] else None
            )
            db.session.add(nuevo_item)
            
            # Descontar insumos del inventario
            if item_data["pizza_id"]:
                recetas = Receta.query.filter_by(pizza_id=item_data["pizza_id"]).all()
                for receta in recetas:
                    insumo = Insumo.query.get(receta.insumo_id)
                    cantidad_a_descontar = receta.cantidad_gastada * item_data["cantidad"]
                    
                    # Si el insumo está en ingredientes extra, aumentar cantidad
                    if item_data["ingredientes_extra"] and insumo.nombre in item_data["ingredientes_extra"]:
                        cantidad_a_descontar *= 1.5
                        print(f"[PEDIDO] Ingrediente extra detectado: {insumo.nombre} (cantidad aumentada)")
                    
                    insumo.cantidad_actual -= cantidad_a_descontar
                    print(f"[PEDIDO] Descontado: {insumo.nombre} -{cantidad_a_descontar} {insumo.unidad_medida} (Restante: {insumo.cantidad_actual})")
        
        db.session.commit()
        print(f"[PEDIDO] ✅ Pedido #{nuevo_pedido.id} creado exitosamente\n")
        
        return jsonify({
            "status": "ok", 
            "mensaje": "Pedido creado con éxito", 
            "pedido_id": nuevo_pedido.id,
            "subtotal": round(subtotal_calculado, 2),
            "iva": round(iva_calculado, 2),
            "total": round(total_calculado, 2)
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Error al crear pedido: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route("/api/pedidos", methods=["GET"])
@requiere_autenticacion
def listar_pedidos():
    usuario_id_token = g.jwt.get("sub")
    rol = g.jwt.get("rol")

    if rol == "admin":
        # Si es admin, puede ver todos o filtrar por usuario_id
        u_id = request.args.get("usuario_id")
        if u_id:
            pedidos = Pedido.query.filter_by(usuario_id=u_id).order_by(Pedido.id.desc()).all()
        else:
            pedidos = Pedido.query.order_by(Pedido.id.desc()).all()
    else:
        # Si es cliente, solo sus pedidos
        pedidos = Pedido.query.filter_by(usuario_id=usuario_id_token).order_by(Pedido.id.desc()).all()
    
    return jsonify({"pedidos": [p.serializar() for p in pedidos]})

@app.route("/api/pedidos/<int:id>/estado", methods=["PATCH"])
@requiere_personal
def actualizar_estado_pedido(id):
    pedido = Pedido.query.get_or_404(id)
    datos = request.get_json() or {}
    nuevo_estado = datos.get("estado", "")

    estado_objetivo = nuevo_estado.strip().lower()
    estado_actual = pedido.estado.strip().lower()

    print(f"\n[DEBUG] Intentando cambiar pedido {id}: '{estado_actual}' -> '{estado_objetivo}'")

    if estado_objetivo == 'entregado' and estado_actual != 'entregado':
        try:
            print(f"=== INICIANDO DESCUENTO PEDIDO {pedido.id} ===")
            for item in pedido.articulos: 
                # 1. Intentamos sacar el ID
                id_a_buscar = item.pizza_id
                
                # 2. Si el ID es None (como en tu pedido 2), buscamos por NOMBRE
                if id_a_buscar is None:
                    print(f"[DEBUG] ID es None para '{item.nombre}', buscando por nombre...")
                    # Quitamos la palabra 'Pizza' si es necesario o buscamos coincidencia parcial
                    pizza_db = Pizza.query.filter(Pizza.nombre.icontains(item.nombre.replace("Pizza ", "").strip())).first()
                    if pizza_db:
                        id_a_buscar = pizza_db.id
                        print(f"[DEBUG] Encontrado ID {id_a_buscar} para '{item.nombre}'")

                if id_a_buscar:
                    recetas = Receta.query.filter_by(pizza_id=id_a_buscar).all()
                    print(f"[DEBUG] Se encontraron {len(recetas)} ingredientes")
                    
                    for r in recetas:
                        insumo = Insumo.query.get(r.insumo_id)
                        cantidad_total = r.cantidad_gastada * item.cantidad
                        
                        if insumo.cantidad_actual < cantidad_total:
                            db.session.rollback()
                            return jsonify({"error": f"No hay suficiente {insumo.nombre}"}), 400
                        
                        insumo.cantidad_actual -= cantidad_total
                        print(f"[OK] Descontado: {insumo.nombre} (-{cantidad_total})")
                else:
                    print(f"[ERROR] Ni el ID ni el nombre '{item.nombre}' sirvieron.")

            db.session.commit()
            print("=== INVENTARIO ACTUALIZADO CON ÉXITO ===\n")
        except Exception as e:
            db.session.rollback()
            print(f"[CRÍTICO] Error: {str(e)}")
            return jsonify({"error": "Error en inventario"}), 500

    pedido.estado = nuevo_estado
    db.session.commit()
    return jsonify({"status": "ok", "mensaje": f"Estado actualizado a {nuevo_estado}"}), 200

@app.route("/api/pizzas/<int:id>/receta", methods=["GET", "POST"])
@requiere_admin
def gestionar_receta(id):
    if request.method == "POST":
        datos = request.get_json() or []
        # Limpiar receta actual
        Receta.query.filter_by(pizza_id=id).delete()
        
        for item in datos:
            nueva = Receta(
                pizza_id=id,
                insumo_id=item.get("insumo_id"),
                cantidad_gastada=float(item.get("cantidad_gastada", 0))
            )
            db.session.add(nueva)
        
        db.session.commit()
        return jsonify({"status": "ok", "mensaje": "Receta actualizada"})
    
    recetas = Receta.query.filter_by(pizza_id=id).all()
    return jsonify({"receta": [r.to_dict() for r in recetas]})

@app.route("/api/health", methods=["GET"])
def estado_servidor(): 
    return jsonify({"status": "ok", "message": "Servidor funcionando"})

# Esta es la que creamos con Milo Local
@app.route("/status", methods=["GET"])
def status_pizzeria():
    return jsonify({
        "status": "open",
        "message": "La pizzería está abierta y el modelo local funciona",
        "chef": "Milo"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''

# ==========================================
# Proyecto: PizzaOS - Backend
# Creado por: Camilo Martinez
# Fecha: 27 de abril de 2026
# ==========================================

from flask import Flask, jsonify, render_template
from flask_cors import CORS
from config import Config, db

# 1. Inicialización de la App
app = Flask(__name__)

# 2. Configuración de CORS
from flask_cors import CORS

CORS(app, resources={r"/api/*": {
    "origins": "http://localhost:4200",
    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}}, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

# Asegurar headers CORS en todas las respuestas, incluyendo preflight OPTIONS
from flask import Response, request as flask_request

@app.after_request
def agregar_headers_cors(respuesta: Response) -> Response:
    respuesta.headers["Access-Control-Allow-Origin"] = "http://localhost:4200"
    respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
    respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    respuesta.headers["Access-Control-Allow-Credentials"] = "true"
    return respuesta

# 3. Cargar configuración de Base de Datos
app.config.from_object(Config)
db.init_app(app)

# 4. Registro de Rutas
from routes.pedido_routes import pedidos_blueprint
app.register_blueprint(pedidos_blueprint, url_prefix='/api')

 

# 5. Rutas de prueba
@app.route('/')
def index():
    return "<h1>¡PizzaOS con Postgres Funcionando!</h1><p>Creado por Camilo Martinez</p>"

from flask_cors import cross_origin

# --- Helpers JWT para rutas de usuarios ---
JWT_SECRET_USUARIOS = "pizzeria_secret_key_fixed_2026_super_safe"

def _verificar_token_admin():
    """Verifica el token JWT y que el rol sea admin. Retorna (payload, None) o (None, respuesta_error)."""
    import jwt as pyjwt
    from flask import request, g
    if flask_request.method == 'OPTIONS':
        return None, (jsonify({}), 200)
    encabezado = flask_request.headers.get('Authorization', '')
    partes = encabezado.split()
    if len(partes) != 2 or partes[0].lower() != 'bearer':
        return None, (jsonify({'error': 'Token requerido'}), 401)
    try:
        payload = pyjwt.decode(partes[1], JWT_SECRET_USUARIOS, algorithms=['HS256'])
    except pyjwt.ExpiredSignatureError:
        return None, (jsonify({'error': 'Token expirado'}), 401)
    except pyjwt.InvalidTokenError as e:
        return None, (jsonify({'error': f'Token inválido: {str(e)}'}), 401)
    if payload.get('rol') != 'admin':
        return None, (jsonify({'error': 'Acceso restringido a administradores'}), 403)
    return payload, None

@app.route('/api/usuarios', methods=['GET', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def get_usuarios():
    payload, err = _verificar_token_admin()
    if err: return err
    from models.usuario import Usuario
    usuarios = Usuario.query.order_by(Usuario.id).all()
    return jsonify({"usuarios": [u.serializar() for u in usuarios]}), 200

@app.route('/api/usuarios', methods=['POST'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def crear_usuario():
    payload, err = _verificar_token_admin()
    if err: return err
    from models.usuario import Usuario
    from werkzeug.security import generate_password_hash
    datos = flask_request.get_json() or {}
    email = str(datos.get('email', '')).strip().lower()
    if not email or not datos.get('nombre'):
        return jsonify({'error': 'Nombre y email son obligatorios'}), 400
    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'El email ya está registrado'}), 409
    contrasena = datos.get('password') or datos.get('contrasena', 'pizzeria123')
    nuevo = Usuario(
        nombre=datos.get('nombre'),
        email=email,
        contrasena_hash=generate_password_hash(contrasena),
        rol=datos.get('rol', 'cocinero')
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.serializar()), 201

@app.route('/api/usuarios/<int:id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def actualizar_usuario(id):
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200
    payload, err = _verificar_token_admin()
    if err: return err
    from models.usuario import Usuario
    from werkzeug.security import generate_password_hash
    usuario = Usuario.query.get_or_404(id)
    datos = flask_request.get_json() or {}
    if 'nombre' in datos:
        usuario.nombre = datos['nombre']
    if 'rol' in datos:
        usuario.rol = datos['rol']
    if 'email' in datos:
        usuario.email = str(datos['email']).strip().lower()
    if datos.get('password'):
        usuario.contrasena_hash = generate_password_hash(datos['password'])
    db.session.commit()
    return jsonify(usuario.serializar()), 200

@app.route('/api/usuarios/<int:id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def eliminar_usuario(id):
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200
    payload, err = _verificar_token_admin()
    if err: return err
    from models.usuario import Usuario
    usuario = Usuario.query.get_or_404(id)
    if usuario.email == 'admin@pizzeria.com':
        return jsonify({'error': 'No se puede eliminar al administrador principal'}), 400
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado'}), 200

@app.route('/api/admin/rentabilidad', methods=['GET', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def get_rentabilidad():
    """
    Devuelve el análisis de rentabilidad por producto filtrado por tamaño:
    costo de producción, precio de venta, ganancia y margen %.
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    payload, err = _verificar_token_admin()
    if err: return err

    from models.producto import Producto, SizeEnum
    from models.pedido import Pedido
    import json as _json

    # Obtener tamaño de los parámetros de consulta, por defecto Pequeña
    size_str = flask_request.args.get('size', 'Pequeña')
    try:
        # Intentamos mapear el string al enum
        # Si el string viene como "Pequeña", buscamos el miembro cuyo valor sea ese.
        size_enum = next(s for s in SizeEnum if s.value == size_str)
    except StopIteration:
        size_enum = SizeEnum.PEQUENA

    productos = Producto.query.all()
    items_rentabilidad = [p.rentabilidad(size_enum) for p in productos]

    # Ordenar por margen descendente
    items_rentabilidad.sort(key=lambda x: x['margen_porcentaje'], reverse=True)

    # Resumen: más rentable y mayor costo para ese tamaño específico
    mas_rentable = max(items_rentabilidad, key=lambda x: x['margen_porcentaje'], default=None)
    mayor_costo = max(items_rentabilidad, key=lambda x: x['costo_produccion'], default=None)

    # Ganancia total estimada de pedidos completados
    ganancia_total = 0.0
    try:
        pedidos_completados = Pedido.query.filter(
            Pedido.estado.ilike('entregado')
        ).all()

        # Mapa nombre → ganancia por unidad para lookup rápido
        ganancia_por_nombre = {p['nombre'].lower(): p['ganancia'] for p in items_rentabilidad}

        for pedido in pedidos_completados:
            if pedido.articulos_json:
                try:
                    articulos = _json.loads(pedido.articulos_json)
                    for art in articulos:
                        nombre_key = str(art.get('nombre', '')).lower()
                        cantidad = int(art.get('cantidad', 1))
                        ganancia_unitaria = ganancia_por_nombre.get(nombre_key, 0.0)
                        ganancia_total += ganancia_unitaria * cantidad
                except Exception:
                    pass
    except Exception as e:
        print(f'[RENTABILIDAD] Error calculando ganancia total: {e}')

    return jsonify({
        "productos": items_rentabilidad,
        "resumen": {
            "mas_rentable": mas_rentable,
            "mayor_costo": mayor_costo,
            "ganancia_total_estimada": round(ganancia_total, 2),
            "total_productos": len(items_rentabilidad)
        }
    }), 200

@app.route('/api/usuarios/<int:id>/rol', methods=['PATCH', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def cambiar_rol_usuario(id):
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200
    payload, err = _verificar_token_admin()
    if err: return err
    from models.usuario import Usuario
    usuario = Usuario.query.get_or_404(id)
    datos = flask_request.get_json() or {}
    nuevo_rol = datos.get('rol', '').strip().lower()
    roles_validos = ['admin', 'cocinero', 'domiciliario', 'cliente', 'mesero']
    if nuevo_rol not in roles_validos:
        return jsonify({'error': f'Rol inválido. Opciones: {", ".join(roles_validos)}'}), 400
    if usuario.email == 'admin@pizzeria.com' and nuevo_rol != 'admin':
        return jsonify({'error': 'No se puede cambiar el rol del administrador principal'}), 400
    rol_anterior = usuario.rol
    usuario.rol = nuevo_rol
    db.session.commit()
    print(f'[ROL] {usuario.email}: {rol_anterior} → {nuevo_rol} (por {payload.get("email")})')
    return jsonify({
        'mensaje': f'Rol de {usuario.nombre} actualizado a {nuevo_rol}',
        'usuario': usuario.serializar()
    }), 200

@app.route('/api/usuarios/<int:id>/reset-password', methods=['POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def reset_password_usuario(id):
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200
    payload, err = _verificar_token_admin()
    if err: return err
    from models.usuario import Usuario
    from werkzeug.security import generate_password_hash
    usuario = Usuario.query.get_or_404(id)
    datos = flask_request.get_json() or {}
    nueva_contrasena = datos.get('nueva_contrasena', '').strip()
    if len(nueva_contrasena) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400
    usuario.contrasena_hash = generate_password_hash(nueva_contrasena)
    db.session.commit()
    print(f'[RESET-PWD] Contraseña reseteada para usuario {usuario.email} por admin {payload.get("email")}')
    return jsonify({'mensaje': f'Contraseña de {usuario.nombre} actualizada correctamente'}), 200

# 6. Ejecución del Servidor
if __name__ == '__main__':
    with app.app_context():
        # Importamos modelos para que SQLAlchemy cree las tablas en Postgres
        import models
        from models.usuario import Usuario
        db.create_all()

        # Migración: agregar precio_unidad a la tabla insumo si no existe
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='insumo' AND column_name='precio_unidad'"
                ))
                if not result.fetchone():
                    conn.execute(text(
                        "ALTER TABLE insumo ADD COLUMN precio_unidad NUMERIC(10,2)"
                    ))
                    # Inicializar con el valor de precio existente
                    conn.execute(text(
                        "UPDATE insumo SET precio_unidad = precio WHERE precio_unidad IS NULL"
                    ))
                    conn.commit()
                    print('[MIGRACIÓN] Columna precio_unidad agregada a tabla insumo')
        except Exception as e:
            print(f'[MIGRACIÓN] precio_unidad ya existe o error: {e}')

        # Crear admin por defecto si no existe
        from werkzeug.security import generate_password_hash
        admin = Usuario.query.filter_by(email='admin@pizzeria.com').first()
        if not admin:
            admin = Usuario(
                nombre='Administrador',
                email='admin@pizzeria.com',
                contrasena_hash=generate_password_hash('admin123'),
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print('[INFO] Usuario admin creado: admin@pizzeria.com / admin123')
        else:
            if admin.rol != 'admin':
                admin.rol = 'admin'
                db.session.commit()
                print('[INFO] Rol de admin corregido')

    app.run(debug=True, port=5000)