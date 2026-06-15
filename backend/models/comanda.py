# models/comanda.py — Modelo ORM para comandas de mesas
# Español: comandas asociadas a una mesa con máquina de estados | English: table orders with state machine

import json
from datetime import datetime

from models.database import db


class Comanda(db.Model):
    """
    Modelo ORM: comanda (pedido de mesa) del restaurante.

    Máquina de estados:
      - 'abierta':  la mesa está en uso, se pueden agregar artículos
      - 'pagada':   la cuenta fue pagada, la mesa vuelve a LIBRE
      - 'cerrada':  comanda finalizada sin pago (administrativo)
    """

    __tablename__ = 'comanda'

    id = db.Column(db.Integer, primary_key=True)
    mesa_id = db.Column(db.Integer, db.ForeignKey('mesas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    estado = db.Column(db.String(50), default='abierta')
    articulos_json = db.Column(db.Text, nullable=True)

    def serializar(self) -> dict:
        """Serializa la comanda para respuesta API, incluyendo datos de la mesa."""
        articulos_lista = []
        if self.articulos_json:
            try:
                articulos_lista = json.loads(self.articulos_json)
            except (json.JSONDecodeError, TypeError):
                pass

        return {
            'id': self.id,
            'mesa_id': self.mesa_id,
            'numero_mesa': self.mesa.numero_mesa if self.mesa else None,
            'usuario_id': self.usuario_id,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'total': float(self.total or 0),
            'estado': self.estado,
            'articulos': articulos_lista,
        }

    def recalcular_total(self) -> float:
        """Recalcula el total desde articulos_json."""
        total = 0.0
        if self.articulos_json:
            try:
                articulos = json.loads(self.articulos_json)
                for art in articulos:
                    precio = float(art.get('precio', 0))
                    cantidad = int(art.get('cantidad', 1))
                    total += precio * cantidad
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        self.total = total
        return total
