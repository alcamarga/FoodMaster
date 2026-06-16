// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo

// Componente standalone para el módulo de cocina | Standalone component for the kitchen module

import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../services/auth.service';

// Interfaces locales para comandas de cocina | Local interfaces for kitchen comandas
interface IComandaCocina {
  id: number;
  mesa_id: number;
  numero_mesa: number;
  fecha: string;
  total: number;
  estado: string;
  articulos: { producto_id?: number; nombre: string; precio: number; cantidad: number }[];
  tiempo_espera?: string; // Tiempo transcurrido formateado | Elapsed time formatted
}

interface IRespuestaComandas {
  status: string;
  comandas: IComandaCocina[];
}

@Component({
  selector: 'app-cocina',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './cocina.component.html',
  styleUrls: ['./cocina.component.css'],
})
export class CocinaComponent implements OnInit, OnDestroy {
  private http = inject(HttpClient);
  private auth = inject(AuthService);
  private router = inject(Router);
  private apiUrl = environment.apiUrl;

  // Español: estado reactivo | English: reactive state
  comandas = signal<IComandaCocina[]>([]);
  cargando = signal(true);
  error = signal<string | null>(null);
  mensajeExito = signal<string | null>(null);

  // Español: totales del dashboard | English: dashboard totals
  totalPendientes = computed(() => this.comandas().length);
  totalEnPreparacion = computed(() => this.comandas().filter(c => c.estado === 'en_preparacion').length);
  totalListos = computed(() => this.comandas().filter(c => c.estado === 'listo').length);

  // Español: intervalos de refresco automático | English: auto-refresh intervals
  private intervalRefresco: ReturnType<typeof setInterval> | null = null;
  private intervalTiempo: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.cargarComandas();
    // Español: refrescar comandas cada 15 segundos | English: refresh comandas every 15 seconds
    this.intervalRefresco = setInterval(() => this.cargarComandas(), 15000);
    // Español: actualizar tiempos de espera cada 30 segundos | English: update wait times every 30 seconds
    this.intervalTiempo = setInterval(() => this.actualizarTiemposEspera(), 30000);
  }

  ngOnDestroy(): void {
    if (this.intervalRefresco) clearInterval(this.intervalRefresco);
    if (this.intervalTiempo) clearInterval(this.intervalTiempo);
  }

  // Español: cargar comandas activas desde el backend | English: load active comandas from backend
  cargarComandas(): void {
    this.http.get<IRespuestaComandas>(`${this.apiUrl}/comandas/activas`).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success') {
          this.comandas.set(respuesta.comandas);
          this.actualizarTiemposEspera();
        }
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('[Cocina] Error al cargar comandas:', err);
        this.error.set('Error al cargar las comandas activas. Verifica la conexión.');
        this.cargando.set(false);
      },
    });
  }

  // Español: actualizar tiempos de espera de cada comanda | English: update wait times for each comanda
  private actualizarTiemposEspera(): void {
    this.comandas.update(comandas =>
      comandas.map(c => ({
        ...c,
        tiempo_espera: this.calcularTiempoEspera(c.fecha),
      }))
    );
  }

  // Español: calcular tiempo transcurrido desde creación | English: calculate elapsed time since creation
  private calcularTiempoEspera(fechaISO: string): string {
    if (!fechaISO) return '—';
    const creada = new Date(fechaISO).getTime();
    const ahora = new Date().getTime();
    const diffMin = Math.floor((ahora - creada) / 60000);

    if (diffMin < 1) return 'Recién llegada';
    if (diffMin < 60) return `${diffMin} min`;
    const horas = Math.floor(diffMin / 60);
    const mins = diffMin % 60;
    return `${horas}h ${mins}min`;
  }

  // Español: obtener clase CSS según tiempo de espera | English: get CSS class based on wait time
  claseEstadoTiempo(fechaISO: string): string {
    if (!fechaISO) return '';
    const creada = new Date(fechaISO).getTime();
    const ahora = new Date().getTime();
    const diffMin = Math.floor((ahora - creada) / 60000);
    if (diffMin > 30) return 'critico';
    if (diffMin > 15) return 'alerta';
    return 'normal';
  }

  // Español: actualizar estado de una comanda | English: update comanda status
  cambiarEstadoComanda(comandaId: number, nuevoEstado: string): void {
    this.http.put(`${this.apiUrl}/comandas/${comandaId}/estado`, { estado: nuevoEstado }).subscribe({
      next: (respuesta: any) => {
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`✅ ${respuesta.message}`);
          this.cargarComandas();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      },
      error: (err) => {
        console.error('[Cocina] Error al actualizar estado:', err);
        this.error.set(err.error?.message || 'Error al actualizar estado');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Español: marcar comanda como "en preparación" | English: mark comanda as "in preparation"
  iniciarPreparacion(comandaId: number): void {
    this.cambiarEstadoComanda(comandaId, 'en_preparacion');
  }

  // Español: marcar comanda como "listo para servir" | English: mark comanda as "ready to serve"
  marcarListo(comandaId: number): void {
    this.cambiarEstadoComanda(comandaId, 'listo');
  }

  // Español: volver al menú principal | English: return to main menu
  salir(): void {
    this.auth.cerrarSesion();
  }
}
