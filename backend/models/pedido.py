from models.database import db
from datetime import datetime


def _iva_decimal():
    """Obtiene el IVA como decimal desde la configuración del negocio."""
    try:
        from models.configuracion import Configuracion
        return Configuracion.obtener_iva_decimal()
    except Exception:
        return 0.19  # fallback


class Pedido(db.Model):
    __tablename__ = 'pedido'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column('cliente', db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(50), default='pendiente')
    articulos_json = db.Column(db.Text, nullable=True)  # Guardamos los productos como JSON

    # Español: tipo de pedido (mesa/domicilio) | English: order type (table/delivery)
    tipo = db.Column(db.String(20), nullable=True, default=None)               # 'mesa' | 'domicilio'

    # Español: campos para delivery | English: delivery fields
    direccion_entrega = db.Column(db.String(255), nullable=True, default='')   # Dirección de envío | Delivery address
    telefono_contacto = db.Column(db.String(20), nullable=True, default='')    # Teléfono del cliente | Customer phone
    metodo_pago = db.Column(db.String(20), nullable=True, default=None)        # 'Efectivo' | 'Transferencia'
    domiciliario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True, default=None)  # Domiciliario asignado | Assigned delivery person
    fecha_entrega = db.Column(db.DateTime, nullable=True, default=None)        # Timestamp de entrega | Delivery timestamp

    # Relaciones | Relationships
    domiciliario_rel = db.relationship('Usuario', foreign_keys=[domiciliario_id], lazy=True)

    def serializar(self):
        import json
        articulos_lista = []
        if self.articulos_json:
            try:
                articulos_lista = json.loads(self.articulos_json)
            except:
                pass

        # Español: calcular total dinámicamente desde los artículos | English: calculate total dynamically from items
        try:
            if not articulos_lista:
                raise ValueError('Lista vacía — usar total almacenado | Empty list — use stored total')
            subtotal_calculado = sum(
                float(a.get('precio', a.get('precio_unitario', 0))) * float(a.get('cantidad', 1))
                for a in articulos_lista
            )
            iva_decimal = _iva_decimal()
            iva_calculado = round(subtotal_calculado * iva_decimal)
            total_calculado = subtotal_calculado + iva_calculado
        except Exception:
            # Español: fallback al total almacenado (pedidos antiguos sin artículos o malformados) | English: fallback to stored total (legacy orders without items or malformed)
            iva_decimal = _iva_decimal()
            total_calculado = float(self.total) if self.total else 0
            subtotal_calculado = round(total_calculado / (1 + iva_decimal))
            iva_calculado = total_calculado - subtotal_calculado

        resultado = {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "total": round(total_calculado, 2),
            "subtotal": round(subtotal_calculado, 2),
            "iva": round(iva_calculado, 2),
            "estado": self.estado or 'pendiente',
            "articulos": articulos_lista,
            "tipo": self.tipo,  # None → null en JSON → frontend usa fallback heurístico | None → null in JSON → frontend uses heuristic fallback
            "direccion_entrega": self.direccion_entrega or '',
            "telefono_contacto": self.telefono_contacto or '',
            "metodo_pago": self.metodo_pago,
            "domiciliario_id": self.domiciliario_id,
            "fecha_entrega": self.fecha_entrega.isoformat() if self.fecha_entrega else None,
        }

        # Español: incluir nombre del domiciliario si está asignado | English: include delivery person name if assigned
        if self.domiciliario_rel:
            resultado['domiciliario_nombre'] = self.domiciliario_rel.nombre

        return resultado