/**
 * FoodMaster - MEMORIA DEL PROYECTO
 * Registro de avances, decisiones técnicas y estado del sistema.
 */

const projectMemory = [
  {
    "last_milestone": "Persistencia en base de datos y Configuración de Recetas Multidimensional",
    "technical_learnings": [
      "Migración completa de SQLite a PostgreSQL para soporte de producción.",
      "Ampliación del modelo Producto para soportar precios por tamaño o variante (precio_1, precio_2, precio_3).",
      "Configuración de CORS para métodos complejos (PUT/OPTIONS) en la edición de menú.",
      "Implementación de lógica de 'Auto-Categoría': creación dinámica de categorías al insertar productos nuevos.",
      "Gestión de suscripciones en Angular (ngOnDestroy) para evitar fugas de memoria."
    ],
    "current_state": "Sistema con backend estable. Inventario y Productos separados correctamente. Configuración de recetas funcional con carga dinámica.",
    "pending_tasks": [
      "Habilitar método PUT en el backend para permitir la edición de productos existentes.",
      "Corregir error 404 de assets/images/default-item.jpg.",
      "Implementar validación de login robusta.",
      "Ajustar diseño responsivo en tablas de inventario para descripciones largas."
    ],
    "historial_previo": {
      "estado_del_proyecto": {
        "ultima_actualizacion": "2026-06-14",
        "version": "2.0.0",
        "hito_actual": "Rebranding a FoodMaster y reestructuración de arquitectura"
      },
      "errores_criticos_resueltos": [
        {
          "id": "CORS-405",
          "problema": "Error 405 Method Not Allowed al intentar guardar nuevos productos.",
          "solucion": "Configuración explícita de métodos POST/OPTIONS y cross_origin en Flask.",
          "fecha_fijacion": "2026-04-30"
        }
      ]
    }
  },
  {
    "fecha": "2026-04-30",
    "modulo": "Fullstack (Angular + Flask + Postgres)",
    "tarea": "Estandarización de Inventario",
    "descripcion": "Separación de Insumos y Productos terminados, activación de recetas técnicas.",
    "logros": [
      "Implementación de precios múltiples para productos.",
      "Carga dinámica de ingredientes en el módulo de recetas.",
      "Limpieza de errores de memoria en el Dashboard.",
      "Registro automatizado de productos y categorías."
    ],
    "estado": "FINALIZADO"
  },
  {
    "fecha": "2026-05-15",
    "modulo": "Backend (Flask + SQLAlchemy)",
    "tarea": "Implementación de Descuento Automático de Inventario",
    "descripcion": "Lógica de control de stock vinculada al estado de la orden/comanda.",
    "logros": [
      "Sincronización de pedidos con recetas para cálculo de consumo.",
      "Manejo de productos sin receta (ítems de venta directa).",
      "Actualización en tiempo real del stock de insumos."
    ],
    "estado": "FINALIZADO"
  },
  {
    "fecha": "2026-05-16",
    "modulo": "Infraestructura & DevOps",
    "tarea": "Despliegue Multi-Contenedor en Azure",
    "descripcion": "Contenerización total (Frontend, Backend, DB) mediante Docker Compose y despliegue PaaS en Azure.",
    "logros": [
      "Arquitectura modular desplegable en cualquier entorno con soporte Docker.",
      "Pipeline de CI/CD automatizado.",
      "Soberanía tecnológica y escalabilidad del servicio."
    ],
    "estado": "COMPLETADO"
  }
];

export default projectMemory;