// Servicio para gestión de la configuración del negocio
// Business configuration management service

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Configuracion {
  id: number;
  nombre_negocio: string;
  direccion: string;
  telefono: string;
  email: string;
  moneda: string;
  simbolo_moneda: string;
  porcentaje_iva: number;
  mensaje_pie: string;
}

export interface RespuestaConfiguracion {
  status: string;
  configuracion: Configuracion;
  message?: string;
}

@Injectable({ providedIn: 'root' })
export class ConfiguracionService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/configuracion`;

  /** Obtiene la configuración actual del negocio */
  obtener(): Observable<RespuestaConfiguracion> {
    return this.http.get<RespuestaConfiguracion>(this.apiUrl);
  }

  /** Actualiza campos de la configuración (solo envía los que cambian) */
  actualizar(datos: Partial<Configuracion>): Observable<RespuestaConfiguracion> {
    return this.http.put<RespuestaConfiguracion>(this.apiUrl, datos);
  }
}
