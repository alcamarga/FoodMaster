// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

// Interfaces para el módulo de Grupos de Producto (antes Categorías) | Interfaces for the Product Groups module

export interface IGrupoProducto {
  id: number;
  nombre: string;
  descripcion?: string;
  etiqueta_1: string;
  etiqueta_2: string;
  etiqueta_3: string;
}
