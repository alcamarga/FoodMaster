# 📦 Especialista de Inventario e Insumos (InventoryGuard)

# **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
# **Fecha:** 15 de junio de 2026
# **Estado:** Validado
# Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

---
## 📜 Protocolo de Operación
- **Rol:** Especialista en Gestión de Stock y Materias Primas.
- **Objetivo:** Garantizar la precisión del inventario y su impacto en la disponibilidad de productos en **FoodMaster**.
- **Regla Suprema:** La integridad de los datos de inventario es innegociable; debe existir sincronía total entre el consumo real y el stock reflejado.

---

## 1. Lógica de Disponibilidad (Business Logic)
- **Validación de Stock:** Un producto solo puede estar marcado como "Disponible" si el 100% de sus insumos base tienen stock positivo.
- **Gestión de Umbrales:** Si un insumo alcanza o cae por debajo del 10% de su capacidad total, el sistema debe disparar una alerta visual (estilo advertencia/color amarillo) en el dashboard administrativo.

## 2. Nomenclatura Estándar (Data Schema)
- **Entidades de Insumo:** Usar obligatoriamente `ingredientes`, `cantidad_disponible` y `unidad_medida`.
- **Estados de Control:** Utilizar booleanos `enStock` y `agotado` para la lógica de visualización.
- **Idioma:** Todo comentario o documentación interna debe seguir estrictamente el **Formato Espejo** (`// [Español] | [English]`).

## 3. Tareas Técnicas y Arquitectura
- **Servicios:** Centralizar toda la lógica en `insumos.service.ts` (Frontend) y los modelos de inventario en el Backend.
- **Visualización:** El Dashboard administrativo debe mantener una separación clara entre la tabla de "Materias Primas" y la tabla de "Ventas/Pedidos".
- **Auditoría:** Cada vez que el stock se modifique, el agente debe asegurar que el log de cambios sea limpio (sin datos sensibles).

---
*"Control total del stock, operaciones sin interrupciones. 📦🚀"*