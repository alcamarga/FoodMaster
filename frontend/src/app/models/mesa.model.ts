// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

// Interfaces para el módulo de Mesas y Comandas | Interfaces for the Tables and Orders module

export interface IMesa {
  id: number;
  numero_mesa: number;
  estado: 'LIBRE' | 'OCUPADA';
  comanda_activa?: IComanda | null;
}

export interface IArticuloComanda {
  producto_id?: number;
  nombre: string;
  precio: number;
  cantidad: number;
}

export interface IComanda {
  id: number;
  mesa_id: number;
  numero_mesa?: number;
  usuario_id?: number | null;
  fecha: string;
  total: number;
  estado: 'abierta' | 'en_preparacion' | 'listo' | 'pagada' | 'cerrada';
  articulos: IArticuloComanda[];
}

// Respuesta del backend al listar comandas de una mesa | Backend response when listing comandas for a table
export interface IRespuestaComandasMesa {
  mesa: IMesa;
  comandas: IComanda[];
}

// Respuesta genérica del backend para operaciones de mesa | Generic backend response for table operations
export interface IRespuestaMesa {
  status: 'success' | 'error';
  message: string;
  mesa?: IMesa;
  comanda?: IComanda;
}
