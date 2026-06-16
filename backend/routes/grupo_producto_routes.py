# routes/grupo_producto_routes.py — Endpoints para grupos de producto
# Español: CRUD de grupos flexibles con etiquetas de precio | English: CRUD for flexible product groups with price labels

import logging

from flask import Blueprint, jsonify, request
from sqlalchemy import inspect, text

from models.database import db
from models.grupo_producto import GrupoProducto

grupo_producto_bp = Blueprint('grupo_producto_bp', __name__)
logger = logging.getLogger(__name__)

# Grupos por defecto para el seed | Default groups for seeding
GRUPOS_POR_DEFECTO = [
    {'nombre': 'Platos Fuertes', 'descripcion': 'Platos principales y especialidades de la casa', 'etiqueta_1': 'Personal', 'etiqueta_2': 'Mediana', 'etiqueta_3': 'Familiar'},
    {'nombre': 'Bebidas', 'descripcion': 'Bebidas carbonatadas, jugos y aguas', 'etiqueta_1': 'Personal', 'etiqueta_2': 'Litro', 'etiqueta_3': 'Familiar'},
    {'nombre': 'Lasaña', 'descripcion': 'Lasañas artesanales horneadas al momento', 'etiqueta_1': 'Pequeña', 'etiqueta_2': 'Grande', 'etiqueta_3': ''},
    {'nombre': 'Entradas', 'descripcion': 'Aperitivos y entradas para compartir', 'etiqueta_1': 'Porción', 'etiqueta_2': 'Familiar', 'etiqueta_3': ''},
    {'nombre': 'Postres', 'descripcion': 'Postres caseros y opciones dulces', 'etiqueta_1': 'Individual', 'etiqueta_2': '', 'etiqueta_3': ''},
    {'nombre': 'Licores', 'descripcion': 'Bebidas alcohólicas nacionales e importadas', 'etiqueta_1': 'Individual', 'etiqueta_2': 'Botella', 'etiqueta_3': ''},
    {'nombre': 'Otros', 'descripcion': 'Productos adicionales sin grupo específico', 'etiqueta_1': 'Único', 'etiqueta_2': '', 'etiqueta_3': ''},
]


def verificar_esquema_grupo():
    """
    Verifica que la tabla 'grupo_producto' tenga las columnas esperadas
    y las agrega con ALTER TABLE si faltan.
    Si la tabla 'categoria' antigua existe, migra los datos.
    """
    try:
        inspector = inspect(db.engine)
        tablas_existentes = inspector.get_table_names()

        # Migrar desde tabla 'categoria' antigua si existe | Migrate from old 'categoria' table if exists
        if 'categoria' in tablas_existentes and 'grupo_producto' not in tablas_existentes:
            logger.warning('⚠️ Migrando datos de tabla "categoria" a "grupo_producto"...')
            with db.engine.connect() as conn:
                conn.execute(text('''
                    CREATE TABLE grupo_producto AS
                    SELECT id, nombre, COALESCE(descripcion, '') as descripcion,
                           COALESCE(etiqueta_1, 'Único') as etiqueta_1,
                           COALESCE(etiqueta_2, '') as etiqueta_2,
                           COALESCE(etiqueta_3, '') as etiqueta_3
                    FROM categoria
                '''))
                conn.execute(text('ALTER TABLE grupo_producto ADD PRIMARY KEY (id)'))
                conn.execute(text('CREATE UNIQUE INDEX ix_grupo_producto_nombre ON grupo_producto (nombre)'))
                conn.commit()
            logger.info('✅ Datos migrados de "categoria" a "grupo_producto"')
            return

        if 'grupo_producto' not in tablas_existentes:
            logger.warning('⚠️ Tabla "grupo_producto" no existe. Se creará con db.create_all()')
            return

        columnas_existentes = {c['name'] for c in inspector.get_columns('grupo_producto')}

        columnas_requeridas = {
            'etiqueta_1': "VARCHAR(50) NOT NULL DEFAULT 'Único'",
            'etiqueta_2': "VARCHAR(50) DEFAULT ''",
            'etiqueta_3': "VARCHAR(50) DEFAULT ''",
            'descripcion': "TEXT DEFAULT ''",
        }

        for col_name, col_def in columnas_requeridas.items():
            if col_name not in columnas_existentes:
                logger.warning('⚠️ Columna "%s" faltante en tabla grupo_producto. Agregando...', col_name)
                with db.engine.connect() as conn:
                    conn.execute(text(f'ALTER TABLE grupo_producto ADD COLUMN {col_name} {col_def}'))
                    conn.commit()
                logger.info('✅ Columna "%s" agregada a tabla grupo_producto', col_name)

        if not columnas_requeridas.keys() <= columnas_existentes:
            logger.info('🔄 Esquema de grupo_producto actualizado correctamente')

    except Exception as e:
        logger.exception('Error al verificar esquema de grupo_producto: %s', e)
        logger.warning('⚠️ No se pudo verificar el esquema. La app continuará con las columnas existentes.')


def sembrar_grupos():
    """
    Crea los grupos por defecto si no existen, o actualiza
    sus etiquetas si ya existen pero tienen valores placeholder.
    """
    for grupo_data in GRUPOS_POR_DEFECTO:
        existe = GrupoProducto.query.filter_by(nombre=grupo_data['nombre']).first()
        if not existe:
            grupo = GrupoProducto(
                nombre=grupo_data['nombre'],
                descripcion=grupo_data.get('descripcion', ''),
                etiqueta_1=grupo_data['etiqueta_1'],
                etiqueta_2=grupo_data['etiqueta_2'],
                etiqueta_3=grupo_data['etiqueta_3'],
            )
            db.session.add(grupo)
        else:
            if existe.etiqueta_1 == 'Único' and grupo_data['etiqueta_1'] != 'Único':
                existe.etiqueta_1 = grupo_data['etiqueta_1']
            if not existe.etiqueta_2 and grupo_data['etiqueta_2']:
                existe.etiqueta_2 = grupo_data['etiqueta_2']
            if not existe.etiqueta_3 and grupo_data['etiqueta_3']:
                existe.etiqueta_3 = grupo_data['etiqueta_3']
            if not existe.descripcion and grupo_data.get('descripcion'):
                existe.descripcion = grupo_data['descripcion']

    db.session.commit()


@grupo_producto_bp.route('/grupos', methods=['GET'])
def obtener_grupos():
    """
    GET /api/grupos — Lista todos los grupos de producto disponibles.
    """
    try:
        grupos = GrupoProducto.query.order_by(GrupoProducto.nombre.asc()).all()
        return jsonify([g.to_dict() for g in grupos]), 200
    except Exception as e:
        logger.exception('Error al listar grupos: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al cargar grupos'}), 500


@grupo_producto_bp.route('/grupos', methods=['POST'])
def crear_grupo():
    """
    POST /api/grupos — Crea un nuevo grupo con etiquetas personalizadas.

    Body: {
        "nombre": "Platos Fuertes",
        "descripcion": "Principales",
        "etiqueta_1": "Individual",
        "etiqueta_2": "Botella",
        "etiqueta_3": ""
    }
    """
    datos = request.get_json() or {}
    nombre = datos.get('nombre', '').strip()

    if not nombre:
        return jsonify({'status': 'error', 'message': 'nombre es requerido'}), 400

    existe = GrupoProducto.query.filter_by(nombre=nombre).first()
    if existe:
        return jsonify({'status': 'error', 'message': f'El grupo "{nombre}" ya existe'}), 409

    try:
        grupo = GrupoProducto(
            nombre=nombre,
            descripcion=datos.get('descripcion', ''),
            etiqueta_1=datos.get('etiqueta_1', 'Único'),
            etiqueta_2=datos.get('etiqueta_2', ''),
            etiqueta_3=datos.get('etiqueta_3', ''),
        )
        db.session.add(grupo)
        db.session.commit()

        logger.info('✅ Grupo "%s" creado con etiquetas: %s', nombre, grupo.obtener_etiquetas())
        return jsonify({'status': 'success', 'grupo': grupo.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        logger.exception('Error al crear grupo "%s": %s', nombre, e)
        return jsonify({'status': 'error', 'message': 'Error al crear el grupo'}), 500
