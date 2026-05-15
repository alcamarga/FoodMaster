from flask import Blueprint, jsonify, request as flask_request
from models.database import db
from models.usuario import Usuario
from models.insumo import Insumo 
from models.producto import Producto, SizeEnum
from models.receta import Receta 
from flask_cors import cross_origin
import jwt as pyjwt
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__)
JWT_SECRET_USUARIOS = "pizzeria_secret_key_fixed_2026_super_safe"

# --- UTILIDADES ---
def _verificar_token_admin():
    encabezado = flask_request.headers.get('Authorization', '')
    try:
        token = encabezado.split()[1]
        payload = pyjwt.decode(token, JWT_SECRET_USUARIOS, algorithms=['HS256'])
        return payload, None
    except:
        return None, (jsonify({'error': 'Token requerido o inválido'}), 401)

# --- RUTAS DE USUARIOS / EMPLEADOS ---
@admin_bp.route('/usuarios', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def gestionar_usuarios():
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    
    # Comentamos la verificación de token temporalmente para facilitar tus pruebas
    # payload, err = _verificar_token_admin()
    # if err: return err
    
    if flask_request.method == 'POST':
        try:
            datos = flask_request.get_json()
            nuevo = Usuario(
                nombre=datos.get('nombre'), 
                email=datos.get('email'), 
                rol=datos.get('rol', 'cocinero')
            )
            pass_plana = datos.get('password')
            if pass_plana:
                nuevo.contrasena_hash = generate_password_hash(pass_plana)
            db.session.add(nuevo)
            db.session.commit()
            return jsonify({'mensaje': 'Empleado creado'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
            
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id, 
        'nombre': u.nombre, 
        'email': u.email, 
        'rol': u.rol
    } for u in usuarios])

# --- RUTAS DE INSUMOS ---
@admin_bp.route('/insumos', methods=['GET', 'POST', 'OPTIONS'])
@admin_bp.route('/insumos/<int:insumo_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin()
def gestionar_insumos(insumo_id=None):
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    
    # GET: Listar todos
    if flask_request.method == 'GET':
        try:
            todos = Insumo.query.all()
            return jsonify([i.to_dict() for i in todos]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # POST: Crear nuevo
    if flask_request.method == 'POST':
        try:
            datos = flask_request.get_json()
            precio_val = datos.get('precio_unitario') or datos.get('precio') or 0
            nuevo = Insumo(
                nombre=datos.get('nombre'),
                cantidad=float(datos.get('cantidad', 0)),
                unidad=datos.get('unidad') or datos.get('unidad_medida') or 'gr',

                precio_unitario=float(precio_val),
                stock_minimo=float(datos.get('stock_minimo', 0))
            )
            db.session.add(nuevo)
            db.session.commit()
            return jsonify(nuevo.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # PUT: Actualizar
    if flask_request.method == 'PUT' and insumo_id:
        try:
            insumo = Insumo.query.get(insumo_id)
            if not insumo: return jsonify({'error': 'No encontrado'}), 404
            datos = flask_request.get_json()
            insumo.nombre = datos.get('nombre', insumo.nombre)
            insumo.cantidad = float(datos.get('cantidad', insumo.cantidad))
            # Capturamos 'unidad' o 'unidad_medida' para sincronizar con el Front
            if 'unidad' in datos:
                insumo.unidad = datos['unidad']
            elif 'unidad_medida' in datos:
                insumo.unidad = datos['unidad_medida']

            if 'precio_unitario' in datos or 'precio' in datos:
                insumo.precio_unitario = float(datos.get('precio_unitario') or datos.get('precio'))
            insumo.stock_minimo = float(datos.get('stock_minimo', insumo.stock_minimo))
            db.session.commit()
            return jsonify({'mensaje': 'Actualizado'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # DELETE: Borrar
    if flask_request.method == 'DELETE' and insumo_id:
        insumo = Insumo.query.get(insumo_id)
        if insumo:
            db.session.delete(insumo)
            db.session.commit()
            return jsonify({'mensaje': 'Eliminado'}), 200
        return jsonify({'error': 'No encontrado'}), 404

# --- RUTAS DE PIZZAS / PRODUCTOS ---
@admin_bp.route('/pizzas', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def get_pizzas():
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    
    if flask_request.method == 'POST':
        try:
            datos = flask_request.get_json()
            
            # Helper para conversión segura
            def safe_float(v):
                try:
                    return float(v) if v is not None and v != "" else 0.0
                except:
                    return 0.0

            nuevo = Producto(
                nombre=datos.get('nombre'),
                descripcion=datos.get('descripcion'),
                categoria=datos.get('categoria', 'Pizza'),
                precio_pequena=safe_float(datos.get('precio_1') or datos.get('precio_personal')),
                precio_mediana=safe_float(datos.get('precio_2') or datos.get('precio_mediano')),
                precio_grande=safe_float(datos.get('precio_3') or datos.get('precio_familiar')),
                precio_base=safe_float(datos.get('precio_1') or datos.get('precio_personal'))
            )


            db.session.add(nuevo)
            db.session.commit()
            return jsonify(nuevo.serializar()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    pizzas = Producto.query.all()
    return jsonify([p.serializar() for p in pizzas]), 200

@admin_bp.route('/pizzas/<int:pizza_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin()
def gestionar_producto_especifico(pizza_id):
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    
    producto = Producto.query.get(pizza_id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    # ACTUALIZAR (PUT)
    if flask_request.method == 'PUT':
        try:
            datos = flask_request.get_json()
            producto.nombre = datos.get('nombre', producto.nombre)
            producto.descripcion = datos.get('descripcion', producto.descripcion)
            producto.categoria = datos.get('categoria', producto.categoria)
            
            # Mapeo de precios desde el Frontend (Soporta ambos estilos)
            # Usamos un helper para conversión segura y evitar Error 500
            def safe_float(v):
                try:
                    return float(v) if v is not None and v != "" else 0.0
                except:
                    return 0.0

            if 'precio_1' in datos or 'precio_personal' in datos:
                val = datos.get('precio_1') or datos.get('precio_personal')
                producto.precio_pequena = safe_float(val)
                producto.precio_base = producto.precio_pequena
            
            if 'precio_2' in datos or 'precio_mediano' in datos:
                val = datos.get('precio_2') or datos.get('precio_mediano')
                producto.precio_mediana = safe_float(val)
            
            if 'precio_3' in datos or 'precio_familiar' in datos:
                val = datos.get('precio_3') or datos.get('precio_familiar')
                producto.precio_grande = safe_float(val)


            db.session.commit()
            return jsonify({'mensaje': '¡Actualizado con éxito!'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # ELIMINAR (DELETE)
    if flask_request.method == 'DELETE':
        try:
            db.session.delete(producto)
            db.session.commit()
            return jsonify({'mensaje': 'Producto eliminado correctamente'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# --- RUTAS DE RECETAS ---
@admin_bp.route('/pizzas/<int:pizza_id>/receta', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def gestionar_receta(pizza_id):
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    tamano = flask_request.args.get('size', 'Pequeña')

    if flask_request.method == 'GET':
        try:
            ingredientes = Receta.query.filter_by(pizza_id=pizza_id, tamano=tamano).all()
            return jsonify([item.to_dict() for item in ingredientes]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    if flask_request.method == 'POST':
        try:
            datos = flask_request.get_json()
            Receta.query.filter_by(pizza_id=pizza_id, tamano=tamano).delete()
            for item in datos:
                nueva_linea = Receta(
                    pizza_id=pizza_id,
                    insumo_id=item['insumo_id'],
                    tamano=tamano,
                    cantidad_gastada=item['cantidad_gastada']
                )
                db.session.add(nueva_linea)
            db.session.commit()
            return jsonify({'mensaje': 'Receta guardada'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# --- RENTABILIDAD ---
@admin_bp.route('/admin/rentabilidad', methods=['GET', 'OPTIONS'])
@cross_origin()
def get_rentabilidad():
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    
    # Capturamos el tamaño del Front
    tamano_solicitado = flask_request.args.get('size', None)

    # Mapeo de equivalencias para que el Front cargue todo correctamente
    equivalencias = {
        'Pequeña': ['Pequeña', 'Personal'],
        'Mediana': ['Mediana', 'Litro'],
        'Familiar': ['Familiar', 'Grande']
    }

    
    # Obtenemos la lista de etiquetas aceptadas según el filtro solicitado
    etiquetas_aceptadas = equivalencias.get(tamano_solicitado, [tamano_solicitado]) if tamano_solicitado else None
    
    try:
        productos = Producto.query.all()
        resultado = []

        def get_etiquetas(cat):
            if cat == 'Pizza': return ['Personal', 'Mediana', 'Familiar']
            if cat == 'Gaseosa': return ['Personal', 'Litro', 'Familiar']
            if cat == 'Lasaña': return ['Pequeña', 'Grande', '']
            return ['Único', '', '']

        for p in productos:
            etiquetas = get_etiquetas(p.categoria)
            opciones = [
                {'nombre': etiquetas[0], 'precio': p.precio_pequena},
                {'nombre': etiquetas[1], 'precio': p.precio_mediana},
                {'nombre': etiquetas[2], 'precio': p.precio_grande}
            ]

            for opt in opciones:
                if not opt['precio'] or opt['precio'] <= 0 or not opt['nombre']:
                    continue
                
                # Filtrado flexible: si hay filtro, buscamos en la lista de equivalencias
                if etiquetas_aceptadas and opt['nombre'] not in etiquetas_aceptadas:
                    continue

                
                receta_items = Receta.query.filter_by(pizza_id=p.id, tamano=opt['nombre']).all()
                
                costo_insumos = 0
                for item in receta_items:
                    if item.insumo:
                        costo_insumos += item.cantidad_gastada * item.insumo.precio_unitario
                
                ganancia_neta = float(opt['precio']) - costo_insumos
                porcentaje_margen = (ganancia_neta / float(opt['precio'])) * 100 if opt['precio'] > 0 else 0

                resultado.append({
                    'id': p.id,
                    'nombre': p.nombre,
                    'categoria': p.categoria,
                    'tamano': opt['nombre'],
                    'costo_produccion': round(costo_insumos, 2),
                    'precio_venta': float(opt['precio']),
                    'ganancia': round(ganancia_neta, 2),
                    'margen_porcentaje': round(porcentaje_margen, 2)
                })


        resumen = {
            'total_items': len(resultado),
            'margen_promedio': round(sum(i['margen_porcentaje'] for i in resultado) / len(resultado), 2) if resultado else 0,
            'tamano_filtrado': tamano_solicitado
        }


        return jsonify({
            'productos': resultado,
            'resumen': resumen
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500