## Creado por Camilo Martinez
## Fecha: 27/04/2026
from flask import Blueprint, request, redirect, render_template, url_for, flash, jsonify
from flask_cors import cross_origin  # <--- Asegúrate que esté aquí solo
from models.pedido import Pedido
from models.insumo import Insumo
from config import db
import jwt as pyjwt
from datetime import datetime, timedelta, timezone

# Definición del Blueprint
pedidos_blueprint = Blueprint('pedidos', __name__, url_prefix='/api')

@pedidos_blueprint.route('/nuevo', methods=['GET', 'POST'])
def nuevo_pedido():
    if request.method == 'POST':
        cliente = request.form.get('cliente')
        pizza_seleccionada = request.form.get('pizzas')
        direccion = request.form.get('direccion')

        # VALIDACIÓN: Si falta algo, detenemos el proceso
        if not cliente or not direccion or not pizza_seleccionada:
            return "<h1>⚠️ Error: Todos los campos son obligatorios.</h1><a href='/pedidos/nuevo'>Volver</a>"

        # 2. Creamos el objeto solo si pasó la validación
        nuevo = Pedido(
            cliente=cliente,
            pizzas=pizza_seleccionada,
            direccion=direccion
        )

        try:
            db.session.add(nuevo)
            db.session.commit()
            return redirect(url_for('pedidos.listar_pedidos'))
        except Exception as e:
            db.session.rollback()
            return f"Error al guardar: {str(e)}"

    ## Si es GET, solo mostramos el formulario con los insumos
    insumos = Insumo.query.all()
    return render_template('pedidos/crear_pedido.html', insumos=insumos)
    
@pedidos_blueprint.route('/listar')
def listar_pedidos():
    todos_los_pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template('pedidos/listar_pedidos.html', pedidos=todos_los_pedidos)

@pedidos_blueprint.route('/pedidos', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_pedidos():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    if request.method == 'POST':
        try:
            data = request.get_json()
            articulos = data.get('articulos', [])
            
            import json
            # Crear string de pizzas para retrocompatibilidad
            pizzas_str = ", ".join([f"{a.get('cantidad', 1)}x {a.get('nombre', '')} {a.get('tamano', '')}" for a in articulos])
            
            nuevo_pedido = Pedido(
                cliente=str(data.get('usuario_id', 'Guest')),
                direccion="Recoger en local", # Default fallback
                pizzas=pizzas_str,
                total=data.get('total', 0.0),
                estado="Pendiente",
                articulos_json=json.dumps(articulos)
            )
            db.session.add(nuevo_pedido)
            db.session.commit()
            return jsonify({"message": "Pedido creado", "id": nuevo_pedido.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    try:
        todos_los_pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
        pedidos_json = []
        for p in todos_los_pedidos:
            # Parsear articulos_json para devolver los items con detalle
            articulos = []
            if p.articulos_json:
                try:
                    import json as _json
                    raw = _json.loads(p.articulos_json)
                    articulos = [
                        {
                            "nombre": a.get("nombre", ""),
                            "tamano": a.get("tamano", ""),
                            "cantidad": a.get("cantidad", 1),
                            "precio": float(a.get("precio", 0))
                        }
                        for a in raw
                    ]
                except Exception:
                    articulos = []

            pedidos_json.append({
                "id": p.id,
                "cliente": p.cliente,
                "pizzas": p.pizzas,
                "direccion": p.direccion,
                "total": float(p.total) if p.total else 0.0,
                "subtotal": float(p.total) / 1.19 if p.total else 0.0,
                "iva": float(p.total) - float(p.total) / 1.19 if p.total else 0.0,
                "estado": p.estado or "Pendiente",
                "fecha_hora": p.fecha.strftime("%Y-%m-%d %H:%M:%S") if p.fecha else "",
                "fecha": p.fecha.strftime("%Y-%m-%d %H:%M:%S") if p.fecha else "",
                "articulos": articulos
            })

        return jsonify({
            "pedidos": pedidos_json,
            "total_pedidos": len(pedidos_json)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/pedidos/<int:id>/estado', methods=['PATCH', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_actualizar_estado_pedido(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        pedido = Pedido.query.get(id)
        if not pedido:
            return jsonify({"error": "Pedido no encontrado"}), 404
            
        pedido.estado = nuevo_estado
        
        # LÓGICA DE DESCUENTO DE INVENTARIO
        if nuevo_estado in ["Preparando", "Entregado"] and not pedido.inventario_deducido:
            import json
            from models.producto import RecetaItem
            
            if pedido.articulos_json:
                articulos = json.loads(pedido.articulos_json)
                for art in articulos:
                    pizza_id = art.get('pizza_id')
                    if not pizza_id: continue
                    cantidad_pedida = art.get('cantidad', 1)
                    
                    # Buscar receta de este producto filtrando por TAMAÑO
                    from models.producto import SizeEnum
                    tamano_pedida_str = art.get('tamano', 'Pequeña')
                    try:
                        tamano_enum = next(s for s in SizeEnum if s.value == tamano_pedida_str)
                    except StopIteration:
                        tamano_enum = SizeEnum.PEQUENA
                        
                    receta_items = RecetaItem.query.filter_by(producto_id=pizza_id, size=tamano_enum).all()
                    
                    if not receta_items:
                        # Si no hay receta para ese tamaño, buscar la predeterminada (Pequeña)
                        print(f"[DEBUG] No hay receta para {tamano_pedida}, usando 'Pequeña'")
                        receta_items = RecetaItem.query.filter_by(producto_id=pizza_id, size='Pequeña').all()

                    for r_item in receta_items:
                        # Descontar insumo proporcionalmente
                        insumo = r_item.insumo
                        if insumo:
                            descuento_total = r_item.cantidad_gastada * cantidad_pedida
                            # Aseguramos que usamos el atributo correcto (cantidad o cantidad_actual)
                            # Viendo el modelo de Insumo (visto en pasos previos), parece ser cantidad_actual
                            # pero en este blueprint usan .cantidad? Vamos a verificar el modelo Insumo.
                            if hasattr(insumo, 'cantidad_actual'):
                                insumo.cantidad_actual = float(insumo.cantidad_actual) - descuento_total
                            else:
                                insumo.cantidad = float(insumo.cantidad) - descuento_total
                            
            pedido.inventario_deducido = True
            
        db.session.commit()
        return jsonify({"message": "Estado actualizado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email = data.get('email', '').strip().lower()
    contrasena = data.get('contrasena', '').strip()

    print(f"DEBUG: Intentando login con email: '{email}'")

    # Buscar usuario en PostgreSQL
    from models.usuario import Usuario
    from werkzeug.security import check_password_hash

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        print(f"DEBUG: Usuario no encontrado: '{email}'")
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    if not check_password_hash(usuario.contrasena_hash, contrasena):
        print(f"DEBUG: Contraseña incorrecta para: '{email}'")
        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    carga_util = {
        "sub": str(usuario.id),
        "nombre": usuario.nombre,
        "email": usuario.email,
        "rol": usuario.rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=168)
    }
    token_real = pyjwt.encode(carga_util, "pizzeria_secret_key_fixed_2026_super_safe", algorithm="HS256")

    print(f"DEBUG: Login exitoso para '{email}' con rol '{usuario.rol}'")
    return jsonify({
        "access_token": token_real,
        "rol": usuario.rol,
        "email": usuario.email,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "email": usuario.email,
            "rol": usuario.rol
        }
    }), 200

@pedidos_blueprint.route('/auth/registro', methods=['POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True, methods=['POST', 'OPTIONS'])
def registro():
    """Registro de nuevos usuarios con rol 'cliente' por defecto."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    from models.usuario import Usuario
    from werkzeug.security import generate_password_hash

    datos = request.get_json(force=True) or {}
    nombre = str(datos.get('nombre', '')).strip()
    email = str(datos.get('email', '')).strip().lower()
    contrasena = str(datos.get('contrasena', '')).strip()

    print(f"[REGISTRO] Intento de registro: nombre='{nombre}', email='{email}'")

    # Validaciones básicas
    if not nombre or not email or not contrasena:
        return jsonify({"error": "Nombre, email y contraseña son obligatorios"}), 400
    if len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Verificar email duplicado
    if Usuario.query.filter_by(email=email).first():
        print(f"[REGISTRO] Email ya registrado: '{email}'")
        return jsonify({"error": "El email ya está registrado"}), 409

    # Crear usuario con rol 'cliente' por defecto
    nuevo = Usuario(
        nombre=nombre,
        email=email,
        contrasena_hash=generate_password_hash(contrasena),
        rol='cliente'
    )
    db.session.add(nuevo)
    db.session.commit()
    print(f"[REGISTRO] Usuario creado: id={nuevo.id}, email='{nuevo.email}', rol='{nuevo.rol}'")

    # Generar token JWT para inicio de sesión automático
    carga_util = {
        "sub": str(nuevo.id),
        "nombre": nuevo.nombre,
        "email": nuevo.email,
        "rol": nuevo.rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=168)
    }
    token = pyjwt.encode(carga_util, "pizzeria_secret_key_fixed_2026_super_safe", algorithm="HS256")

    return jsonify({
        "access_token": token,
        "rol": nuevo.rol,
        "email": nuevo.email,
        "usuario": {
            "id": nuevo.id,
            "nombre": nuevo.nombre,
            "email": nuevo.email,
            "rol": nuevo.rol,
            "fecha_registro": nuevo.fecha_registro
        }
    }), 201

from flask_cors import cross_origin

@pedidos_blueprint.route('/pizzas', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_pizzas():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    from models.producto import Producto, Categoria

    if request.method == 'POST':
        try:
            data = request.get_json()
            categoria_nombre = data.get('categoria', 'Pizza')
            
            # Buscar o crear categoría
            cat = Categoria.query.filter_by(nombre=categoria_nombre).first()
            if not cat:
                cat = Categoria(nombre=categoria_nombre)
                db.session.add(cat)
                db.session.commit()
                
            nuevo_prod = Producto(
                nombre=data.get('nombre'),
                descripcion=data.get('descripcion', ''),
                precio_1=data.get('precio_1', data.get('precio', 0.0)),
                precio_2=data.get('precio_2'),
                precio_3=data.get('precio_3'),
                categoria_id=cat.id
            )
            db.session.add(nuevo_prod)
            db.session.commit()
            
            return jsonify({
                "id": nuevo_prod.id,
                "nombre": nuevo_prod.nombre,
                "categoria": cat.nombre,
                "precio_1": nuevo_prod.precio_1,
                "precio_2": nuevo_prod.precio_2,
                "precio_3": nuevo_prod.precio_3
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    try:
        productos = Producto.query.all()
        pizzas_json = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "precio_1": float(p.precio_1) if p.precio_1 is not None else None,
                "precio_2": float(p.precio_2) if p.precio_2 is not None else None,
                "precio_3": float(p.precio_3) if p.precio_3 is not None else None,
                "categoria": p.categoria.nombre if p.categoria else "Pizza"
            } for p in productos
        ]
        return jsonify(pizzas_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/insumos', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_insumos():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    if request.method == 'POST':
        data = request.get_json() or {}
        precio_val = float(data.get('precio_unidad', data.get('precio', 0)) or 0)
        nuevo = Insumo(
            nombre=data.get('nombre'),
            cantidad=int(data.get('cantidad', 0)),
            unidad_medida=data.get('unidad_medida', 'gr'),
            stock_minimo=float(data.get('stock_minimo', 0) or 0),
            precio=precio_val,
            precio_unidad=precio_val
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify(nuevo.to_dict()), 201

    try:
        insumos = Insumo.query.order_by(Insumo.nombre).all()
        return jsonify([i.to_dict() for i in insumos])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/insumos/<int:id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_actualizar_insumo(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    insumo = Insumo.query.get_or_404(id)
    data = request.get_json() or {}
    if 'cantidad' in data:
        insumo.cantidad = int(data['cantidad'])
    if 'precio_unidad' in data:
        precio = float(data['precio_unidad'] or 0)
        insumo.precio_unidad = precio
        insumo.precio = precio          # mantener retrocompat.
    if 'stock_minimo' in data:
        insumo.stock_minimo = float(data['stock_minimo'] or 0)
    if 'nombre' in data:
        insumo.nombre = data['nombre']
    if 'unidad_medida' in data:
        insumo.unidad_medida = data['unidad_medida']
    db.session.commit()
    return jsonify(insumo.to_dict()), 200

@pedidos_blueprint.route('/insumos/<int:id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_eliminar_insumo(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    insumo = Insumo.query.get_or_404(id)
    db.session.delete(insumo)
    db.session.commit()
    return jsonify({"status": "ok", "mensaje": "Insumo eliminado"}), 200

from flask_cors import cross_origin

@pedidos_blueprint.route('/pizzas/<int:id>', methods=['PUT', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True, methods=['PUT', 'OPTIONS'])
def api_actualizar_pizza(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    from models.producto import Producto
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        data = request.get_json() or {}
        if 'nombre' in data:
            producto.nombre = data['nombre']
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        if 'precio_1' in data:
            producto.precio_1 = float(data['precio_1']) if data['precio_1'] is not None else None
        if 'precio_2' in data:
            producto.precio_2 = float(data['precio_2']) if data['precio_2'] is not None else None
        if 'precio_3' in data:
            producto.precio_3 = float(data['precio_3']) if data['precio_3'] is not None else None
        if 'categoria' in data:
            from models.producto import Categoria
            cat = Categoria.query.filter_by(nombre=data['categoria']).first()
            if not cat:
                cat = Categoria(nombre=data['categoria'])
                db.session.add(cat)
                db.session.flush()
            producto.categoria_id = cat.id

        db.session.commit()
        return jsonify({
            "status": "ok",
            "id": producto.id,
            "nombre": producto.nombre,
            "descripcion": producto.descripcion,
            "precio_1": float(producto.precio_1) if producto.precio_1 is not None else None,
            "precio_2": float(producto.precio_2) if producto.precio_2 is not None else None,
            "precio_3": float(producto.precio_3) if producto.precio_3 is not None else None,
            "categoria": producto.categoria.nombre if producto.categoria else None
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/pizzas/<int:id>', methods=['DELETE', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True, methods=['DELETE', 'OPTIONS'])
def api_eliminar_pizza(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    from models.producto import Producto
    try:
        producto = Producto.query.get(id)
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404
        db.session.delete(producto)
        db.session.commit()
        return jsonify({"status": "ok", "mensaje": "Producto eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/pizzas/<int:id>/receta', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin(origins="http://localhost:4200", supports_credentials=True)
def api_receta(id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    from models.producto import RecetaItem
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            # El frontend enviará el tamaño seleccionado
            from models.producto import SizeEnum
            requested_size_str = request.args.get('size', 'Pequeña')
            try:
                requested_size = next(s for s in SizeEnum if s.value == requested_size_str)
            except StopIteration:
                requested_size = SizeEnum.PEQUENA
            
            # Borrar receta anterior de este producto PARA ESTE TAMAÑO SOLAMENTE
            RecetaItem.query.filter_by(producto_id=id, size=requested_size).delete()
            
            # Insertar los nuevos items
            nuevos_items = []
            for item in data:
                nuevo = RecetaItem(
                    producto_id=id,
                    insumo_id=item['insumo_id'],
                    cantidad_gastada=item['cantidad_gastada'],
                    size=requested_size
                )
                db.session.add(nuevo)
                nuevos_items.append(nuevo)
                
            db.session.commit()
            return jsonify({"message": f"Receta para tamaño {requested_size} actualizada"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    try:
        from models.producto import SizeEnum
        requested_size_str = request.args.get('size')
        query = RecetaItem.query.filter_by(producto_id=id)
        if requested_size_str:
            try:
                requested_size = next(s for s in SizeEnum if s.value == requested_size_str)
                query = query.filter_by(size=requested_size)
            except StopIteration:
                pass # Si el tamaño no es válido, no filtramos por tamaño o usamos default
        
        receta_items = query.all()
        receta_json = [
            {
                "pizza_id": r.producto_id,
                "insumo_id": r.insumo_id,
                "insumo_nombre": r.insumo.nombre,
                "cantidad_gastada": float(r.cantidad_gastada),
                "unidad_medida": getattr(r.insumo, 'unidad_medida', 'gr'),
                "size": r.size.value if hasattr(r.size, 'value') else r.size
            } for r in receta_items
        ]
        return jsonify({"receta": receta_json}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
