import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface RecetaItem {
  id?: number;
  pizza_id: number;
  insumo_id: number;
  insumo_nombre?: string;
  cantidad_gastada: number;
  unidad_medida?: string;
}

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private http = inject(HttpClient);
  private apiUrl = `${environment.apiUrl}/productos`;

  obtenerReceta(pizzaId: number, size?: string): Observable<{ receta: RecetaItem[] }> {
    const url = `${this.apiUrl}/${pizzaId}/receta${size ? '?size=' + size : ''}`;
    return this.http.get<{ receta: RecetaItem[] }>(url);
  }

  guardarReceta(pizzaId: number, receta: RecetaItem[], size?: string): Observable<any> {
    const url = `${this.apiUrl}/${pizzaId}/receta${size ? '?size=' + size : ''}`;
    return this.http.post(url, receta);
  }
}
