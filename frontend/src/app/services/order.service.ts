import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface ItemPedido {
  nombre?: string;
  producto_nombre?: string;
  tamano?: string;
  cantidad?: number;
  precio?: number;
  precio_unitario?: number;
  [key: string]: any;
}

export interface Pedido {
  id: number;
  usuario_id?: number;
  cliente?: string;
  fecha_hora?: string;
  fecha?: string;
  subtotal?: number;
  iva?: number;
  total: number;
  estado?: string;
  articulos?: ItemPedido[];
  pizzas?: string;
}

@Injectable({ providedIn: 'root' })
export class OrderService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/pedidos`;

  // Listar pedidos (filtra automáticamente en el backend por token)
  obtenerPedidos(): Observable<{ pedidos: Pedido[] }> {
    return this.http.get<{ pedidos: Pedido[] }>(this.apiUrl);
  }

  // Actualizar estado (solo para admin)
  actualizarEstado(id: number, estado: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/${id}/estado`, { estado });
  }
}
