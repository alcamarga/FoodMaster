// Servicio para el módulo de rentabilidad del administrador.
// Autor: Camilo Martinez | Fecha: 01/05/2026

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RentabilidadItem {
  id: number;
  nombre: string;
  categoria: string;
  tamano: string;
  costo_produccion: number;

  precio_venta: number;
  ganancia: number;
  margen_porcentaje: number;
}

export interface ResumenRentabilidad {
  mas_rentable: RentabilidadItem | null;
  mayor_costo: RentabilidadItem | null;
  ganancia_total_estimada: number;
  total_productos: number;
}

export interface RespuestaRentabilidad {
  productos: RentabilidadItem[];
  resumen: ResumenRentabilidad;
}

@Injectable({ providedIn: 'root' })
export class RentabilidadService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/admin/rentabilidad`;

  obtenerRentabilidad(size?: string): Observable<RespuestaRentabilidad> {
    const url = `${this.apiUrl}${size ? '?size=' + size : ''}`;
    return this.http.get<RespuestaRentabilidad>(url);
  }
}
