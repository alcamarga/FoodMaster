# routes/mesa_routes.py — Endpoints para gestión de mesas y comandas
# Español: rutas para CRUD de mesas, apertura/cierre de comandas | English: routes for table CRUD and comanda open/close

import json
import logging
from datetime import datetime
from functools import wraps

from flask import Blueprint, jsonify, request

from models.database import db
from models.mesa import Mesa
from models.comanda import Comanda
from models.pedido import Pedido
from models.usuario import Usuario

mesa_bp = Blueprint('mesa_bp', __name__)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Decorador de roles | Role decorator
# ---------------------------------------------------------------------------

JWT_SECRET_MESA = "pizzeria_secret_key_fixed_2026_super_safe"

def roles_requeridos(*roles_permitidos: str):
    """
    Decorador que verifica que el token JWT contenga un rol permitido.
    Uso: @roles_requeridos('admin', 'cocinero')
    """
    import jwt as pyjwt

    def decorador(func):
        @wraps(func)
        def envoltura(*args, **kwargs):
            encabezado = request.headers.get('Authorization', '')
            try:
                token = encabezado.split()[1]
                payload = pyjwt.decode(token, JWT_SECRET_MESA, algorithms=['HS256'])
                rol_usuario = payload.get('rol', '')
                if rol_usuario not in roles_permitidos:
                    return jsonify({'status': 'error', 'message': f'Acceso denegado. Se requiere rol: {roles_permitidos}'}), 403
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
# Endpoints públicos de cocina (sin autenticación para facilitar integración)
# ---------------------------------------------------------------------------

@mesa_bp.route('/comandas/activas', methods=['GET'])
@roles_requeridos('admin', 'cocinero', 'mesero')
def obtener_comandas_activas():
    """
    GET /api/comandas/activas — Lista todas las comandas activas del flujo de cocina
    (abierta, en_preparacion, listo), ordenadas por fecha ascendente (más antiguas primero).
    """
    try:
        # Español: mostrar todo el flujo de trabajo de cocina | English: show full kitchen workflow
        comandas = Comanda.query.filter(
            Comanda.estado.in_(['abierta', 'en_preparacion', 'listo'])
        ).order_by(Comanda.fecha.asc()).all()
        return jsonify({
            'status': 'success',
            'comandas': [c.serializar() for c in comandas],
        }), 200
    except Exception as e:
        logger.exception('Error al listar comandas activas: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al cargar comandas'}), 500


@mesa_bp.route('/comandas/<int:comanda_id>/estado', methods=['PUT'])
@roles_requeridos('admin', 'cocinero')
def actualizar_estado_comanda(comanda_id: int):
    """
    PUT /api/comandas/<id>/estado — Actualiza el estado de una comanda.
    Body: { "estado": "en_preparacion" | "listo" }
    """
    try:
        datos = request.get_json() or {}
        nuevo_estado = datos.get('estado', '').strip()

        estados_validos = {'en_preparacion', 'listo'}
        if nuevo_estado not in estados_validos:
            return jsonify({
                'status': 'error',
                'message': f'Estado inválido: "{nuevo_estado}". Use: {estados_validos}'
            }), 400

        comanda = Comanda.query.get(comanda_id)
        if not comanda:
            return jsonify({'status': 'error', 'message': f'Comanda #{comanda_id} no encontrada'}), 404

        estado_anterior = comanda.estado
        comanda.estado = nuevo_estado
        db.session.commit()

        logger.info('🍳 Comanda #%s: %s → %s', comanda_id, estado_anterior, nuevo_estado)
        return jsonify({
            'status': 'success',
            'message': f'Comanda #{comanda_id} marcada como "{nuevo_estado}"',
            'comanda': comanda.serializar(),
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al actualizar estado de comanda %s: %s', comanda_id, e)
        return jsonify({'status': 'error', 'message': 'Error al actualizar estado'}), 500


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _obtener_mesa_o_error(mesa_id: int) -> Mesa:
    """Obtiene una mesa por ID o lanza 404."""
    mesa = Mesa.query.get(mesa_id)
    if not mesa:
        raise ValueError(f'Mesa #{mesa_id} no encontrada')
    return mesa


def _obtener_comanda_activa(mesa_id: int) -> Comanda | None:
    """Obtiene la comanda activa (abierta) de una mesa."""
    return Comanda.query.filter_by(
        mesa_id=mesa_id,
        estado='abierta',
    ).order_by(Comanda.id.desc()).first()


# ---------------------------------------------------------------------------
# Mesas
# ---------------------------------------------------------------------------

@mesa_bp.route('/mesas', methods=['GET'])
def obtener_mesas():
    """
    GET /api/mesas — Lista todas las mesas ordenadas por número.
    """
    try:
        mesas = Mesa.query.order_by(Mesa.numero_mesa.asc()).all()
        return jsonify([m.to_dict() for m in mesas]), 200
    except Exception as e:
        logger.exception('Error al consultar mesas: %s', e)
        return jsonify({'status': 'error', 'message': 'No se pudieron cargar las mesas'}), 500


@mesa_bp.route('/mesas', methods=['POST'])
def crear_mesa():
    """
    POST /api/mesas — Crea una nueva mesa.
    Body: { "numero_mesa": 5 }
    """
    datos = request.get_json() or {}
    numero_mesa = datos.get('numero_mesa')

    if not numero_mesa:
        return jsonify({'status': 'error', 'message': 'numero_mesa es requerido'}), 400

    try:
        existe = Mesa.query.filter_by(numero_mesa=int(numero_mesa)).first()
        if existe:
            return jsonify({'status': 'error', 'message': f'La mesa #{numero_mesa} ya existe'}), 409

        mesa = Mesa(numero_mesa=int(numero_mesa), estado='LIBRE')
        db.session.add(mesa)
        db.session.commit()

        logger.info('✅ Mesa #%s creada', numero_mesa)
        return jsonify({'status': 'success', 'mesa': mesa.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al crear mesa: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al crear la mesa'}), 500


@mesa_bp.route('/mesas/<int:mesa_id>', methods=['GET'])
def obtener_mesa(mesa_id: int):
    """
    GET /api/mesas/<id> — Devuelve una mesa con su comanda activa (si tiene).
    """
    try:
        mesa = _obtener_mesa_o_error(mesa_id)
        comanda_activa = _obtener_comanda_activa(mesa_id)

        respuesta = mesa.to_dict()
        if comanda_activa:
            respuesta['comanda_activa'] = comanda_activa.serializar()
        else:
            respuesta['comanda_activa'] = None

        return jsonify(respuesta), 200

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.exception('Error al obtener mesa %s: %s', mesa_id, e)
        return jsonify({'status': 'error', 'message': 'Error al obtener la mesa'}), 500


# ---------------------------------------------------------------------------
# Comandas — Apertura y gestión
# ---------------------------------------------------------------------------

@mesa_bp.route('/mesas/<int:mesa_id>/comanda', methods=['POST'])
def abrir_comanda(mesa_id: int):
    """
    POST /api/mesas/<id>/comanda — Abre una nueva comanda en la mesa.
    La mesa cambia a estado OCUPADA. No puede haber otra comanda activa.

    Body (opcional): { "usuario_id": 1 }
    """
    try:
        mesa = _obtener_mesa_o_error(mesa_id)
        datos = request.get_json() or {}

        # Validar que no haya una comanda activa
        comanda_existente = _obtener_comanda_activa(mesa_id)
        if comanda_existente:
            return jsonify({
                'status': 'error',
                'message': f'La mesa #{mesa.numero_mesa} ya tiene una comanda activa (ID: {comanda_existente.id})',
            }), 409

        # Validar que la mesa esté libre
        if mesa.estado == 'OCUPADA':
            return jsonify({
                'status': 'error',
                'message': f'La mesa #{mesa.numero_mesa} ya está OCUPADA',
            }), 409

        # Crear comanda
        comanda = Comanda(
            mesa_id=mesa_id,
            usuario_id=datos.get('usuario_id'),
            estado='abierta',
            total=0.00,
            articulos_json='[]',
        )
        db.session.add(comanda)
        db.session.flush()

        # Máquina de estados: al abrir comanda → mesa OCUPADA
        mesa.estado = 'OCUPADA'
        db.session.commit()

        logger.info('🍽️ Comanda #%s abierta en mesa #%s', comanda.id, mesa.numero_mesa)
        return jsonify({
            'status': 'success',
            'message': f'Comanda abierta en mesa #{mesa.numero_mesa}',
            'comanda': comanda.serializar(),
        }), 201

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        db.session.rollback()
        logger.exception('Error al abrir comanda en mesa %s: %s', mesa_id, e)
        return jsonify({'status': 'error', 'message': 'Error al abrir la comanda'}), 500


@mesa_bp.route('/mesas/<int:mesa_id>/comanda/<int:comanda_id>/agregar', methods=['POST'])
@mesa_bp.route('/mesas/<int:mesa_id>/agregar', methods=['POST'])
def agregar_producto(mesa_id: int, comanda_id: int | None = None):
    """
    POST /api/mesas/<id>/agregar — Agrega un artículo a la comanda activa.

    Body: {
        "producto_id": 1,
        "nombre": "Pizza Margarita",
        "precio": 15000,
        "cantidad": 2
    }
    También acepta: /api/mesas/<id>/comanda/<comanda_id>/agregar para comanda específica.
    """
    try:
        mesa = _obtener_mesa_o_error(mesa_id)
        datos = request.get_json() or {}

        # Determinar la comanda destino
        if comanda_id:
            comanda = Comanda.query.get(comanda_id)
            if not comanda or comanda.mesa_id != mesa_id:
                return jsonify({'status': 'error', 'message': 'Comanda no encontrada en esta mesa'}), 404
        else:
            comanda = _obtener_comanda_activa(mesa_id)

        if not comanda:
            return jsonify({
                'status': 'error',
                'message': f'La mesa #{mesa.numero_mesa} no tiene una comanda activa. Ábrela primero con POST /api/mesas/{mesa_id}/comanda',
            }), 400

        producto_id = datos.get('producto_id')
        nombre = datos.get('nombre')
        precio = datos.get('precio')
        cantidad = int(datos.get('cantidad', 1))

        if not nombre or precio is None:
            return jsonify({'status': 'error', 'message': 'nombre y precio son requeridos'}), 400

        # Cargar artículos actuales
        articulos = []
        if comanda.articulos_json:
            try:
                articulos = json.loads(comanda.articulos_json)
            except (json.JSONDecodeError, TypeError):
                articulos = []

        # Buscar si el producto ya existe en la comanda para sumar cantidad
        encontrado = False
        for art in articulos:
            if producto_id and art.get('producto_id') == producto_id:
                art['cantidad'] = art.get('cantidad', 1) + cantidad
                encontrado = True
                break
            if not producto_id and art.get('nombre') == nombre:
                art['cantidad'] = art.get('cantidad', 1) + cantidad
                encontrado = True
                break

        if not encontrado:
            articulos.append({
                'producto_id': producto_id or 0,
                'nombre': nombre,
                'precio': float(precio),
                'cantidad': cantidad,
            })

        comanda.articulos_json = json.dumps(articulos, ensure_ascii=False)
        comanda.recalcular_total()
        db.session.commit()

        logger.info('➕ %s x%d agregado a comanda #%s', nombre, cantidad, comanda.id)
        return jsonify({
            'status': 'success',
            'message': f'✅ {nombre} x{cantidad} agregado a la comanda',
            'comanda': comanda.serializar(),
        }), 200

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        db.session.rollback()
        logger.exception('Error al agregar producto a mesa %s: %s', mesa_id, e)
        return jsonify({'status': 'error', 'message': 'Error al agregar producto'}), 500


# ---------------------------------------------------------------------------
# Cierre y pago de comandas
# ---------------------------------------------------------------------------

@mesa_bp.route('/mesas/<int:mesa_id>/comanda/<int:comanda_id>/pagar', methods=['POST'])
def pagar_comanda(mesa_id: int, comanda_id: int):
    """
    POST /api/mesas/<id>/comanda/<comanda_id>/pagar — Marca la comanda como pagada.
    La mesa vuelve a estado LIBRE.
    """
    try:
        mesa = _obtener_mesa_o_error(mesa_id)
        comanda = Comanda.query.get(comanda_id)

        if not comanda or comanda.mesa_id != mesa_id:
            return jsonify({'status': 'error', 'message': 'Comanda no encontrada en esta mesa'}), 404

        if comanda.estado != 'abierta':
            return jsonify({
                'status': 'error',
                'message': f'La comanda ya está {comanda.estado}',
            }), 400

        # Español: crear Pedido a partir de la comanda pagada (tipo='mesa') para que aparezca en Gestión de Pedidos | English: create Pedido from paid comanda (tipo='mesa') so it appears in Order Management
        pedido_mesa = Pedido(
            cliente_id=comanda.usuario_id,
            articulos_json=comanda.articulos_json or '[]',
            total=float(comanda.total or 0),
            estado='pagada',
            tipo='mesa',
            # Español: usar la fecha actual (momento del pago) para alinearse con pedidos de delivery | English: use current time (payment moment) to align with delivery orders
            fecha=datetime.utcnow(),
        )
        db.session.add(pedido_mesa)
        db.session.flush()
        logger.info('🪑 Pedido de mesa #%s creado desde comanda #%s (total: $%s)', pedido_mesa.id, comanda_id, comanda.total)

        # Máquina de estados: al pagar comanda → mesa LIBRE
        comanda.estado = 'pagada'
        mesa.estado = 'LIBRE'
        db.session.commit()

        logger.info('💰 Comanda #%s pagada — mesa #%s liberada — Pedido #%s registrado', comanda_id, mesa.numero_mesa, pedido_mesa.id)
        return jsonify({
            'status': 'success',
            'message': f'Comanda #{comanda_id} pagada. Mesa #{mesa.numero_mesa} liberada. Pedido #{pedido_mesa.id} registrado.',
            'comanda': comanda.serializar(),
            'pedido_id': pedido_mesa.id,
        }), 200

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        db.session.rollback()
        logger.exception('Error al pagar comanda %s: %s', comanda_id, e)
        return jsonify({'status': 'error', 'message': 'Error al procesar el pago'}), 500


@mesa_bp.route('/mesas/<int:mesa_id>/comanda/<int:comanda_id>/cerrar', methods=['POST'])
def cerrar_comanda(mesa_id: int, comanda_id: int):
    """
    POST /api/mesas/<id>/comanda/<comanda_id>/cerrar — Cierra la comanda sin pago.
    La mesa vuelve a estado LIBRE.
    """
    try:
        mesa = _obtener_mesa_o_error(mesa_id)
        comanda = Comanda.query.get(comanda_id)

        if not comanda or comanda.mesa_id != mesa_id:
            return jsonify({'status': 'error', 'message': 'Comanda no encontrada en esta mesa'}), 404

        if comanda.estado != 'abierta':
            return jsonify({
                'status': 'error',
                'message': f'La comanda ya está {comanda.estado}',
            }), 400

        # Máquina de estados: al cerrar comanda → mesa LIBRE
        comanda.estado = 'cerrada'
        mesa.estado = 'LIBRE'
        db.session.commit()

        logger.info('🔒 Comanda #%s cerrada — mesa #%s liberada', comanda_id, mesa.numero_mesa)
        return jsonify({
            'status': 'success',
            'message': f'Comanda #{comanda_id} cerrada. Mesa #{mesa.numero_mesa} liberada.',
            'comanda': comanda.serializar(),
        }), 200

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        db.session.rollback()
        logger.exception('Error al cerrar comanda %s: %s', comanda_id, e)
        return jsonify({'status': 'error', 'message': 'Error al cerrar la comanda'}), 500


# ---------------------------------------------------------------------------
# Historial de comandas por mesa
# ---------------------------------------------------------------------------

@mesa_bp.route('/mesas/<int:mesa_id>/comandas', methods=['GET'])
def listar_comandas_mesa(mesa_id: int):
    """
    GET /api/mesas/<id>/comandas — Lista todas las comandas de una mesa.
    """
    try:
        mesa = _obtener_mesa_o_error(mesa_id)
        comandas = Comanda.query.filter_by(mesa_id=mesa_id).order_by(Comanda.fecha.desc()).all()
        return jsonify({
            'mesa': mesa.to_dict(),
            'comandas': [c.serializar() for c in comandas],
        }), 200

    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        logger.exception('Error al listar comandas de mesa %s: %s', mesa_id, e)
        return jsonify({'status': 'error', 'message': 'Error al consultar comandas'}), 500
