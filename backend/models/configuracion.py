# models/configuracion.py — Modelo ORM para configuración del negocio
# Español: parámetros globales del restaurante (nombre, IVA, moneda, contacto)
# English: global restaurant settings (name, VAT, currency, contact)

from models.database import db


class Configuracion(db.Model):
    """
    Almacena la configuración global del negocio.
    Es una tabla de una sola fila (singleton) con ID fijo = 1.
    """
    __tablename__ = 'configuracion'

    id = db.Column(db.Integer, primary_key=True, default=1)  # Siempre ID=1 (singleton)

    # Español: datos del negocio | English: business info
    nombre_negocio = db.Column(db.String(200), nullable=False, default='Mi Pizzería')
    direccion = db.Column(db.String(300), nullable=True, default='')
    telefono = db.Column(db.String(50), nullable=True, default='')
    email = db.Column(db.String(120), nullable=True, default='')

    # Español: moneda y formato | English: currency and format
    moneda = db.Column(db.String(10), nullable=False, default='COP')
    simbolo_moneda = db.Column(db.String(5), nullable=False, default='$')

    # Español: impuestos | English: taxes
    porcentaje_iva = db.Column(db.Numeric(5, 2), nullable=False, default=19.00)

    # Español: pie de página en tickets/facturas | English: footer on receipts/invoices
    mensaje_pie = db.Column(db.String(500), nullable=True, default='¡Gracias por su visita!')

    def serializar(self) -> dict:
        """Serializa la configuración para respuesta API."""
        return {
            'id': self.id,
            'nombre_negocio': self.nombre_negocio,
            'direccion': self.direccion or '',
            'telefono': self.telefono or '',
            'email': self.email or '',
            'moneda': self.moneda,
            'simbolo_moneda': self.simbolo_moneda,
            'porcentaje_iva': float(self.porcentaje_iva or 19.00),
            'mensaje_pie': self.mensaje_pie or '',
        }

    @classmethod
    def obtener(cls):
        """
        Obtiene la configuración (crea la fila por defecto si no existe).
        Patrón singleton: siempre retorna la fila con ID=1.
        """
        config = cls.query.get(1)
        if not config:
            config = cls(id=1)
            db.session.add(config)
            db.session.commit()
        return config

    @classmethod
    def obtener_iva_decimal(cls) -> float:
        """
        Retorna el porcentaje de IVA como decimal (ej: 19.00 → 0.19).
        Útil para cálculos en pedidos y facturación.
        """
        config = cls.obtener()
        return float(config.porcentaje_iva or 19.00) / 100.0
