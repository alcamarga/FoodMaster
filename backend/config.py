## Creado por Camilo Martinez
## Fecha: 27/04/2026

import os
from flask_sqlalchemy import SQLAlchemy

# La base de datos nace aquí para que nadie dependa de app.py
db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:admin123@localhost:5432/pizzeria_core'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'pizzas-secretas-123'