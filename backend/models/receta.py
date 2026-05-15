from models.database import db

class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True)
    pizza_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('insumos.id'), nullable=False)
    tamano = db.Column(db.String(20), nullable=False) # Pequeña, Mediana, Familiar
    cantidad_gastada = db.Column(db.Float, nullable=False)

    # Relación para sacar el nombre del insumo fácilmente
    insumo = db.relationship('Insumo', backref='recetas')

    def to_dict(self):
        return {
            'id': self.id,
            'pizza_id': self.pizza_id,
            'insumo_id': self.insumo_id,
            'insumo_nombre': self.insumo.nombre if self.insumo else "Desconocido",
            'unidad_medida': self.insumo.unidad if self.insumo else "gr",
            'tamano': self.tamano,
            'cantidad_gastada': self.cantidad_gastada
        }