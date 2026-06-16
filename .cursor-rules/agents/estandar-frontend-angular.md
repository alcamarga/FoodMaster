🎨 Estándar de Desarrollo Frontend (Angular)
Creado por: Camilo Martinez Galarza (CMG-Solutions)
Fecha: [15/06/2026]
Estado: Validado
Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

📜 Control de Autoría y Arquitectura
Lead Architect: Camilo Martinez Galarza

Asistente de Arquitectura: Gemini/Cami

"Este estándar es la ley en el Framework FoodMaster. Cualquier desviación debe ser consultada con el Arquitecto."

Este archivo guía a los agentes sobre cómo escribir código en el sistema FoodMaster.

1. Arquitectura Angular (v18+)
Standalone Components: No usar NgModules. Todo componente debe ser standalone: true.

Flujo de Control Moderno: Usar siempre la sintaxis de @-rules:

@for (item of list; track item.id) { ... } en lugar de *ngFor.

@if (condition) { ... } en lugar de *ngIf.

2. Configuración Crítica del Sistema
Zone.js: Verificar que zone.js esté en polyfills dentro de angular.json.

Detección de Cambios: Preferir provideZoneChangeDetection({ eventCoalescing: true }) en app.config.ts.

3. Estilo y UI
Framework: Usar Bootstrap 5 para todas las clases de CSS.

Estructura HTML: Mantener la semántica (tablas, formularios) para evitar errores de hidratación.

Dualidad de Diseño: El diseño debe adaptarse tanto a la lógica de Comandas (salón) como a la de Pedidos (domicilios).

4. Tipado y Modelos
Interfaces: Antes de crear un servicio, definir una interface (ej. IComanda, IPedido).

Strict Mode: Prohibido el uso de any.

4.1 Comentarios en código (idioma)
Seguir la política comentarios espejo: // Español | English en TS, <!-- … | … --> en plantillas.

4.2 Protocolo de Encabezado (Header Requirement)
Obligatorio: Todo archivo nuevo de TypeScript o componente Angular debe iniciar con el siguiente bloque de comentarios:

TypeScript
// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** [Fecha actual]
// **Estado:** [Estado del archivo: Ej. Desarrollo/Validado]
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

5. Limpieza de Errores (Troubleshooting)
Si Angular no muestra cambios:

rm -rf .angular/cache

fuser -k 4200/tcp

ng serve --host 0.0.0.0

"Lógica sólida, interfaz impecable. 🚀"