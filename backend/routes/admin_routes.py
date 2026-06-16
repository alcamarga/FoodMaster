import os
import uuid
import logging
from flask import Blueprint, jsonify, request as flask_request, send_from_directory
from models.database import db

# Español: configuración de logging | English: logging setup
logger = logging.getLogger(__name__)
from models.usuario import Usuario
from models.insumo import Insumo 
from models.producto import Producto, SizeEnum
from models.receta import Receta
from models.grupo_producto import GrupoProducto
from models.mesa import Mesa
from models.comanda import Comanda
from flask_cors import cross_origin
import jwt as pyjwt
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

# Configuración de subida de imágenes | Image upload configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

# Español: ruta individual de usuario (editar/eliminar) | English: individual user route (update/delete)
@admin_bp.route('/usuarios/<int:usuario_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin()
def gestionar_usuario_individual(usuario_id):
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # PUT: Actualizar empleado
    if flask_request.method == 'PUT':
        try:
            datos = flask_request.get_json()
            if not datos:
                return jsonify({'error': 'Datos inválidos'}), 400

            usuario.nombre = datos.get('nombre', usuario.nombre)
            usuario.email = datos.get('email', usuario.email)
            usuario.rol = datos.get('rol', usuario.rol)

            pass_plana = datos.get('password')
            if pass_plana:
                usuario.contrasena_hash = generate_password_hash(pass_plana)

            db.session.commit()
            logger.info('👤 Usuario #%s actualizado: %s (%s)', usuario.id, usuario.nombre, usuario.rol)
            return jsonify({
                'mensaje': 'Empleado actualizado con éxito',
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'rol': usuario.rol
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.exception('Error al actualizar usuario #%s: %s', usuario_id, e)
            return jsonify({'error': str(e)}), 500

    # DELETE: Eliminar empleado
    if flask_request.method == 'DELETE':
        try:
            db.session.delete(usuario)
            db.session.commit()
            logger.info('👤 Usuario #%s eliminado: %s', usuario.id, usuario.nombre)
            return jsonify({'mensaje': 'Empleado eliminado correctamente'}), 200
        except Exception as e:
            db.session.rollback()
            logger.exception('Error al eliminar usuario #%s: %s', usuario_id, e)
            return jsonify({'error': str(e)}), 500

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

# --- RUTAS DE PRODUCTOS ---
@admin_bp.route('/productos', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def get_productos():
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

            import json
            tags_raw = datos.get('tags')
            tags_json = json.dumps(tags_raw, ensure_ascii=False) if isinstance(tags_raw, list) else '[]'

            nuevo = Producto(
                nombre=datos.get('nombre'),
                descripcion=datos.get('descripcion'),
                categoria=datos.get('categoria', 'General'),
                tags=tags_json,
                imagen_url=datos.get('imagen_url', ''),
                precio_pequena=safe_float(datos.get('precio_1') or datos.get('precio_personal')),
                precio_mediana=safe_float(datos.get('precio_2') or datos.get('precio_mediano')),
                precio_grande=safe_float(datos.get('precio_3') or datos.get('precio_familiar')),
                precio_base=safe_float(datos.get('precio_1') or datos.get('precio_personal'))
            )


            db.session.add(nuevo)
            db.session.commit()

            # Español: verificar conexión con InventoryGuard | English: verify InventoryGuard connection
            insumos_asociados = Insumo.query.filter(Insumo.nombre.ilike(f'%{nuevo.nombre}%')).count()
            if insumos_asociados == 0:
                logger.info(
                    '📦 Producto #%s "%s" creado sin insumos asociados. '
                    'InventoryGuard: registrar receta en /api/productos/%s/receta para habilitar control de stock.',
                    nuevo.id, nuevo.nombre, nuevo.id
                )
            else:
                logger.info(
                    '📦 Producto #%s "%s" creado con %d insumo(s) asociado(s). InventoryGuard: OK.',
                    nuevo.id, nuevo.nombre, insumos_asociados
                )

            return jsonify(nuevo.serializar()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    pizzas = Producto.query.all()
    return jsonify([p.serializar() for p in pizzas]), 200

@admin_bp.route('/productos/<int:producto_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
@cross_origin()
def gestionar_producto_especifico(producto_id):
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    
    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    # ACTUALIZAR (PUT)
    if flask_request.method == 'PUT':
        try:
            datos = flask_request.get_json()
            import json
            producto.nombre = datos.get('nombre', producto.nombre)
            producto.descripcion = datos.get('descripcion', producto.descripcion)
            producto.categoria = datos.get('categoria', producto.categoria)

            # Español: actualizar etiquetas tags si se enviaron | English: update tags if provided
            if 'tags' in datos:
                tags_raw = datos.get('tags')
                producto.tags = json.dumps(tags_raw, ensure_ascii=False) if isinstance(tags_raw, list) else '[]'

            # Español: actualizar URL de imagen si se envió | English: update image URL if provided
            if 'imagen_url' in datos:
                producto.imagen_url = datos.get('imagen_url', '')

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
@admin_bp.route('/productos/<int:producto_id>/receta', methods=['GET', 'POST', 'OPTIONS'])
@cross_origin()
def gestionar_receta(producto_id):
    if flask_request.method == 'OPTIONS': return jsonify({}), 200
    tamano = flask_request.args.get('size', 'Pequeña')

    if flask_request.method == 'GET':
        try:
            ingredientes = Receta.query.filter_by(pizza_id=producto_id, tamano=tamano).all()
            return jsonify([item.to_dict() for item in ingredientes]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    if flask_request.method == 'POST':
        try:
            datos = flask_request.get_json()
            Receta.query.filter_by(pizza_id=producto_id, tamano=tamano).delete()
            for item in datos:
                nueva_linea = Receta(
                    pizza_id=producto_id,
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

# --- RESET DE MESA (ADMIN) ---
@admin_bp.route('/admin/reset-mesa/<int:mesa_id>', methods=['POST'])
@cross_origin()
def reset_mesa_admin(mesa_id: int):
    """
    POST /api/admin/reset-mesa/<id> — Fuerza el estado de una mesa a LIBRE y elimina
    cualquier comanda huérfana (abierta) asociada. Requiere autenticación de administrador.
    """
    try:
        # Validar token de administrador
        payload, error = _verificar_token_admin()
        if error:
            return jsonify({'status': 'error', 'message': 'Se requiere autenticación de administrador'}), 401

        mesa = Mesa.query.get(mesa_id)
        if not mesa:
            return jsonify({'status': 'error', 'message': f'Mesa #{mesa_id} no encontrada'}), 404

        # Español: buscar comandas huérfanas (abiertas o pagadas sin liberar) | English: find orphan comandas (open or paid without release)
        comandas_activas = Comanda.query.filter_by(mesa_id=mesa_id, estado='abierta').all()
        for comanda in comandas_activas:
            comanda.estado = 'cerrada'
            logger.info('🔒 Comanda #%s cerrada por reset administrativo', comanda.id)

        # Forzar estado de la mesa a LIBRE
        estado_anterior = mesa.estado
        mesa.estado = 'LIBRE'
        db.session.commit()

        logger.info('🔄 Reset de mesa #%s completado: %s → LIBRE, %d comanda(s) cerrada(s)',
                     mesa_id, estado_anterior, len(comandas_activas))

        return jsonify({
            'status': 'success',
            'message': f'Mesa #{mesa_id} reseteada a LIBRE. {len(comandas_activas)} comanda(s) cerrada(s).',
            'mesa': mesa.to_dict(),
            'comandas_cerradas': len(comandas_activas),
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al resetear mesa %s: %s', mesa_id, e)
        return jsonify({'status': 'error', 'message': 'Error al resetear la mesa'}), 500

# --- SUBIDA DE IMÁGENES (PRODUCTOS) ---
@admin_bp.route('/upload', methods=['POST', 'OPTIONS'])
@cross_origin()
def subir_imagen():
    """
    POST /api/upload — Sube una imagen para un producto y devuelve la URL.
    Body: multipart/form-data con campo 'file'
    Retorna: { "status": "success", "url": "/static/uploads/imagen.jpg" }
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        if 'file' not in flask_request.files:
            return jsonify({'status': 'error', 'message': 'No se envió ningún archivo'}), 400

        archivo = flask_request.files['file']
        if archivo.filename == '' or not archivo.filename:
            return jsonify({'status': 'error', 'message': 'Nombre de archivo vacío'}), 400

        # Validar extensión | Validate extension
        ext = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'status': 'error', 'message': f'Extensión no permitida: {ext}. Use: {ALLOWED_EXTENSIONS}'}), 400

        # Español: generar nombre único para evitar colisiones | English: generate unique name to avoid collisions
        nombre_unico = f'{uuid.uuid4().hex}.{ext}'
        ruta_completa = os.path.join(UPLOAD_FOLDER, nombre_unico)
        archivo.save(ruta_completa)

        # Español: devolver URL completa con host del backend | English: return full URL with backend host
        url_imagen = f'{flask_request.host_url.rstrip("/")}/static/uploads/{nombre_unico}'
        logger.info('🖼️ Imagen subida: %s', url_imagen)

        return jsonify({'status': 'success', 'url': url_imagen}), 201

    except Exception as e:
        logger.exception('Error al subir imagen: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al subir la imagen'}), 500

# --- LIMPIAR MESA (ADMIN) — versión GET para diagnóstico ---
@admin_bp.route('/admin/limpiar-mesa/<int:mesa_id>', methods=['GET'])
@cross_origin()
def limpiar_mesa_admin(mesa_id: int):
    """
    GET /api/admin/limpiar-mesa/<id> — Diagnostica y fuerza el estado de una mesa a LIBRE.
    Cierra cualquier comanda activa asociada. No requiere autenticación para facilitar
    diagnóstico rápido desde el navegador.
    """
    try:
        mesa = Mesa.query.get(mesa_id)
        if not mesa:
            return jsonify({'status': 'error', 'message': f'Mesa #{mesa_id} no encontrada'}), 404

        # Español: diagnosticar estado actual | English: diagnose current state
        comandas_activas = Comanda.query.filter_by(mesa_id=mesa_id, estado='abierta').all()
        resultado = {
            'mesa_id': mesa.id,
            'numero_mesa': mesa.numero_mesa,
            'estado_anterior': mesa.estado,
            'comandas_abiertas': len(comandas_activas),
            'accion': 'ninguna',
        }

        if mesa.estado == 'LIBRE' and len(comandas_activas) == 0:
            resultado['mensaje'] = 'La mesa ya está libre y sin comandas activas. No requiere acción.'
            return jsonify({'status': 'ok', 'resultado': resultado}), 200

        # Forzar limpieza | Force cleanup
        for comanda in comandas_activas:
            comanda.estado = 'cerrada'
            logger.info('🔒 Comanda #%s cerrada por limpieza administrativa', comanda.id)

        estado_anterior = mesa.estado
        mesa.estado = 'LIBRE'
        db.session.commit()

        resultado['estado_anterior'] = estado_anterior
        resultado['accion'] = 'limpiada'
        resultado['mensaje'] = f'Mesa #{mesa_id} liberada. {len(comandas_activas)} comanda(s) cerrada(s).'

        logger.info('🧹 Limpieza de mesa #%s: %s → LIBRE, %d comanda(s)',
                     mesa_id, estado_anterior, len(comandas_activas))

        return jsonify({'status': 'success', 'resultado': resultado}), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al limpiar mesa %s: %s', mesa_id, e)
        return jsonify({'status': 'error', 'message': 'Error al limpiar la mesa'}), 500

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

        # Obtener etiquetas desde la base de datos (grupos dinámicos) | Get labels from DB (dynamic groups)
        grupos_db = {g.nombre: g for g in GrupoProducto.query.all()}

        def get_etiquetas(grupo_nombre):
            grupo = grupos_db.get(grupo_nombre)
            if grupo:
                etiquetas = grupo.obtener_etiquetas()
                while len(etiquetas) < 3:
                    etiquetas.append('')
                return etiquetas
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