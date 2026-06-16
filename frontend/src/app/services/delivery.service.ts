// Servicio de API para el flujo de delivery de FoodMaster.
// Español: endpoints de seguimiento, pedidos activos y asignación de domiciliarios | English: tracking, active orders and delivery assignment endpoints

import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthService } from './auth.service';

export interface TimelineStep {
  titulo: string;
  clave: string;
  timestamp: string | null;
  activo: boolean;
  completado: boolean;
}

export interface SeguimientoPedido {
  id: number;
  cliente_id?: number;
  fecha?: string;
  total: number;
  estado: string;
  articulos: any[];
  direccion_entrega?: string;
  telefono_contacto?: string;
  metodo_pago?: string | null;
  domiciliario_id?: number | null;
  domiciliario_nombre?: string;
  fecha_entrega?: string | null;
  timeline: TimelineStep[];
  domiciliario?: { id: number; nombre: string } | null;
}

export interface DeliveryPedido {
  id: number;
  total: number;
  estado: string;
  direccion_entrega?: string;
  telefono_contacto?: string;
  metodo_pago?: string | null;
  es_mio?: boolean;
  fecha?: string;
  articulos?: any[];
}

export interface ActivosResponse {
  pedidos: DeliveryPedido[];
  total: number;
}

@Injectable({ providedIn: 'root' })
export class DeliveryService {
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private apiUrl = `${environment.apiUrl}`;

  private get headers() {
    const token = this.auth.obtenerTokenAcceso();
    return token
      ? new HttpHeaders({ Authorization: `Bearer ${token}` })
      : new HttpHeaders();
  }

  // Español: obtener seguimiento de un pedido (público) | English: get order tracking info (public)
  obtenerSeguimiento(pedidoId: number): Observable<SeguimientoPedido> {
    return this.http.get<SeguimientoPedido>(`${this.apiUrl}/pedidos/${pedidoId}/seguimiento`);
  }

  // Español: listar pedidos activos para delivery (domiciliario/admin) | English: list active delivery orders (delivery person/admin)
  obtenerActivos(): Observable<ActivosResponse> {
    return this.http.get<ActivosResponse>(`${this.apiUrl}/delivery/activos`, { headers: this.headers });
  }

  // Español: auto-asignar domiciliario a un pedido | English: self-assign delivery person to an order
  asignarPedido(pedidoId: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/pedidos/${pedidoId}/domiciliario`, {}, { headers: this.headers });
  }

  // Español: liberar pedido (desasignarse) | English: release an order (unassign)
  liberarPedido(pedidoId: number): Observable<any> {
    return this.http.patch(`${this.apiUrl}/pedidos/${pedidoId}/domiciliario`,
      { accion: 'liberar' },
      { headers: this.headers }
    );
  }

  // Español: registrar pago al completar entrega | English: register payment on delivery completion
  registrarPago(pedidoId: number, metodoPago: string): Observable<any> {
    return this.http.patch(`${this.apiUrl}/pedidos/${pedidoId}/pago`,
      { metodo_pago: metodoPago },
      { headers: this.headers }
    );
  }

  // Español: obtener mis pedidos (cliente o domiciliario autenticado) | English: get my orders (authenticated client or delivery person)
  obtenerMisPedidos(): Observable<{ pedidos: any[]; total_pedidos: number }> {
    return this.http.get<{ pedidos: any[]; total_pedidos: number }>(
      `${this.apiUrl}/pedidos/mis`, { headers: this.headers }
    );
  }
}
