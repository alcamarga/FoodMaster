# 🍽️ FoodMaster — Plataforma de Gestión de Restaurantes Multi-Nicho

## Descripción
**FoodMaster** es una plataforma moderna y versátil para la gestión integral de restaurantes, diseñada para adaptarse a cualquier tipo de negocio gastronómico: pizzerías, restaurantes de comida rápida, cafeterías, bares, y más. Con una interfaz intuitiva, diseño premium oscuro con acentos esmeralda, y una arquitectura escalable, FoodMaster es la solución definitiva para la administración de menús, pedidos, mesas, inventario y personal.

## Vista Previa
La aplicación cuenta con un diseño oscuro premium con glassmorphism, acentos en esmeralda (#10b981) y una experiencia de usuario fluida y profesional. El sistema está optimizado tanto para el uso en cocina (tablets) como para la administración desde escritorio.

## Arquitectura
FoodMaster utiliza **Angular 19** como framework frontend, combinado con **Signals** para manejo de estado reactivo y un **Interceptor JWT** para proteger las rutas. El backend es una **API REST en Flask (Python)** que se comunica con **PostgreSQL** (o SQLite en desarrollo) utilizando **SQLAlchemy** como ORM.

### Stack Técnico

| Capa | Tecnología |
|------|-----------|
| **Frontend** | Angular 19, Signals, Bootstrap 5, TypeScript |
| **Backend** | Flask (Python 3.12), SQLAlchemy, JWT |
| **Base de Datos** | PostgreSQL (producción) / SQLite (desarrollo) |
| **Proxy** | Nginx (producción), Proxy Angular CLI (desarrollo) |
| **Contenedores** | Docker, Docker Compose |
| **Cloud** | Microsoft Azure (Web Apps, PostgreSQL, Container Registry) |
| **IA Local** | Open WebUI + Ollama (Gemma2, Llama3) |

### Características Principales
- **🎨 Diseño Premium**: Tema oscuro con glassmorphism, acentos esmeralda, y animaciones sutiles.
- **🔐 RBAC Profesional**: Control de acceso basado en roles (Admin, Cocinero, Domiciliario, Mesero) con interfaces adaptativas.
- **🪑 Gestión de Mesas**: Sistema de mesas con comandas estilo "DiscOS" — apertura, cierre, agregado de productos en tiempo real.
- **🚚 Delivery Inteligente**: Flujo completo de delivery con asignación de domiciliarios, registro de pago (Efectivo/Transferencia) y seguimiento en tiempo real con timeline y código QR.
- **📋 Tipos de Pedido**: El sistema diferencia claramente entre **pedidos de mesa** y **pedidos de domicilio**, con filtros y visualización dedicada en la gestión administrativa.
- **📦 Inventario Inteligente**: Control detallado de insumos con descuento automático de stock (gr, ml, unidades) al entregar pedidos.
- **📋 Recetas y Rentabilidad**: Recetas técnicas por producto con análisis de margen por tamaño y costo de producción.
- **👥 Gestión de Personal**: Panel administrativo con CRUD completo de empleados y asignación de roles.
- **📱 Responsive**: Diseñado para funcionar en tablets de cocina, dispositivos móviles y escritorio.
- **🔒 Seguridad**: JWT, CORS dinámico, sanitización de inputs, y logging seguro sin datos sensibles.
- **🧠 IA Local (Self-Hosted)**: Integración con Open WebUI + Ollama para auditoría técnica y revisión de código con privacidad total.
- **📲 Código QR**: Cada pedido de delivery genera un código QR único que enlaza al seguimiento en tiempo real, facilitando la comunicación con el cliente.

### Estado Actual
🚀 **FoodMaster v1.0.0 — Sistema Completo de Gestión de Restaurante**

FoodMaster es un ecosistema 100% portable y autónomo con frontend (Angular/Nginx), backend (Flask) y base de datos (PostgreSQL) orquestados profesionalmente.

#### Módulos Implementados
- **🍳 Monitor de Cocina (KDS):** Vista en tiempo real con pedidos activos (Pendiente + En Preparación) separados por origen Mesa/Domicilio. Refresco automático cada 15s. Solo visible para Administradores y Cocineros.
- **📋 Gestión de Pedidos:** Tabla profesional con detalle de productos, estados claros (Pendiente / En Preparación / Pagado) e IVA dinámico.
- **🪑 Gestión de Mesas:** Comandas estilo POS con apertura, agregado de productos y cierre/pago.
- **🚚 Delivery Inteligente:** Asignación de domiciliarios, seguimiento con QR, pago en efectivo/transferencia.
- **⚙️ Configuración del Negocio:** Nombre, datos de contacto, moneda e IVA dinámico desde panel admin.
- **📊 Rentabilidad y Finanzas:** Análisis de márgenes, cierre de caja.
- **👥 Gestión de Personal:** CRUD de empleados con roles.
- **📦 Inventario Inteligente:** Control de insumos con descuento automático de stock.

## Instalación y Desarrollo Local

### Prerrequisitos
- Python 3.10+
- Node.js 18+
- Docker (opcional, para producción local)

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 seed.py    # Poblar base de datos con datos de ejemplo
python3 app.py     # Iniciar servidor Flask en :5000
```

### Frontend
```bash
cd frontend
npm install
ng serve --host 0.0.0.0   # Iniciar en :4200 con proxy a Flask
```

### Producción (Docker)
```bash
docker-compose up --build
```

## ☁️ Despliegue en la Nube
FoodMaster utiliza una arquitectura multi-contenedor desacoplada en **Microsoft Azure**:

- **Frontend (Angular)**: Azure Web App con Nginx — sirve la SPA compilada y conecta directamente con la API.
- **Backend (Flask)**: Azure Web App con CORS dinámico y manejo robusto de peticiones JSON.
- **Base de Datos**: Azure Database for PostgreSQL (Flexible Server) para persistencia gestionada.
- **Registro de Imágenes**: Azure Container Registry (ACR) privado para versionamiento de contenedores.

## Seguridad e Inteligencia Artificial Local
El proyecto integra una infraestructura de IA local auto-gestionada para auditoría técnica, priorizando la privacidad de datos y soberanía tecnológica:

- **Stack**: Open WebUI desplegado en Docker (WSL2/SSD) conectado a **Ollama**.
- **Modelos**: Gemma2 y Llama3 para análisis de lógica de negocio y seguridad.
- **Caso de Uso**: Auditoría de la capa de seguridad de Flask, análisis de headers CORS, y revisión de código automatizada.

## Licencia
**Desarrollado por:** Camilo Martinez Galarza 🧑🏽‍💻(CMG-Solutions)  
**Proyecto:** Personal-Proprietary — Todos los derechos reservados.
