# models/mesa.py — Modelo ORM para mesas físicas del restaurante
# Español: mesas con estados LIBRE/OCUPADA y relación con comandas | English: tables with LIBRE/OCUPADA states and comanda relationship

from models.database import db


class Mesa(db.Model):
    """Modelo ORM: mesas físicas del restaurante."""

    __tablename__ = 'mesas'

    id = db.Column(db.Integer, primary_key=True)
    numero_mesa = db.Column(db.Integer, unique=True, nullable=False)
    estado = db.Column(db.String(20), default='LIBRE', nullable=False)

    # Relación con comandas (una mesa puede tener muchas comandas en el tiempo)
    comandas = db.relationship('Comanda', backref='mesa', lazy=True)

    def to_dict(self) -> dict:
        """Serializa la mesa para respuesta API."""
        return {
            'id': self.id,
            'numero_mesa': self.numero_mesa,
            'estado': self.estado,
        }
