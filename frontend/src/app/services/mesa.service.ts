// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

// Servicio para gestionar mesas y comandas del salón | Service for managing tables and in-house orders

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { IMesa, IComanda, IRespuestaMesa, IRespuestaComandasMesa } from '../models/mesa.model';

const URL_MESAS = `${environment.apiUrl}/mesas`;

@Injectable({ providedIn: 'root' })
export class MesaService {
  private http = inject(HttpClient);

  // Obtener todas las mesas ordenadas por número | Get all tables sorted by number
  obtenerMesas(): Observable<IMesa[]> {
    return this.http.get<IMesa[]>(URL_MESAS);
  }

  // Obtener una mesa específica con su comanda activa | Get a specific table with its active comanda
  obtenerMesa(mesaId: number): Observable<IMesa> {
    return this.http.get<IMesa>(`${URL_MESAS}/${mesaId}`);
  }

  // Crear una nueva mesa | Create a new table
  crearMesa(numeroMesa: number): Observable<IRespuestaMesa> {
    return this.http.post<IRespuestaMesa>(URL_MESAS, { numero_mesa: numeroMesa });
  }

  // Abrir una nueva comanda en la mesa | Open a new order on the table
  abrirComanda(mesaId: number): Observable<IRespuestaMesa> {
    return this.http.post<IRespuestaMesa>(`${URL_MESAS}/${mesaId}/comanda`, {});
  }

  // Agregar un producto a la comanda activa de la mesa | Add a product to the table's active order
  agregarProducto(mesaId: number, producto: { producto_id?: number; nombre: string; precio: number; cantidad: number }): Observable<IRespuestaMesa> {
    return this.http.post<IRespuestaMesa>(`${URL_MESAS}/${mesaId}/agregar`, producto);
  }

  // Pagar una comanda (libera la mesa) | Pay a comanda (releases the table)
  pagarComanda(mesaId: number, comandaId: number): Observable<IRespuestaMesa> {
    return this.http.post<IRespuestaMesa>(`${URL_MESAS}/${mesaId}/comanda/${comandaId}/pagar`, {});
  }

  // Cerrar una comanda sin pago (libera la mesa) | Close a comanda without payment (releases the table)
  cerrarComanda(mesaId: number, comandaId: number): Observable<IRespuestaMesa> {
    return this.http.post<IRespuestaMesa>(`${URL_MESAS}/${mesaId}/comanda/${comandaId}/cerrar`, {});
  }

  // Listar historial de comandas de una mesa | List comanda history for a table
  obtenerComandasMesa(mesaId: number): Observable<IRespuestaComandasMesa> {
    return this.http.get<IRespuestaComandasMesa>(`${URL_MESAS}/${mesaId}/comandas`);
  }

  // Forzar liberación de una mesa (admin) | Force release a table (admin)
  limpiarMesa(mesaId: number): Observable<any> {
    return this.http.get(`${environment.apiUrl}/admin/limpiar-mesa/${mesaId}`);
  }
}
