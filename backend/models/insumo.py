# models/insumo.py
from .database import db

class Insumo(db.Model):
    __tablename__ = 'insumos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cantidad = db.Column(db.Float, default=0.0)
    unidad = db.Column(db.String(20), default='gr')
    precio_unitario = db.Column(db.Float, nullable=False) # Nombre real en BD
    stock_minimo = db.Column(db.Float, default=1.0)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'cantidad': self.cantidad,
            'unidad': self.unidad,
            'unidad_medida': self.unidad,            # <--- PARA ANGULAR
            'precio': self.precio_unitario,          # <--- VITAL PARA ANGULAR
            'precio_unitario': self.precio_unitario, # Para consistencia
            'stock_minimo': self.stock_minimo
        }