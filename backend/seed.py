## Creado por Camilo Martinez - FoodMaster
## Fecha: 13/05/2026

import sys
import os
from sqlalchemy import text

# Aseguramos que Python encuentre los modelos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.database import db
from models.usuario import Usuario
from models.producto import Producto
from werkzeug.security import generate_password_hash

def seed_data():
    with app.app_context():
        print("🚀 Iniciando limpieza profunda de la base de datos...")
        
        try:
            # Limpieza total con nombres correctos (plurales)
            db.session.execute(text('DROP TABLE IF EXISTS pedido, recetas, receta_item, receta, insumos, producto, usuario CASCADE;'))
            db.session.commit()
            print("✨ Tablas antiguas eliminadas (incluyendo insumos y recetas).")
        except Exception as e:
            print(f"Nota: No se pudieron borrar algunas tablas: {e}")
            db.session.rollback()

        # Recreamos las tablas
        db.create_all()
        print("📁 Tablas recreadas con éxito con el esquema actualizado.")

        # 1. USUARIO ADMINISTRADOR
        admin = Usuario(
            nombre='Admin Camilo',
            email='admin@pizzeria.com',
            contrasena_hash=generate_password_hash('admin123'),
            rol='admin'
        )
        db.session.add(admin)

        # 2. PRODUCTOS (Con todos los campos para evitar UndefinedColumn)
        pizzas = [
            Producto(nombre='Pizza Tradicional', descripcion='Clásica de jamón y queso', categoria='Pizza', precio_base=20000, precio_pequena=20000, precio_mediana=30000, precio_grande=40000),
            Producto(nombre='Pizza Especial', descripcion='Con pepperoni y champiñones', categoria='Pizza', precio_base=25000, precio_pequena=25000, precio_mediana=35000, precio_grande=45000),
            Producto(nombre='Coca-Cola Personal', descripcion='250ml', categoria='Gaseosa', precio_base=4000, precio_pequena=4000),
            Producto(nombre='Coca-Cola 1.5L', descripcion='Botella familiar', categoria='Gaseosa', precio_base=9000, precio_pequena=9000),
            Producto(nombre='Lasaña Mixta', descripcion='Carne y Pollo', categoria='Lasaña', precio_base=18000, precio_pequena=18000, precio_mediana=28000)
        ]

        for p in pizzas:
            db.session.add(p)

        try:
            db.session.commit()

            print("\n✅ ¡SISTEMA RESTAURADO CON ÉXITO!")
            print("---------------------------------")
            print("Pizzas y productos cargados correctamente.")
            print("---------------------------------")
            print("👉 Ahora corre: python3 app.py")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error al guardar los datos: {e}")

if __name__ == '__main__':
    seed_data()