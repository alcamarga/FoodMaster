# routes/kitchen_routes.py — Endpoints unificados para el panel de cocina (KDS)
# Español: muestra pedidos de Mesa (comandas) y Domicilio en una sola vista
# English: unified Kitchen Display System showing both Dine-in (comandas) and Delivery orders

import json
import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request

from models.database import db
from models.comanda import Comanda
from models.pedido import Pedido

logger = logging.getLogger(__name__)

kitchen_bp = Blueprint('kitchen', __name__)

JWT_SECRET_KITCHEN = "pizzeria_secret_key_fixed_2026_super_safe"


def roles_requeridos_cocina(*roles_permitidos: str):
    """
    Decorador que verifica que el token JWT contenga un rol permitido.
    Uso: @roles_requeridos_cocina('admin', 'cocinero')
    """
    import jwt as pyjwt

    def decorador(func):
        @wraps(func)
        def envoltura(*args, **kwargs):
            encabezado = request.headers.get('Authorization', '')
            try:
                token = encabezado.split()[1]
                payload = pyjwt.decode(token, JWT_SECRET_KITCHEN, algorithms=['HS256'])
                rol_usuario = payload.get('rol', '')
                if rol_usuario not in roles_permitidos:
                    return jsonify({'status': 'error', 'message': f'Acceso denegado al Monitor de Cocina. Se requiere rol: {roles_permitidos}'}), 403
                return func(*args, **kwargs)
            except IndexError:
                return jsonify({'status': 'error', 'message': 'Token requerido en header Authorization'}), 401
            except pyjwt.ExpiredSignatureError:
                return jsonify({'status': 'error', 'message': 'Token expirado'}), 401
            except pyjwt.InvalidTokenError:
                return jsonify({'status': 'error', 'message': 'Token inválido'}), 401
        return envoltura
    return decorador

# ---------------------------------------------------------------------------
# Mapa de estados: estados internos del modelo → estados de cocina
# Internal model states → kitchen display states
# ---------------------------------------------------------------------------
# Comanda:
#   'abierta'           → 'pendiente'
#   'en_preparacion'    → 'en_preparacion'
#   'listo'             → 'despachado'
#
# Pedido (tipo='domicilio'):
#   'pendiente'         → 'pendiente'
#   'en_preparacion'    → 'en_preparacion'
#   'listo'             → 'despachado'
# ---------------------------------------------------------------------------

ESTADO_COCINA_PENDIENTE = 'pendiente'
ESTADO_COCINA_PREPARACION = 'en_preparacion'
ESTADO_COCINA_DESPACHADO = 'despachado'

# Estados del modelo que corresponden a cada estado de cocina
ESTADOS_PENDIENTES_MODELO = {  # Se muestran como 'pendiente' en cocina
    'comanda': {'abierta'},
    'pedido': {'pendiente'},
}
ESTADOS_PREPARACION_MODELO = {  # Se muestran como 'en_preparacion'
    'comanda': {'en_preparacion'},
    'pedido': {'en_preparacion'},
}
ESTADOS_DESPACHADOS_MODELO = {  # Se muestran como 'despachado'
    'comanda': {'listo'},
    'pedido': {'listo'},
}

# NOTA: MODEL_ESTADOS_COCINA eliminado — no se usa en queries.
# Las queries usan _estados_modelo_para_cocina() que excluye 'despachado'.


def _mapear_estado_cocina(tipo: str, estado_modelo: str) -> str:
    """Mapea un estado interno del modelo al estado de cocina correspondiente."""
    if estado_modelo in ESTADOS_PENDIENTES_MODELO.get(tipo, set()):
        return ESTADO_COCINA_PENDIENTE
    if estado_modelo in ESTADOS_PREPARACION_MODELO.get(tipo, set()):
        return ESTADO_COCINA_PREPARACION
    if estado_modelo in ESTADOS_DESPACHADOS_MODELO.get(tipo, set()):
        return ESTADO_COCINA_DESPACHADO
    return estado_modelo


def _estados_modelo_para_cocina(tipo: str) -> set:
    """
    Retorna los estados del modelo que deben mostrarse en el Monitor de Cocina.
    SOLO incluye estados activos: pendiente + en_preparacion.
    Los items 'despachado' (modelo 'listo') se excluyen del monitor.
    """
    resultados = set()
    resultados.update(ESTADOS_PENDIENTES_MODELO.get(tipo, set()))
    resultados.update(ESTADOS_PREPARACION_MODELO.get(tipo, set()))
    # Español: 'despachado' se excluye del monitor — el pedido sigue su curso
    # y se consolida en Gestión de Pedidos solo cuando el estado final es 'Pagado'
    # resultados.update(ESTADOS_DESPACHADOS_MODELO.get(tipo, set()))  # NO incluir
    return resultados


def _serializar_item_comanda(comanda: Comanda) -> dict:
    """Serializa una comanda para el formato unificado de cocina."""
    estado_cocina = _mapear_estado_cocina('comanda', comanda.estado)

    articulos = []
    if comanda.articulos_json:
        try:
            articulos = json.loads(comanda.articulos_json)
        except (json.JSONDecodeError, TypeError):
            articulos = []

    return {
        'id': comanda.id,
        'tipo': 'mesa',
        'origen': f'Mesa #{comanda.mesa.numero_mesa}' if comanda.mesa else f'Mesa #{comanda.mesa_id}',
        'origen_detalle': f'Mesa #{comanda.mesa.numero_mesa}' if comanda.mesa else f'Mesa #{comanda.mesa_id}',
        'cliente_nombre': None,
        'direccion_entrega': None,
        'telefono_contacto': None,
        'mesa_id': comanda.mesa_id,
        'numero_mesa': comanda.mesa.numero_mesa if comanda.mesa else None,
        'fecha': comanda.fecha.isoformat() if comanda.fecha else None,
        'estado': estado_cocina,
        'estado_modelo': comanda.estado,  # Estado real en BD
        'articulos': articulos,
        'total': float(comanda.total or 0),
        'usuario_id': comanda.usuario_id,
    }


def _serializar_item_pedido(pedido: Pedido) -> dict:
    """Serializa un pedido (domicilio) para el formato unificado de cocina."""
    estado_cocina = _mapear_estado_cocina('pedido', pedido.estado.lower() if pedido.estado else 'pendiente')

    articulos = []
    if pedido.articulos_json:
        try:
            articulos = json.loads(pedido.articulos_json)
        except (json.JSONDecodeError, TypeError):
            articulos = []

    # Intentar obtener nombre del cliente desde usuario
    cliente_nombre = None
    if pedido.cliente_id:
        from models.usuario import Usuario
        usuario = Usuario.query.get(pedido.cliente_id)
        if usuario:
            cliente_nombre = usuario.nombre

    return {
        'id': pedido.id,
        'tipo': 'domicilio',
        'origen': f'🛵 Domicilio - {cliente_nombre or "Cliente"}' if cliente_nombre else '🛵 Domicilio',
        'origen_detalle': f'Domicilio — {cliente_nombre or "Cliente #" + str(pedido.cliente_id or "")}' if (cliente_nombre or pedido.cliente_id) else 'Domicilio',
        'cliente_nombre': cliente_nombre,
        'direccion_entrega': pedido.direccion_entrega or '',
        'telefono_contacto': pedido.telefono_contacto or '',
        'mesa_id': None,
        'numero_mesa': None,
        'fecha': pedido.fecha.isoformat() if pedido.fecha else None,
        'estado': estado_cocina,
        'estado_modelo': pedido.estado,  # Estado real en BD
        'articulos': articulos,
        'total': float(pedido.total or 0),
        'usuario_id': pedido.cliente_id,
    }


# ---------------------------------------------------------------------------
# Endpoint: Lista unificada de pendientes de cocina
# ---------------------------------------------------------------------------

@kitchen_bp.route('/kitchen/pendientes', methods=['GET'])
@roles_requeridos_cocina('admin', 'cocinero')
def obtener_pendientes_cocina():
    """
    GET /api/kitchen/pendientes
    Retorna una lista unificada de todos los items que la cocina debe procesar,
    tanto de Mesa (comandas abiertas/en_preparacion/listo) como de Domicilio
    (pedidos pendientes/en_preparacion/listo), ordenados por fecha ascendente.
    """
    try:
        # 1. Obtener comandas activas (Mesa)
        estados_comanda = _estados_modelo_para_cocina('comanda')
        comandas = Comanda.query.filter(
            Comanda.estado.in_(estados_comanda)
        ).order_by(Comanda.fecha.asc()).all()

        # 2. Obtener pedidos de domicilio activos en cocina
        estados_pedido = _estados_modelo_para_cocina('pedido')
        pedidos = Pedido.query.filter(
            Pedido.tipo == 'domicilio',
            Pedido.estado.in_(estados_pedido)
        ).order_by(Pedido.fecha.asc()).all()

        # 3. Serializar ambos en formato unificado
        items = []
        items.extend([_serializar_item_comanda(c) for c in comandas])
        items.extend([_serializar_item_pedido(p) for p in pedidos])

        # 4. Ordenar por fecha (más antiguos primero)
        items.sort(key=lambda x: x['fecha'] or '')

        # 5. Calcular totales (solo activos: pendiente + en_preparacion)
        totales = {
            'pendientes': sum(1 for i in items if i['estado'] == 'pendiente'),
            'en_preparacion': sum(1 for i in items if i['estado'] == 'en_preparacion'),
        }

        return jsonify({
            'status': 'success',
            'items': items,
            'totales': totales,
            'total_items': len(items),
        }), 200

    except Exception as e:
        logger.exception('Error al cargar pendientes de cocina: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al cargar pedidos de cocina'}), 500


# ---------------------------------------------------------------------------
# Endpoint: Actualizar estado de cocina
# ---------------------------------------------------------------------------

@kitchen_bp.route('/kitchen/<int:item_id>/estado', methods=['PUT'])
@roles_requeridos_cocina('admin', 'cocinero')
def actualizar_estado_cocina(item_id: int):
    """
    PUT /api/kitchen/<id>/estado
    Actualiza el estado de cocina de un item (comanda o pedido).
    Body: { "tipo": "mesa" | "domicilio", "estado": "en_preparacion" | "despachado" }

    Traducción de estados de cocina → estados del modelo:
      - 'en_preparacion' → comanda: 'en_preparacion', pedido: 'en_preparacion'
      - 'despachado'     → comanda: 'listo',       pedido: 'listo'
    """
    try:
        datos = request.get_json() or {}
        tipo = datos.get('tipo', '').strip().lower()
        nuevo_estado_cocina = datos.get('estado', '').strip().lower()

        if tipo not in ('mesa', 'domicilio'):
            return jsonify({
                'status': 'error',
                'message': 'tipo inválido. Use: "mesa" o "domicilio"'
            }), 400

        # Mapear estado de cocina → estado del modelo
        mapa_a_modelo = {
            'en_preparacion': 'en_preparacion',
            'despachado': 'listo',
        }

        if nuevo_estado_cocina not in mapa_a_modelo:
            return jsonify({
                'status': 'error',
                'message': f'Estado de cocina inválido: "{nuevo_estado_cocina}". Use: {list(mapa_a_modelo.keys())}'
            }), 400

        nuevo_estado_modelo = mapa_a_modelo[nuevo_estado_cocina]

        # Buscar y actualizar según tipo
        if tipo == 'mesa':
            comanda = Comanda.query.get(item_id)
            if not comanda:
                return jsonify({'status': 'error', 'message': f'Comanda #{item_id} no encontrada'}), 404

            # Validar transición válida
            if comanda.estado == nuevo_estado_modelo:
                return jsonify({'status': 'success', 'message': f'Comanda #{item_id} ya está en "{nuevo_estado_modelo}"'}), 200

            estado_anterior = _mapear_estado_cocina('comanda', comanda.estado)
            comanda.estado = nuevo_estado_modelo
            db.session.commit()

            logger.info('🍳 Cocina: Comanda #%s: %s → %s (cocina: %s)', item_id, estado_anterior, nuevo_estado_cocina, nuevo_estado_modelo)

            return jsonify({
                'status': 'success',
                'message': f'Comanda #{item_id} marcada como "{nuevo_estado_cocina}"',
                'item': _serializar_item_comanda(comanda),
            }), 200

        else:  # tipo == 'domicilio'
            pedido = Pedido.query.get(item_id)
            if not pedido:
                return jsonify({'status': 'error', 'message': f'Pedido #{item_id} no encontrado'}), 404

            if pedido.tipo != 'domicilio':
                return jsonify({'status': 'error', 'message': f'Pedido #{item_id} no es de tipo domicilio'}), 400

            if pedido.estado == nuevo_estado_modelo:
                return jsonify({'status': 'success', 'message': f'Pedido #{item_id} ya está en "{nuevo_estado_modelo}"'}), 200

            estado_anterior = _mapear_estado_cocina('pedido', pedido.estado)
            pedido.estado = nuevo_estado_modelo
            db.session.commit()

            logger.info('🍳 Cocina: Pedido #%s: %s → %s (cocina: %s)', item_id, estado_anterior, nuevo_estado_cocina, nuevo_estado_modelo)

            return jsonify({
                'status': 'success',
                'message': f'Pedido #{item_id} marcado como "{nuevo_estado_cocina}"',
                'item': _serializar_item_pedido(pedido),
            }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al actualizar estado de cocina para item %s: %s', item_id, e)
        return jsonify({'status': 'error', 'message': 'Error al actualizar estado'}), 500
