from app import app
from models.database import db
from models.producto import Producto
# Asegúrate de importar tu modelo de Insumos si se llama así
# from models.insumo import Insumo 

with app.app_context():
    # Extraer Productos (Pizzas)
    productos = Producto.query.all()
    print("\n--- COPIA ESTO PARA TU SEED.PY (PRODUCTOS) ---")
    for p in productos:
        print(f"p{p.id} = Producto(nombre='{p.nombre}', precio_base={p.precio_base}, categoria='{p.categoria}')")
        print(f"db.session.add(p{p.id})")
    
    # Si tienes Insumos, haz lo mismo aquí
    # insumos = Insumo.query.all()
    # for i in insumos:
    #     print(f"i{i.id} = Insumo(nombre='{i.nombre}', stock={i.stock}, costo_unitario={i.costo_unitario})")
    #     print(f"db.session.add(i{i.id})")
    
    print("\ndb.session.commit()")