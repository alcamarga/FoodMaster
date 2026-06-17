# 📋 Project Memory — FoodMaster

## Estado del Sistema
**Fecha:** 17 de junio de 2026
**Versión:** 1.0.0 (Producción)
**Última Tarea:** #7 — Monitor de Cocina

## Arquitectura

### Frontend (Angular 19)
- **Estilo:** Standalone Components + Signals
- **Autenticación:** JWT con interceptor HTTP
- **Control de Acceso:** RoleGuard basado en roles del usuario
- **Rutas protegidas:**
  - `/cocina` — Monitor de Cocina (admin, cocinero)
  - `/admin/dashboard` — Admin Dashboard (admin)
  - `/admin/mesas` — Gestión de Mesas (admin, mesero)
  - `/admin/pedidos` — Gestión de Pedidos (admin, cocinero)
  - `/delivery/activos` — Delivery Activos (admin, domiciliario)

### Backend (Flask + SQLAlchemy)
- **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación:** JWT con decorador `roles_requeridos()`
- **Blueprints registrados:** auth, pedidos, admin, mesa, kitchen, configuracion, delivery, caja, grupo_producto

## Roles del Sistema
| Rol | Acceso |
|-----|--------|
| `admin` | Dashboard completo, configuración, cocina, todo |
| `cocinero` | Monitor de Cocina, Gestión de Pedidos |
| `mesero` | Gestión de Mesas y Comandas |
| `domiciliario` | Delivery Activos, Mis Pedidos |
| `cliente` | Menú, Mis Pedidos, Seguimiento |

## Tareas Completadas

### Tarea #1-2: Configuración Inicial
- Estructura Angular + Flask, CORS, proxy, Docker

### Tarea #3: Identidad de Usuario
- JWT como fuente autoritativa de `user_id` en comandas y pedidos
- Fix de "User #undefined"

### Tarea #4: Flujo de Cocina Unificado (KDS)
- Endpoint `/api/kitchen/pendientes` unifica Mesa (comandas) + Domicilio (pedidos)
- Estados: `pendiente` → `en_preparacion` → `despachado`
- Frontend CocinaComponent con origen diferenciado

### Tarea #5: Configuración del Negocio
- Modelo singleton `Configuracion` (nombre negocio, IVA, moneda, etc.)
- IVA dinámico desde BD en cálculos de pedidos
- Frontend en Admin Dashboard

### Tarea #6: Refinamiento Gestión de Pedidos
- Tabla profesional con detalle de productos
- Estados: Pendiente / En Preparación / Pagado
- IVA dinámico, fix "User #undefined"

### Tarea #7: Monitor de Cocina
- **Backend:** Validación de roles (admin, cocinero) en endpoints `/api/kitchen/*`
- **Backend:** Solo retorna items activos (Pendiente + En Preparación)
- **Frontend:** CocinaComponent refinado como "Monitor de Cocina"
- Flujo: Pedido aparece al registrarse → Despachado desaparece del monitor → Se consolida en Gestión de Pedidos al pagar

### Tarea #8: IVA Incluido en Precio Final
- **Cambio de lógica:** El IVA ahora está **incluido** en el precio de los productos (no se suma aparte)
- **Fórmula:** `subtotal = total / 1.19`, `iva = total - subtotal` (extracción en lugar de adición)
- **Backend:** `serializar()` en `pedido.py` y `crear_pedido()` en `pedido_routes.py` actualizados
- **Frontend:** `cart.service.ts` (signals), `resumen-pedido`, `mesas`, `finanzas` actualizados con la nueva lógica

## Próximos Pasos
- Implementar actualización de estados de pedidos
- Pruebas de integración finales
- Tickets/facturas con datos del negocio (Configuracion)
