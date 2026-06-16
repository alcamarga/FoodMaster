// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

// Servicio para gestionar grupos de producto (antes categorías) desde el backend | Service for managing product groups from the backend

import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay } from 'rxjs';
import { environment } from '../../environments/environment';
import { IGrupoProducto } from '../models/grupo_producto.model';

const URL_API_GRUPOS = `${environment.apiUrl}/grupos`;

@Injectable({ providedIn: 'root' })
export class GrupoProductoService {
  private http = inject(HttpClient);

  // Cache compartido | Shared cache
  private _gruposCache$: Observable<IGrupoProducto[]> | null = null;

  /** Obtener todos los grupos (con cache) | Get all groups (with cache) */
  obtenerGrupos(): Observable<IGrupoProducto[]> {
    if (!this._gruposCache$) {
      this._gruposCache$ = this.http.get<IGrupoProducto[]>(URL_API_GRUPOS).pipe(
        shareReplay(1)
      );
    }
    return this._gruposCache$;
  }

  /** Limpiar caché (útil después de crear un grupo) | Clear cache (useful after creating a group) */
  limpiarCache(): void {
    this._gruposCache$ = null;
  }
}
