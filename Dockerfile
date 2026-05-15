# 1. Usamos una imagen de base (ejemplo Python)
FROM python:3.10-slim

# 2. Creamos una carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos los archivos de requerimientos e instalamos librerías
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamos todo el código de tu pizzería a la carpeta /app
COPY . .

# 5. El comando para arrancar tu sistema
CMD ["python", "backend/app.py"]