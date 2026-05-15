# 🍕 Pizzería App Core

## Descripción
Pizzería App Core es una plataforma moderna para la gestión de menús, diseñada para proporcionar una experiencia atractiva y eficiente tanto para clientes como para administradores. Con una interfaz intuitiva y un diseño acogedor con temática de pizzería artesanal, esta aplicación es perfecta para cualquier negocio de comida italiana.

## Vista Previa
La aplicación cuenta con un diseño acogedor y moderno, inspirado en la temática de una pizzería artesanal. El uso de colores cálidos, imágenes atractivas y un fondo con un toque de glassmorphism crea una experiencia visual agradable y profesional.

## Arquitectura
Nuestra pizzería app core utiliza Angular 19 como framework frontend, combinado con Signals para manejar los flujos de trabajo y un Interceptor JWT para proteger las rutas.

### Backend
La parte backend es una API en Flask que se comunica con una base de datos SQLite utilizando SQLAlchemy. También incluye protección de rutas para asegurar la seguridad de los datos.

### Instalación
Para levantar el entorno y correr app.py, sigue estos pasos:

1️⃣ Crea un entorno virtual (venv) con Python.
2️⃣ Instala las dependencias necesarias con pip: `pip install -r requirements.txt`.
3️⃣ Corre app.py con Flask: `flask run`.

### Frontend
1️⃣ Instala Node.js y npm.
2️⃣ Ejecuta el comando `npm install` en la carpeta del proyecto para instalar todas las dependencias.
3️⃣ Ejecuta el comando `ng serve` para iniciar el servidor de desarrollo de Angular.

## Sección de Features
- **Diseño Glassmorphism**: Nuestro diseño utiliza una combinación de gradientes y sombras para crear un efecto visual atractivo.
- **Uso de Signals**: Utilizamos Signals para manejar el estado del proyecto y mantener la información sincronizada entre los diferentes componentes.
- **Seguimiento de Pedidos**: Sistema integral para que los clientes sigan sus pedidos y los administradores gestionen los estados en tiempo real.
- **Gestión de Recetas e Inventario**: Control detallado de insumos por producto con descuento automático de stock (en gr, ml y unidades) al iniciar la preparación.
- **RBAC Profesional**: Control de acceso basado en roles (Admin, Cocinero, Domiciliario) con interfaces adaptativas y seguridad en el backend.
- **Gestión de Personal Administrativa**: Panel dedicado para que el administrador gestione a su equipo con un CRUD completo (Crear, Editar, Eliminar) y asignación de roles.

## Seguridad e Inteligencia Artificial Local (Self-Hosted)
A partir de mayo de 2026, el proyecto integra una infraestructura de IA local para auditoría técnica y revisión de código, priorizando la privacidad de los datos y la soberanía tecnológica.

- **Stack**: Open WebUI desplegado en Docker (WSL2/SSD) conectado a **Ollama**.
- **Modelos**: Gemma2 y Llama3 para análisis de lógica de negocio y seguridad.
- **Caso de Uso Actual**: Auditoría de la capa de seguridad de Flask, específicamente el análisis de headers CORS (Preflight y Access-Control) para mitigar vulnerabilidades de Cross-Origin.

## Estado actual
🚀 **Hito Alcanzado: Arquitectura Multi-Contenedor Completa (15/05/2026)**. PizzaOS ahora es un ecosistema 100% portable y autónomo. Hemos integrado el Frontend de Angular con Nginx como servidor de producción y proxy inverso, el Backend de Flask y la Base de Datos PostgreSQL en una orquestación profesional.

### 🍕 Gestión de Inventario Inteligente (Update 24/04/2026)
El sistema ahora incluye un motor de descuentos automáticos vinculado al estado de los pedidos:
- **Activación por Estado:** Los insumos se descuentan únicamente cuando el pedido cambia a estado "Entregado".
- **Lógica de Recetas:** Cada producto está vinculado a una receta técnica (ej. gramos de queso, ml de salsa).
- **Sistema Anti-Errores:** El backend valida la integridad de los datos mediante ID y fallback por nombre, asegurando que el stock siempre sea preciso.
- **Control de Ruptura de Stock:** Validación automática que impide la entrega si no hay existencias suficientes.
- **Actualización de precios y análisis de rentabilidad:** Se cargaron precios reales de insumos; el Análisis de Rentabilidad solo considera 'Precio 1' (pizza pequeña), dejando a la Pizza Marinara con margen crítico del 27.3%. Pendiente: desglose por tamaños de pizza.