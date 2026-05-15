import json
from flask import Blueprint, jsonify, request
from models.database import db
from models.pedido import Pedido 
from models.receta import Receta
from models.insumo import Insumo

# Cambiamos el nombre interno para evitar conflictos
pedidos_blueprint = Blueprint('pedidos', __name__)

@pedidos_blueprint.route('/pedidos', methods=['GET'])
def get_pedidos():
    try:
        # Traemos todos los pedidos de la DB
        pedidos = Pedido.query.all()
        # Si .serializar() falla, esto dará error 500. 
        # Asegúrate de que el modelo Pedido tenga def serializar(self):
        return jsonify([p.serializar() for p in pedidos]), 200
    except Exception as e:
        print(f"Error crítico en GET pedidos: {e}")
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/pedidos', methods=['POST'])
def crear_pedido():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400
    try:
        nuevo_pedido = Pedido(
            cliente_id=datos.get('cliente_id'),
            articulos_json=datos.get('articulos_json'),
            total=datos.get('total'),
            estado=datos.get('estado', 'pendiente')
        )
        db.session.add(nuevo_pedido)
        db.session.commit()
        return jsonify(nuevo_pedido.serializar()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear pedido: {e}")
        return jsonify({"error": str(e)}), 500

@pedidos_blueprint.route('/pedidos/<int:pedido_id>', methods=['PUT'])
def actualizar_estado_pedido(pedido_id):
    datos = request.get_json()
    nuevo_estado = datos.get('estado', '').upper()
    
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({"error": "Pedido no encontrado"}), 404
        
        estado_anterior = pedido.estado.upper()
        pedido.estado = nuevo_estado
        
        # LÓGICA DE DESCUENTO DE INVENTARIO
        # Solo se dispara si el nuevo estado es ENTREGADO y antes no lo estaba
        if nuevo_estado == 'ENTREGADO' and estado_anterior != 'ENTREGADO':
            print(f"📦 [Inventario] Procesando descuento para Pedido #{pedido_id}")
            
            # Parseamos los artículos (vienen como string JSON en la DB)
            articulos = []
            try:
                articulos = json.loads(pedido.articulos_json) if pedido.articulos_json else []
            except:
                # Si ya es un objeto (por alguna razón), lo usamos
                articulos = pedido.articulos_json if isinstance(pedido.articulos_json, list) else []

            for art in articulos:
                pizza_id = art.get('id')
                tamano = art.get('tamano')
                cantidad_vendida = art.get('cantidad', 1)
                
                if not pizza_id or not tamano:
                    continue
                
                # Buscamos la receta para este producto y tamaño
                ingredientes = Receta.query.filter_by(pizza_id=pizza_id, tamano=tamano).all()
                
                if not ingredientes:
                    print(f"⚠️ [Inventario] Sin receta para {art.get('nombre')} ({tamano})")
                    continue
                
                for ing in ingredientes:
                    insumo = Insumo.query.get(ing.insumo_id)
                    if insumo:
                        descuento = ing.cantidad_gastada * cantidad_vendida
                        insumo.cantidad -= descuento
                        print(f"📉 [Inventario] Descontado {descuento} {insumo.unidad} de {insumo.nombre}")
        
        db.session.commit()
        return jsonify(pedido.serializar()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar pedido: {e}")
        return jsonify({"error": str(e)}), 500