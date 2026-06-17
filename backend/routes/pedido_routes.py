import json
import logging
import jwt as pyjwt
from flask import Blueprint, jsonify, request
from models.database import db
from models.pedido import Pedido
from models.receta import Receta
from models.insumo import Insumo
from models.configuracion import Configuracion

logger = logging.getLogger(__name__)

# NOTE: La cadena de conexión a PostgreSQL se configura a través de la variable de entorno DATABASE_URL
# en el archivo de configuración (config.py) usando os.getenv('DATABASE_URL').

pedidos_blueprint = Blueprint('pedidos', __name__)
JWT_SECRET = "pizzeria_secret_key_fixed_2026_super_safe"

@pedidos_blueprint.route('/pedidos', methods=['GET'])
def get_pedidos():
    try:
        usuario_id = request.args.get('usuario_id')
        if usuario_id:
            pedidos = Pedido.query.filter_by(cliente_id=int(usuario_id)).all()
        else:
            pedidos = Pedido.query.all()
        return jsonify({"pedidos": [p.serializar() for p in pedidos]}), 200
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(f"❌ [CRÍTICO] Error en GET pedidos:\n{trace}")
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/pedidos', methods=['POST'])
def crear_pedido():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400
    try:
        articulos_brutos = datos.get('articulos') or datos.get('articulos_json') or []
        articulos_str = articulos_brutos if isinstance(articulos_brutos, str) else json.dumps(articulos_brutos)
        # Español: calcular total dinámicamente desde los artículos (server-side) | English: calculate total dynamically from items (server-side)
        try:
            subtotal = sum(
                float(a.get('precio', a.get('precio_unitario', 0))) * float(a.get('cantidad', 1))
                for a in articulos_brutos
            )
            porcentaje_iva = Configuracion.obtener_iva_decimal()
            iva = round(subtotal * porcentaje_iva)
            total_calculado = subtotal + iva
        except Exception:
            subtotal = 0
            iva = 0
            total_calculado = float(datos.get('total', 0))

        # Español: obtener usuario autenticado desde el JWT como fuente autoritativa
        # English: get authenticated user from JWT as authoritative source
        cliente_id = None
        encabezado = request.headers.get('Authorization', '')
        try:
            token = encabezado.split()[1]
            payload = pyjwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            cliente_id = payload.get('id')
        except Exception:
            # Español: fallback al body para compatibilidad | English: body fallback for compatibility
            cliente_id = datos.get('usuario_id') or datos.get('cliente_id')

        if not cliente_id:
            logger.warning('⚠️ Pedido creado sin cliente_id — no hay token JWT ni usuario_id en body')

        nuevo_pedido = Pedido(
            cliente_id=cliente_id,
            articulos_json=articulos_str,
            total=total_calculado,
            estado=datos.get('estado', 'pendiente'),
            # Español: tipo de pedido — 'domicilio' por defecto, 'mesa' si se envía explícitamente | English: order type — default 'domicilio', 'mesa' if explicitly sent
            tipo=datos.get('tipo') or 'domicilio',
            # Español: campos de delivery | English: delivery fields
            direccion_entrega=datos.get('direccion') or datos.get('direccion_entrega', ''),
            telefono_contacto=datos.get('telefono') or datos.get('telefono_contacto', ''),
        )
        db.session.add(nuevo_pedido)
        # Descuento de inventario al crear el pedido
        for art in articulos_brutos:
            try:
                producto_id = art.get('pizza_id') or art.get('id')
                tamano = art.get('tamano')
                cantidad_vendida = float(art.get('cantidad', 1))
                if not producto_id:
                    continue
                if tamano:
                    ingredientes = Receta.query.filter_by(pizza_id=producto_id, tamano=tamano).all()
                else:
                    ingredientes = Receta.query.filter_by(pizza_id=producto_id).all()
                if not ingredientes:
                    insumo_directo = Insumo.query.filter_by(nombre=art.get('nombre')).first()
                    if insumo_directo:
                        insumo_directo.cantidad -= cantidad_vendida
                        db.session.add(insumo_directo)
                    continue
                for ing in ingredientes:
                    insumo = Insumo.query.get(ing.insumo_id)
                    if insumo:
                        descuento = float(ing.cantidad_gastada) * cantidad_vendida
                        insumo.cantidad -= descuento
                        db.session.add(insumo)
            except Exception:
                import traceback
                print(f"❌ Error crítico descontando inventario al crear pedido:\n{traceback.format_exc()}")
        db.session.commit()
        return jsonify(nuevo_pedido.serializar()), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        trace = traceback.format_exc()
        print(f"❌ [CRÍTICO] Error al guardar pedido en BD:\n{trace}")
        return jsonify({"error": "Error interno del servidor al procesar el pedido", "detalles": str(e)}), 500

@pedidos_blueprint.route('/pedidos/<int:pedido_id>/estado', methods=['PATCH', 'OPTIONS'])
def actualizar_estado_pedido(pedido_id):
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    datos = request.get_json()
    nuevo_estado = datos.get('estado', '').upper()
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({"error": "Pedido no encontrado"}), 404
        estado_anterior = pedido.estado.upper()
        pedido.estado = nuevo_estado
        # Descuento de inventario al pasar a ENTREGADO o PAGADO
        if nuevo_estado in ('ENTREGADO', 'PAGADO') and estado_anterior not in ('ENTREGADO', 'PAGADO'):
            articulos = []
            try:
                articulos = json.loads(pedido.articulos_json) if pedido.articulos_json else []
            except:
                articulos = pedido.articulos_json if isinstance(pedido.articulos_json, list) else []
            for art in articulos:
                try:
                    producto_id = art.get('pizza_id') or art.get('id')
                    tamano = art.get('tamano')
                    cantidad_vendida = art.get('cantidad', 1)
                    if not producto_id:
                        continue
                    if tamano:
                        ingredientes = Receta.query.filter_by(pizza_id=producto_id, tamano=tamano).all()
                    else:
                        ingredientes = Receta.query.filter_by(pizza_id=producto_id).all()
                    if not ingredientes:
                        insumo_directo = Insumo.query.filter_by(nombre=art.get('nombre')).first()
                        if insumo_directo:
                            insumo_directo.cantidad -= float(cantidad_vendida)
                            db.session.add(insumo_directo)
                        continue
                    for ing in ingredientes:
                        insumo = Insumo.query.get(ing.insumo_id)
                        if insumo:
                            descuento = float(ing.cantidad_gastada) * float(cantidad_vendida)
                            insumo.cantidad -= descuento
                            db.session.add(insumo)
                except Exception:
                    import traceback
                    print(f"❌ Error crítico al descontar receta de '{art.get('nombre')}':\n{traceback.format_exc()}")
        db.session.add(pedido)
        db.session.commit()
        return jsonify(pedido.serializar()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar pedido: {e}")
        return jsonify({"error": str(e)}), 500