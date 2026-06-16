# routes/delivery_routes.py — Rutas para el flujo de delivery de FoodMaster
# Español: endpoints para seguimiento, domiciliarios y pagos | English: endpoints for tracking, delivery personnel and payments

import json
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request as flask_request
from models.database import db
from models.pedido import Pedido
from models.usuario import Usuario
import jwt as pyjwt

logger = logging.getLogger(__name__)

delivery_bp = Blueprint('delivery', __name__)
JWT_SECRET = "pizzeria_secret_key_fixed_2026_super_safe"


# --- UTILIDADES ---

def _verificar_token():
    """Extrae y valida el token JWT del header Authorization."""
    encabezado = flask_request.headers.get('Authorization', '')
    try:
        token = encabezado.split()[1]
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload, None
    except Exception:
        return None, (jsonify({'error': 'Token requerido o inválido'}), 401)


def _usuario_token(payload) -> Usuario | None:
    """Obtiene el usuario desde el payload del token."""
    if not payload:
        return None
    return Usuario.query.get(payload.get('id'))


# --- ENDPOINTS ---

@delivery_bp.route('/pedidos/mis', methods=['GET', 'OPTIONS'])
def mis_pedidos():
    """
    GET /api/pedidos/mis
    Obtiene los pedidos del usuario autenticado (cliente) o los pedidos
    asignados al domiciliario autenticado.
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    payload, error = _verificar_token()
    if error:
        return error

    try:
        usuario = _usuario_token(payload)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if usuario.rol == 'domiciliario':
            # Español: domiciliario ve los pedidos que tiene asignados | English: delivery person sees assigned orders
            pedidos = Pedido.query.filter_by(domiciliario_id=usuario.id).order_by(Pedido.fecha.desc()).all()
        else:
            # Español: cliente/admin/cocinero ven sus propios pedidos | English: client/admin/cook see their own orders
            pedidos = Pedido.query.filter_by(cliente_id=usuario.id).order_by(Pedido.fecha.desc()).all()

        return jsonify({
            'pedidos': [p.serializar() for p in pedidos],
            'total_pedidos': len(pedidos),
        }), 200

    except Exception as e:
        logger.exception('Error al obtener mis pedidos: %s', e)
        return jsonify({'error': 'Error al obtener pedidos'}), 500


@delivery_bp.route('/pedidos/<int:pedido_id>/seguimiento', methods=['GET', 'OPTIONS'])
def seguimiento_pedido(pedido_id):
    """
    GET /api/pedidos/<id>/seguimiento
    Devuelve información detallada del pedido para la vista de seguimiento.
    No requiere autenticación para permitir compartir el enlace (vista pública limitada).
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404

        data = pedido.serializar()

        # Español: añadir información adicional para seguimiento | English: add extra info for tracking
        data['timeline'] = _generar_timeline(pedido)

        # Español: si hay un domiciliario asignado, incluir sus datos básicos | English: if delivery person assigned, include basic info
        if pedido.domiciliario_rel:
            data['domiciliario'] = {
                'id': pedido.domiciliario_rel.id,
                'nombre': pedido.domiciliario_rel.nombre,
            }

        return jsonify(data), 200

    except Exception as e:
        logger.exception('Error al obtener seguimiento: %s', e)
        return jsonify({'error': 'Error al obtener seguimiento'}), 500


@delivery_bp.route('/pedidos/<int:pedido_id>/domiciliario', methods=['PATCH', 'OPTIONS'])
def asignar_domiciliario(pedido_id):
    """
    PATCH /api/pedidos/<id>/domiciliario
    Auto-asigna el domiciliario autenticado al pedido.
    Body (opcional): { "accion": "liberar" } para desasignarse.
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    payload, error = _verificar_token()
    if error:
        return error

    try:
        usuario = _usuario_token(payload)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if usuario.rol not in ('domiciliario', 'admin'):
            return jsonify({'error': 'Solo domiciliarios o administradores pueden asignarse pedidos'}), 403

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404

        datos = flask_request.get_json(silent=True) or {}
        accion = datos.get('accion', 'asignar')

        if accion == 'liberar':
            # Español: desasignar domiciliario | English: unassign delivery person
            nombre_anterior = pedido.domiciliario_rel.nombre if pedido.domiciliario_rel else None
            pedido.domiciliario_id = None
            db.session.commit()
            logger.info('📦 Domiciliario %s liberó pedido #%s', usuario.nombre, pedido_id)
            return jsonify({
                'mensaje': f'Pedido #{pedido_id} liberado',
                'domiciliario_anterior': nombre_anterior,
            }), 200

        # Español: asignar domiciliario al pedido | English: assign delivery person to order
        if pedido.domiciliario_id and pedido.domiciliario_id != usuario.id:
            return jsonify({'error': f'El pedido ya está asignado a otro domiciliario'}), 409

        pedido.domiciliario_id = usuario.id
        if pedido.estado.lower() in ('pendiente', 'en_preparacion'):
            pedido.estado = 'listo'

        db.session.commit()
        logger.info('📦 Domiciliario %s asignado al pedido #%s', usuario.nombre, pedido_id)

        return jsonify({
            'mensaje': f'Domiciliario {usuario.nombre} asignado al pedido #{pedido_id}',
            'pedido': pedido.serializar(),
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al asignar domiciliario: %s', e)
        return jsonify({'error': 'Error al asignar domiciliario'}), 500


@delivery_bp.route('/pedidos/<int:pedido_id>/pago', methods=['PATCH', 'OPTIONS'])
def registrar_pago(pedido_id):
    """
    PATCH /api/pedidos/<id>/pago
    El domiciliario registra el método de pago al completar la entrega.
    Body: { "metodo_pago": "Efectivo" | "Transferencia" }
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    payload, error = _verificar_token()
    if error:
        return error

    try:
        usuario = _usuario_token(payload)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if usuario.rol not in ('domiciliario', 'admin'):
            return jsonify({'error': 'Solo domiciliarios o administradores pueden registrar pagos'}), 403

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404

        # Español: verificar que el domiciliario está asignado a este pedido | English: verify delivery person is assigned
        if usuario.rol == 'domiciliario' and pedido.domiciliario_id != usuario.id:
            return jsonify({'error': 'No estás asignado a este pedido'}), 403

        datos = flask_request.get_json(silent=True) or {}
        metodo = datos.get('metodo_pago', '').strip().capitalize()

        if metodo not in ('Efectivo', 'Transferencia'):
            return jsonify({'error': 'Método de pago inválido. Use: Efectivo o Transferencia'}), 400

        pedido.metodo_pago = metodo
        pedido.estado = 'entregado'
        pedido.fecha_entrega = datetime.utcnow()
        db.session.commit()

        logger.info('💰 Pedido #%s: pago registrado (%s) por %s', pedido_id, metodo, usuario.nombre)

        return jsonify({
            'mensaje': f'Pago registrado: {metodo}',
            'pedido': pedido.serializar(),
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al registrar pago: %s', e)
        return jsonify({'error': 'Error al registrar pago'}), 500


@delivery_bp.route('/delivery/activos', methods=['GET', 'OPTIONS'])
def pedidos_activos():
    """
    GET /api/delivery/activos
    Lista los pedidos pendientes de entrega (visibles para domiciliarios y admin).
    """
    if flask_request.method == 'OPTIONS':
        return jsonify({}), 200

    payload, error = _verificar_token()
    if error:
        return error

    try:
        usuario = _usuario_token(payload)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        if usuario.rol not in ('domiciliario', 'admin'):
            return jsonify({'error': 'Acceso no autorizado'}), 403

        # Español: pedidos en estado listo o en_camino (pendientes de entrega) | English: orders ready or on the way
        estados_activos = ['listo', 'en_camino', 'en_preparacion']
        pedidos = Pedido.query.filter(Pedido.estado.in_(estados_activos)).order_by(Pedido.fecha.asc()).all()

        # Español: si es domiciliario, marcar cuáles son sus asignados | English: if delivery person, mark which are theirs
        resultados = []
        for p in pedidos:
            data = p.serializar()
            if usuario.rol == 'domiciliario':
                data['es_mio'] = (p.domiciliario_id == usuario.id)
            resultados.append(data)

        return jsonify({
            'pedidos': resultados,
            'total': len(resultados),
        }), 200

    except Exception as e:
        logger.exception('Error al listar pedidos activos: %s', e)
        return jsonify({'error': 'Error al obtener pedidos activos'}), 500


# --- FUNCIONES AUXILIARES ---

def migrar_columnas_delivery():
    """
    Agrega las columnas de delivery a la tabla pedido si no existen.
    Compatible con SQLite (ALTER TABLE ... ADD COLUMN).
    """
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)
    columnas_existentes = [c['name'] for c in inspector.get_columns('pedido')]

    migraciones = [
        ('direccion_entrega', 'ALTER TABLE pedido ADD COLUMN direccion_entrega VARCHAR(255) DEFAULT \'\''),
        ('telefono_contacto', 'ALTER TABLE pedido ADD COLUMN telefono_contacto VARCHAR(20) DEFAULT \'\''),
        ('metodo_pago', 'ALTER TABLE pedido ADD COLUMN metodo_pago VARCHAR(20) DEFAULT NULL'),
        ('domiciliario_id', 'ALTER TABLE pedido ADD COLUMN domiciliario_id INTEGER REFERENCES usuario(id) DEFAULT NULL'),
        ('fecha_entrega', 'ALTER TABLE pedido ADD COLUMN fecha_entrega DATETIME DEFAULT NULL'),
    ]

    for columna, sql in migraciones:
        if columna not in columnas_existentes:
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f'✅ [Migración] Columna "{columna}" agregada a tabla pedido')
            except Exception as e:
                db.session.rollback()
                print(f'⚠️ [Migración] No se pudo agregar "{columna}": {e}')


def _generar_timeline(pedido: Pedido) -> list:
    """
    Genera una línea de tiempo del pedido basada en su estado actual y fechas.
    Cada paso tiene: titulo, descripcion, timestamp, activo (bool)
    """
    pasos = [
        {'titulo': 'Pedido Recibido', 'clave': 'pendiente', 'timestamp': pedido.fecha.isoformat() if pedido.fecha else None},
        {'titulo': 'En Preparación', 'clave': 'en_preparacion', 'timestamp': None},
        {'titulo': 'Listo para Entrega', 'clave': 'listo', 'timestamp': None},
        {'titulo': 'En Camino', 'clave': 'en_camino', 'timestamp': None},
        {'titulo': 'Entregado', 'clave': 'entregado', 'timestamp': pedido.fecha_entrega.isoformat() if pedido.fecha_entrega else None},
    ]

    # Español: mapeo de estados existentes a estados del timeline | English: map existing states to timeline states
    mapa_estados = {
        'pendiente': 0,
        'en_preparacion': 1,
        'listo': 2,
        'en_camino': 3,
        'entregado': 4,
    }

    indice_actual = mapa_estados.get(pedido.estado.lower(), -1)

    for i, paso in enumerate(pasos):
        paso['activo'] = (i <= indice_actual)
        paso['completado'] = (i < indice_actual)

    return pasos
