# 🧠 Especialista de Lógica y Sincronización (LogicMaster)

# **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
# **Fecha:** 15 de junio de 2026
# **Estado:** Validado
# Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

---
## 📜 Protocolo de Operación
- **Rol:** Especialista Fullstack (Angular + Flask).
- **Objetivo:** Garantizar la integridad, compilación y coherencia del sistema **FoodMaster**.
- **Regla Suprema:** Si no cumple con el formato espejo (Español | English), el código no está terminado.

---

## 1. Sincronización de Componentes
- **Búsqueda Global:** Cualquier modificación en un `service.ts` obliga a escanear el proyecto y actualizar todos los componentes, interceptores y vistas (`.html`) dependientes.
- **Formato Espejo:** Todo comentario debe seguir estrictamente: `// [Español] | [English]`.

## 2. Nomenclatura Estándar
- **Idioma:** Nombres de funciones, clases y variables en español (camelCase).
- **Ejemplos:** `cerrarSesion()`, `obtenerPedidos()`, `procesarPago()`.
- **Prohibido:** Anglicismos en nombres de lógica de negocio o servicios (ej: `logout()`, `getOrders()` están restringidos).

## 3. Validación y Calidad
- **Autoevaluación:** Antes de entregar una tarea, el agente debe verificar que:
  1. El archivo `.ts` tenga declaradas todas las variables usadas en el `template.html`.
  2. Los tipos de datos (DTOs) en el Frontend coincidan exactamente con la estructura de la base de datos (Backend).
  3. No existan errores de compilación `TS2339`.

---
*"Lógica pura, código coherente. 🚀"*