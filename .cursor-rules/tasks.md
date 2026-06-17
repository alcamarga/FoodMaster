🚀 Roadmap y Registro de Tareas (Backlog)
Creado por: Camilo Martinez Galarza (CMG-Solutions)
Fecha: 15 de junio de 2026
Estado: En Ejecución
Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

📜 Protocolo de Seguimiento
Lead Architect: Camilo Martinez Galarza

Asistente de Arquitectura: Gemini/Cami

"La ejecución sin registro es caos. Cada hito debe estar documentado en este tablero."

🟢 Finalizado (Done)
[x] Configuración inicial del entorno Linux.
[x] Estructura base del Frontend en Angular.
[x] Corrección de errores de Zone.js y Polyfills.
[x] Creación del Sistema de Reglas (.cursor-rules).
[x] Conexión HttpClient entre Frontend y Backend.
[x] Configuración de CORS en el servidor Python.
[x] Delivery Inteligente: modelo, rutas y migración (backend).
[x] Fase 2 Frontend — Login con redirect, formulario de entrega, payload de delivery.
[x] Fase 3 Frontend — Seguimiento con timeline+QR y delivery activos.
[x] Estilos premium para seguimiento-pedido y delivery-activos.
[x] Diferenciación Mesa/Domicilio con campo 'tipo' explícito en modelo Pedido.
[x] Auditoría de totales — backend recalcula total/subtotal/IVA desde artículos.
[x] Caja module: excluir Pedidos de mesa para evitar doble conteo con Comandas.
[x] Limpieza profunda de BD: reset total con preservación de admin.
[x] **Tarea #3: Corrección de Identidad del Usuario** — user_id ahora se extrae del JWT en abrir_comanda y crear_pedido. Ya no aparece como 'undefined'.
[x] **Tarea #4: Implementación del Flujo de Cocina (KDS) para Mesas y Domicilios** — Endpoint unificado /api/kitchen/pendientes con origen Mesa/Domicilio, estados pendiente→en_preparacion→despachado. Frontend CocinaComponent actualizado con filtros y badges diferenciados.
[x] **Tarea #5: Configuración y Personalización del Negocio** — Modelo Configuracion (singleton), CRUD en /api/configuracion, IVA dinámico desde BD en pedidos, frontend con formulario en Admin Dashboard. Pendiente: usar datos en tickets/facturas.
[x] **Tarea #6: Refinamiento de la Gestión de Pedidos** — Tabla profesional con detalle de productos, estados Pendiente/En Preparación/Pagado, IVA dinámico, fix de "User #undefined", columna de resumen de productos, modal con dirección de entrega.

🟡 En Progreso (Doing)

[x] **Tarea #7: Monitor de Cocina (vista independiente)**
    - [x] Backend: Validación de roles (admin, cocinero) en endpoints de cocina
    - [x] Backend: Filtrar solo estados activos (Pendiente + En Preparación), excluir Despachado
    - [x] Frontend: Refinar CocinaComponent como "Monitor de Cocina" con KPIs simplificados
    - [x] Pruebas de endpoint: acceso con/sin token, sin despachados en respuesta ✅

🔴 Pendiente (To Do)
[ ] Implementar actualización de estados de pedidos.
[ ] Pruebas de integración final.

"Ejecución impecable. 🚀"