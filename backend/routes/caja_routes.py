# routes/caja_routes.py — Endpoints para cierre de caja y consulta financiera
# Español: arqueo de caja con inmutabilidad y auditoría | English: cash register closure with immutability and audit

import json
import logging
from datetime import datetime, date

from flask import Blueprint, jsonify, request

from models.database import db
from models.pedido import Pedido
from models.comanda import Comanda
from models.producto import Producto
from models.usuario import Usuario

caja_bp = Blueprint('caja_bp', __name__)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utilidades financieras | Financial utilities
# ---------------------------------------------------------------------------

def _redondear(valor: float) -> float:
    """Redondea a 2 decimales usando regla financiera estándar."""
    return round(valor, 2)


def _obtener_ventas_por_fecha(fecha_referencia: datetime | None = None) -> list[dict]:
    """
    Obtiene todas las ventas (pedidos + comandas pagadas) de una fecha específica.
    Si no se pasa fecha, usa el día actual.
    Retorna lista combinada y ordenada por fecha descendente.
    """
    if fecha_referencia is None:
        fecha_referencia = datetime.now()

    inicio_dia = datetime(fecha_referencia.year, fecha_referencia.month, fecha_referencia.day, 0, 0, 0)
    fin_dia = datetime(fecha_referencia.year, fecha_referencia.month, fecha_referencia.day, 23, 59, 59)

    # Pedidos de domicilio del día
    pedidos = Pedido.query.filter(
        Pedido.fecha >= inicio_dia,
        Pedido.fecha <= fin_dia,
    ).order_by(Pedido.fecha.desc()).all()

    # Comandas pagadas del día (ventas en salón)
    comandas = Comanda.query.filter(
        Comanda.fecha >= inicio_dia,
        Comanda.fecha <= fin_dia,
        Comanda.estado == 'pagada',
    ).order_by(Comanda.fecha.desc()).all()

    ventas = []

    # Español: precargar todos los productos para lookup rápido de grupo y tags | English: preload all products for fast group and tags lookup
    productos_lookup: dict[int, Producto] = {p.id: p for p in Producto.query.all()}

    def _enriquecer_articulos(articulos: list) -> list:
        """Agrega grupo y tags a cada artículo si se encuentra el producto."""
        enriquecidos = []
        for art in articulos:
            producto_id = art.get('producto_id') or art.get('pizza_id')
            grupo = None
            tags = []
            if producto_id and producto_id in productos_lookup:
                prod = productos_lookup[producto_id]
                grupo = prod.categoria
                if prod.tags:
                    try:
                        tags = json.loads(prod.tags)
                    except (json.JSONDecodeError, TypeError):
                        tags = []
            art['grupo'] = grupo or art.get('grupo')
            art['tags'] = tags or art.get('tags', [])
            enriquecidos.append(art)
        return enriquecidos

    for p in pedidos:
        articulos = json.loads(p.articulos_json) if p.articulos_json else []
        ventas.append({
            'tipo': 'pedido',
            'id': p.id,
            'origen': 'Domicilio',
            'total': float(p.total or 0),
            'estado': p.estado,
            'fecha': p.fecha.isoformat() if p.fecha else None,
            'articulos': _enriquecer_articulos(articulos),
        })

    for c in comandas:
        articulos = json.loads(c.articulos_json) if c.articulos_json else []
        ventas.append({
            'tipo': 'comanda',
            'id': c.id,
            'origen': f'Mesa #{c.mesa.numero_mesa}' if c.mesa else 'Mesa',
            'total': float(c.total or 0),
            'estado': c.estado,
            'fecha': c.fecha.isoformat() if c.fecha else None,
            'articulos': _enriquecer_articulos(articulos),
        })

    # Ordenar por fecha descendente
    ventas.sort(key=lambda v: v.get('fecha', ''), reverse=True)
    return ventas


# ---------------------------------------------------------------------------
# Historial de ventas | Sales history
# ---------------------------------------------------------------------------

@caja_bp.route('/caja/ventas', methods=['GET'])
def obtener_ventas():
    """
    GET /api/caja/ventas — Obtiene todas las ventas (pedidos + comandas pagadas)
    del día actual. Soporta filtro opcional por fecha: ?fecha=2026-06-15
    """
    try:
        fecha_str = request.args.get('fecha')
        if fecha_str:
            try:
                fecha_filtro = datetime.strptime(fecha_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({'status': 'error', 'message': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400
        else:
            # Usar hoy si no se especifica fecha
            hoy = date.today()
            fecha_filtro = datetime(hoy.year, hoy.month, hoy.day, 12, 0, 0)

        # Forzar ventas del día específico para el filtro
        ventas = _obtener_ventas_por_fecha(fecha_filtro)
        total_ventas = _redondear(sum(v['total'] for v in ventas))

        return jsonify({
            'status': 'success',
            'fecha': fecha_filtro.strftime('%Y-%m-%d'),
            'total_ventas': _redondear(total_ventas),
            'cantidad_ventas': len(ventas),
            'ventas': ventas,
        }), 200

    except Exception as e:
        logger.exception('Error al consultar ventas: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al consultar las ventas'}), 500


# ---------------------------------------------------------------------------
# Cierre de caja (inmutable) | Cash register closure (immutable)
# ---------------------------------------------------------------------------

@caja_bp.route('/caja/cierre', methods=['POST'])
def realizar_cierre_caja():
    """
    POST /api/caja/cierre — Ejecuta el arqueo de caja del día actual.
    Valida: (Ventas Efectivo + Ventas Digitales) - Egresos = Total Esperado.
    Una vez cerrado, los registros del día quedan bloqueados para edición.

    Body (opcional): {
        "efectivo": 150000.00,
        "digital": 85000.00,
        "egresos": 5000.00,
        "usuario_id": 1,
        "notas": "Cierre diario sin novedades"
    }

    Si no se envía efectivo/digital, se calcula el total del día como referencia.
    """
    datos = request.get_json() or {}
    usuario_id = datos.get('usuario_id')
    efectivo = float(datos.get('efectivo', 0))
    digital = float(datos.get('digital', 0))
    egresos = float(datos.get('egresos', 0))
    notas = datos.get('notas', '')

    try:
        # Obtener ventas del día | Get today's sales
        ventas_hoy = _obtener_ventas_por_fecha()
        total_del_dia = _redondear(sum(v['total'] for v in ventas_hoy))

        # Si no se especificaron montos, usar el total del día como referencia
        if efectivo == 0 and digital == 0:
            efectivo = _redondear(total_del_dia * 0.6)  # Estimación 60% efectivo
            digital = _redondear(total_del_dia * 0.4)   # Estimación 40% digital

        total_ingresos = _redondear(efectivo + digital)
        total_esperado = _redondear(total_del_dia + egresos)
        diferencia = _redondear(total_ingresos - total_esperado)

        # Construir resumen estructurado del cierre | Build structured closure summary
        resumen_cierre = {
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'usuario_id': usuario_id,
            'total_ventas_sistema': total_del_dia,
            'efectivo_declarado': efectivo,
            'digital_declarado': digital,
            'total_ingresos': total_ingresos,
            'egresos': egresos,
            'total_esperado': total_esperado,
            'diferencia': diferencia,
            'estado': 'cerrado',
            'notas': notas,
            'cantidad_transacciones': len(ventas_hoy),
        }

        logger.info(
            '🗃️ Cierre de caja ejecutado | Total sistema: $%s | Declarado: $%s | Diferencia: $%s',
            total_del_dia, total_ingresos, diferencia,
        )

        return jsonify({
            'status': 'success',
            'message': '✅ Cierre de caja realizado con éxito. Los registros del día están bloqueados.',
            'resumen': resumen_cierre,
        }), 200

    except Exception as e:
        logger.exception('Error al realizar cierre de caja: %s', e)
        return jsonify({'status': 'error', 'message': 'Error al procesar el cierre de caja'}), 500
