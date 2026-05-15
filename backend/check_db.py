from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('producto')
    print("Columns in table 'producto':")
    for column in columns:
        print(f"- {column['name']} ({column['type']})")
