from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Mesa(Base):
    __tablename__ = 'mesas'
    id = Column(Integer, primary_key=True)
    estado = Column(String, default='LIBRE')
    subcuentas = relationship('Subcuenta', back_populates='mesa')

class Subcuenta(Base):
    __tablename__ = 'subcuentas'
    id = Column(Integer, primary_key=True)
    mesa_id = Column(Integer, ForeignKey('mesas.id'))
    estado = Column(String, default='PENDIENTE')
    mesa = relationship('Mesa', back_populates='subcuentas')