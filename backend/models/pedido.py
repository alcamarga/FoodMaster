from models.database import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'pedido'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column('cliente', db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(50), default='pendiente')
    articulos_json = db.Column(db.Text, nullable=True)  # Guardamos los productos como JSON

    def serializar(self):
        import json
        articulos_lista = []
        if self.articulos_json:
            try:
                articulos_lista = json.loads(self.articulos_json)
            except:
                pass

        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "fecha": self.fecha.isoformat(),
            "total": float(self.total),
            "estado": self.estado,
            "articulos": articulos_lista
        }