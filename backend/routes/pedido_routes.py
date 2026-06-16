import json
from flask import Blueprint, jsonify, request
from models.database import db
from models.pedido import Pedido
from models.receta import Receta
from models.insumo import Insumo

# NOTE: La cadena de conexión a PostgreSQL se configura a través de la variable de entorno DATABASE_URL
# en el archivo de configuración (config.py) usando os.getenv('DATABASE_URL').

pedidos_blueprint = Blueprint('pedidos', __name__)

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
        nuevo_pedido = Pedido(
            cliente_id=datos.get('usuario_id') or datos.get('cliente_id'),
            articulos_json=articulos_str,
            total=datos.get('total'),
            estado=datos.get('estado', 'pendiente'),
            # Español: tipo de pedido (domicilio por defecto desde el flujo de compra) | English: order type (delivery by default from purchase flow)
            tipo='domicilio',
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
        # Descuento de inventario solo al pasar a ENTREGADO
        if nuevo_estado == 'ENTREGADO' and estado_anterior != 'ENTREGADO':
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