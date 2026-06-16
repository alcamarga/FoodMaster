## Creado por Camilo Martinez
## Fecha: 27/04/2026

import os
from flask_sqlalchemy import SQLAlchemy

# La base de datos nace aquí para que nadie dependa de app.py
db = SQLAlchemy()

class Config:
    # Ahora apuntamos a nuestro archivo local foodmaster.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///foodmaster.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Cambiamos la clave secreta por una más genérica y segura
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'foodmaster-clave-segura-2026'