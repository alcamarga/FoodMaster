from app import app, db
from models.usuario import Usuario
from werkzeug.security import generate_password_hash

def reset_database():
    with app.app_context():
        print("--- Iniciando borrado de tablas ---")
        db.drop_all()
        print("--- Tablas borradas. Creando nueva estructura ---")
        db.create_all()
        
        # Crear usuario administrador inicial
        admin = Usuario(
            nombre='Admin FoodMaster',
            email='admin@foodmaster.com', # Nota el cambio de correo
            contrasena_hash=generate_password_hash('123456'),
            rol='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("--- Base de datos recreada y administrador creado con éxito ---")

if __name__ == "__main__":
    reset_database()