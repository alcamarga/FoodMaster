# models/grupo_producto.py — Modelo ORM para grupos de producto (antes Categoria)
# Español: grupos flexibles con etiquetas de precio | English: flexible product groups with price labels

from models.database import db


class GrupoProducto(db.Model):
    """
    Modelo ORM: grupos de producto (antes Categoria).

    Cada grupo define las etiquetas de tamaño/precio que se mostrarán
    en el frontend. Permite nombres genéricos como 'Platos Fuertes',
    'Bebidas', 'Entradas', etc.
    """

    __tablename__ = 'grupo_producto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    descripcion = db.Column(db.Text, nullable=True, default='')
    etiqueta_1 = db.Column(db.String(50), nullable=False, default='Único')
    etiqueta_2 = db.Column(db.String(50), nullable=True, default='')
    etiqueta_3 = db.Column(db.String(50), nullable=True, default='')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion or '',
            'etiqueta_1': self.etiqueta_1,
            'etiqueta_2': self.etiqueta_2 or '',
            'etiqueta_3': self.etiqueta_3 or '',
        }

    def obtener_etiquetas(self) -> list[str]:
        """Retorna solo las etiquetas no vacías como lista."""
        etiquetas = [self.etiqueta_1]
        if self.etiqueta_2:
            etiquetas.append(self.etiqueta_2)
        if self.etiqueta_3:
            etiquetas.append(self.etiqueta_3)
        return etiquetas
