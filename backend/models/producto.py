from models.database import db
import enum

# Esto es lo que faltaba y por eso daba el ImportError
class SizeEnum(enum.Enum):
    PEQUENA = "Pequeña"
    MEDIANA = "Mediana"
    GRANDE = "Grande"

class Producto(db.Model):
    __tablename__ = 'producto'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    # Mapeamos 'precio' de la DB a precio_base en Python
    precio_base = db.Column('precio', db.Numeric(10, 2), nullable=False)
    
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50))  # Español: grupo principal (obligatorio) | English: main product group (required)
    tags = db.Column(db.Text, nullable=True, default='[]')  # Español: etiquetas libres en JSON | English: free-form tags in JSON
    imagen_url = db.Column(db.String(500), nullable=True, default='')  # Español: URL de la imagen del producto | English: product image URL
    precio_pequena = db.Column(db.Float)
    precio_mediana = db.Column(db.Float)
    precio_grande = db.Column(db.Float)

    def rentabilidad(self, size_enum):
        return {
            "nombre": self.nombre,
            "costo_produccion": 10.0, 
            "ganancia": 5.0,
            "margen_porcentaje": 50.0
        }

    def serializar(self):
        import json
        # Parsear tags desde JSON | Parse tags from JSON
        tags_lista = []
        if self.tags:
            try:
                tags_lista = json.loads(self.tags)
            except (json.JSONDecodeError, TypeError):
                tags_lista = []

        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion or "",
            'categoria': self.categoria or "General",
            'tags': tags_lista,
            'imagen_url': self.imagen_url or '',
            'precio': float(self.precio_pequena) if self.precio_pequena and self.precio_pequena > 0 else float(self.precio_base or 0),
            'precio_1': float(self.precio_pequena or 0),
            'precio_2': float(self.precio_mediana or 0),
            'precio_3': float(self.precio_grande or 0),
            'precio_personal': float(self.precio_pequena or 0),
            'precio_mediano': float(self.precio_mediana or 0),
            'precio_familiar': float(self.precio_grande or 0)
        }