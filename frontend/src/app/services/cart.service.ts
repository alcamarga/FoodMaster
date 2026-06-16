// Servicio compartido para el estado del carrito usando Signals.
// Autor: Camilo Martínez | Fecha: 23/03/2026 | Versión: 1.7

import { Injectable, computed, effect, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Pizza } from '../models/pizza.model';
import { environment } from '../../environments/environment';

export interface ArticuloCarrito {
  pizzaId: number;
  tamanoId: number; // Mantener por compatibilidad futura
  cantidad: number;
  precioUnitario: number;
  nombre: string;
  tamano: string;
}

@Injectable({ providedIn: 'root' })
export class CartService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;
  // Señal interna que almacena los artículos del carrito
  private _items = signal<ArticuloCarrito[]>(this.cargarDesdeStorage());

  // Exposición solo lectura de la señal
  public readonly items = this._items.asReadonly();

  // Total de artículos (suma de cantidades)
  public readonly totalArticulos = computed(() =>
    this._items().reduce((acc, a) => acc + a.cantidad, 0)
  );

  // Precio total del carrito (sin IVA = subtotal base)
  public readonly totalCarrito = computed(() =>
    this._items().reduce((acc, a) => acc + a.precioUnitario * a.cantidad, 0)
  );

  // IVA (19% sobre el subtotal)
  public readonly ivaCarrito = computed(() =>
    Math.round(this.totalCarrito() * 0.19)
  );

  // Total final con IVA incluido
  public readonly totalConIva = computed(() =>
    this.totalCarrito() + this.ivaCarrito()
  );

  constructor() {
    // Sincronizar cambios con localStorage
    effect(() => {
      const datos = this._items();
      localStorage.setItem('carrito', JSON.stringify(datos));
    });
  }

  private cargarDesdeStorage(): ArticuloCarrito[] {
    const json = localStorage.getItem('carrito');
    return json ? JSON.parse(json) : [];
  }

  /** Añade un producto al carrito.
   * Si ya existe una fila con el mismo pizzaId y tamaño, incrementa la cantidad.
   */
  agregarAlCarrito(pizza: Pizza, tamanoLabel: string, precioExacto: number): void {
    this._items.update(actual => {
      const indice = actual.findIndex(a => a.pizzaId === pizza.id && a.tamano === tamanoLabel);
      if (indice !== -1) {
        const articulo = actual[indice];
        const actualizado = { ...articulo, cantidad: articulo.cantidad + 1 };
        return [...actual.slice(0, indice), actualizado, ...actual.slice(indice + 1)];
      }
      const nuevo: ArticuloCarrito = {
        pizzaId: pizza.id,
        tamanoId: 0,
        cantidad: 1,
        precioUnitario: precioExacto,
        nombre: pizza.nombre,
        tamano: tamanoLabel
      };
      return [...actual, nuevo];
    });
  }

  /** Elimina un artículo por su índice en la lista. */
  quitarArticulo(indice: number): void {
    this._items.update(actual => actual.filter((_, i) => i !== indice));
  }

  /** Incrementa la cantidad de un artículo. */
  aumentarCantidad(indice: number): void {
    this._items.update(actual =>
      actual.map((item, i) => i === indice ? { ...item, cantidad: item.cantidad + 1 } : item)
    );
  }

  /** Decrementa la cantidad y elimina el artículo si llega a 0. */
  disminuirCantidad(indice: number): void {
    this._items.update(actual =>
      actual
        .map((item, i) => i === indice ? { ...item, cantidad: item.cantidad - 1 } : item)
        .filter(item => item.cantidad > 0)
    );
  }

  /** Vacía todo el carrito. */
  vaciarCarrito(): void {
    this._items.set([]);
  }

  /** Español: envía el pedido al backend con datos de entrega | English: send order to backend with delivery data */
  confirmarPedido(usuarioId: number, datosEntrega?: { direccion: string; telefono: string; metodo_pago?: string | null }): Observable<any> {
    const subtotal = this.totalCarrito();
    const iva = subtotal * 0.19; // 19% IVA
    const total = subtotal + iva;
    const fechaActual = new Date().toISOString().slice(0, 19).replace('T', ' ');

    const payload: any = {
      usuario_id: usuarioId,
      subtotal: subtotal,
      iva: iva,
      total: total,
      fecha_hora: fechaActual,
      articulos: this._items().map(item => ({
        pizza_id: item.pizzaId,
        nombre: item.nombre,
        tamano: item.tamano,
        cantidad: item.cantidad,
        precio: item.precioUnitario
      }))
    };

    // Español: incluir datos de entrega si se proporcionaron | English: include delivery data if provided
    if (datosEntrega) {
      payload.direccion = datosEntrega.direccion;
      payload.telefono = datosEntrega.telefono;
      if (datosEntrega.metodo_pago) {
        payload.metodo_pago = datosEntrega.metodo_pago;
      }
    }

    return this.http.post(`${this.apiUrl}/pedidos`, payload);
  }
}
