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
  cliente_id?: number | null;   // Español: ID del usuario/cliente desde el backend | English: user/client ID from backend
  usuario_id?: number;
  cliente?: string;
  fecha_hora?: string;
  fecha?: string;
  subtotal?: number;            // Español: subtotal calculado por el backend desde articulos_json | English: subtotal calculated by backend from articulos_json
  iva?: number;                 // Español: IVA calculado por el backend desde articulos_json | English: VAT calculated by backend from articulos_json
  total: number;                // Español: total calculado por el backend (subtotal + IVA) | English: total calculated by backend (subtotal + VAT)
  estado?: string;
  articulos?: ItemPedido[];
  pizzas?: string;
  tipo?: string;                // Español: 'mesa' | 'domicilio' — tipo explícito de pedido | English: 'table' | 'delivery' — explicit order type
  direccion_entrega?: string;   // Español: dirección de entrega para delivery | English: delivery address
  telefono_contacto?: string;   // Español: teléfono de contacto para delivery | English: contact phone for delivery
  metodo_pago?: string | null;  // Español: método de pago registrado | English: registered payment method
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
