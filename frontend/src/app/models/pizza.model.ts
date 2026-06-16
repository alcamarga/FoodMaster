// Modelos para el catálogo de productos y sus precios.
// Autor: Camilo Martinez | Fecha: 23/03/2026 | Versión: 4.3

export interface Pizza {
  id: number;
  nombre: string;
  descripcion: string;
  categoria: string;
  tags?: string[];
  precio_1?: number;
  precio_2?: number;
  precio_3?: number;
  imagen?: string;         // Español: alias legacy para imagen_url | English: legacy alias for imagen_url
  imagen_url?: string;     // Español: URL de la imagen del producto | English: product image URL
  activo?: boolean;
}
