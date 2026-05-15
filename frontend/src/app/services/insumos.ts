// Servicio para gestión de insumos del inventario.
// Autor: Camilo Martinez | Fecha: 01/05/2026 | Versión: 2.0

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Insumo {
  id: number;
  nombre: string;
  cantidad: number;
  precio: number;   // precio de compra por unidad de medida
  unidad_medida?: string;
  stock_minimo?: number;
}

/** Payload para crear o editar un insumo */
export interface InsumoPayload {
  nombre: string;
  cantidad: number;
  precio: number;
  unidad_medida: string;
  stock_minimo: number;
}

@Injectable({ providedIn: 'root' })
export class InsumosService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/insumos`;

  getInsumos(): Observable<Insumo[]> {
    return this.http.get<Insumo[]>(this.apiUrl);
  }

  createInsumo(insumo: InsumoPayload): Observable<Insumo> {
    return this.http.post<Insumo>(this.apiUrl, insumo);
  }

  /** Actualiza cantidad, precio_unidad, stock_minimo, nombre o unidad_medida */
  updateInsumo(id: number, cambios: Partial<InsumoPayload>): Observable<Insumo> {
    return this.http.put<Insumo>(`${this.apiUrl}/${id}`, cambios);
  }

  deleteInsumo(id: number): Observable<{ status: string; mensaje: string }> {
    return this.http.delete<{ status: string; mensaje: string }>(`${this.apiUrl}/${id}`);
  }
}
