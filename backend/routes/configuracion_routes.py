# routes/configuracion_routes.py — Endpoints para configuración del negocio
# Español: CRUD de parámetros globales (nombre, IVA, moneda, contacto)
# English: CRUD for global settings (name, VAT, currency, contact)

import logging
from flask import Blueprint, jsonify, request

from models.database import db
from models.configuracion import Configuracion

logger = logging.getLogger(__name__)

config_bp = Blueprint('configuracion', __name__)


@config_bp.route('/configuracion', methods=['GET', 'OPTIONS'])
def obtener_configuracion():
    """
    GET /api/configuracion — Obtiene la configuración actual del negocio.
    Si no existe, la crea con valores por defecto.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        config = Configuracion.obtener()
        return jsonify({
            'status': 'success',
            'configuracion': config.serializar(),
        }), 200
    except Exception as e:
        logger.exception('Error al obtener configuración: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al cargar configuración'}), 500


@config_bp.route('/configuracion', methods=['PUT', 'OPTIONS'])
def actualizar_configuracion():
    """
    PUT /api/configuracion — Actualiza la configuración del negocio.
    Body: { "nombre_negocio": "...", "porcentaje_iva": 19, ... }
    Solo envía los campos que desea actualizar.
    """
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        datos = request.get_json()
        if not datos:
            return jsonify({'status': 'error', 'message': 'No se enviaron datos'}), 400

        config = Configuracion.obtener()

        # Español: mapeo de campos permitidos | English: allowed field mapping
        campos_permitidos = {
            'nombre_negocio': 'nombre_negocio',
            'direccion': 'direccion',
            'telefono': 'telefono',
            'email': 'email',
            'moneda': 'moneda',
            'simbolo_moneda': 'simbolo_moneda',
            'porcentaje_iva': 'porcentaje_iva',
            'mensaje_pie': 'mensaje_pie',
        }

        for campo_api, campo_modelo in campos_permitidos.items():
            if campo_api in datos:
                valor = datos[campo_api]
                # Validar IVA | Validate VAT
                if campo_api == 'porcentaje_iva':
                    try:
                        valor = float(valor)
                        if valor < 0 or valor > 100:
                            return jsonify({
                                'status': 'error',
                                'message': 'El IVA debe estar entre 0 y 100'
                            }), 400
                    except (ValueError, TypeError):
                        return jsonify({
                            'status': 'error',
                            'message': 'El IVA debe ser un número válido'
                        }), 400

                setattr(config, campo_modelo, valor)

        db.session.commit()
        logger.info('⚙️ Configuración actualizada: IVA=%.2f%%, negocio=%s',
                     float(config.porcentaje_iva), config.nombre_negocio)

        return jsonify({
            'status': 'success',
            'message': 'Configuración actualizada correctamente',
            'configuracion': config.serializar(),
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al actualizar configuración: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al actualizar configuración'}), 500
