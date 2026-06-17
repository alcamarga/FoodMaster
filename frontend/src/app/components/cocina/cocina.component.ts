// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 17 de junio de 2026
// **Estado:** Producción — Tarea #7: Monitor de Cocina

// Componente standalone para el Monitor de Cocina (KDS)
// Muestra SOLO pedidos activos (Pendiente + En Preparación) de Mesa y Domicilio
// Los items 'Despachado' desaparecen del monitor y se consolidan en Gestión de Pedidos al pagar
// Accesible solo para roles: Administrador y Cocinero

import { Component, OnInit, OnDestroy, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';
import { AuthService } from '../../services/auth.service';

// Interfaz unificada para items de cocina (Mesa + Domicilio)
// Unified interface for kitchen items (Dine-in + Delivery)
interface IItemCocina {
  id: number;
  tipo: 'mesa' | 'domicilio';
  origen: string;           // "Mesa #5" o "🛵 Domicilio - Juan"
  origen_detalle: string;   // Texto más descriptivo
  cliente_nombre: string | null;
  direccion_entrega: string;
  telefono_contacto: string;
  mesa_id: number | null;
  numero_mesa: number | null;
  fecha: string;
  estado: string;           // 'pendiente' | 'en_preparacion' | 'despachado'
  estado_modelo: string;    // Estado real en BD
  articulos: { producto_id?: number; nombre: string; precio: number; cantidad: number }[];
  total: number;
  usuario_id: number | null;
  tiempo_espera?: string;
}

interface IRespuestaCocina {
  status: string;
  items: IItemCocina[];
  totales: {
    pendientes: number;
    en_preparacion: number;
  };
  total_items: number;
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
  items = signal<IItemCocina[]>([]);
  cargando = signal(true);
  error = signal<string | null>(null);
  mensajeExito = signal<string | null>(null);

  // Español: totales del monitor de cocina (solo estados activos: pendiente + en_preparacion)
  // English: kitchen monitor totals (only active states: pendiente + en_preparacion)
  totalPendientes = computed(() => this.items().filter(i => i.estado === 'pendiente').length);
  totalEnPreparacion = computed(() => this.items().filter(i => i.estado === 'en_preparacion').length);
  totalItems = computed(() => this.items().length);

  // Español: filtro por origen | English: origin filter
  filtroOrigen = signal<string | null>(null); // null = todos, 'mesa', 'domicilio'
  itemsFiltrados = computed(() => {
    const filtro = this.filtroOrigen();
    if (!filtro) return this.items();
    return this.items().filter(i => i.tipo === filtro);
  });

  // Español: intervalos de refresco automático | English: auto-refresh intervals
  private intervalRefresco: ReturnType<typeof setInterval> | null = null;
  private intervalTiempo: ReturnType<typeof setInterval> | null = null;

  ngOnInit(): void {
    this.cargarItems();
    // Español: refrescar cada 15 segundos | English: refresh every 15 seconds
    this.intervalRefresco = setInterval(() => this.cargarItems(), 15000);
    // Español: actualizar tiempos de espera cada 30 segundos | English: update wait times every 30 seconds
    this.intervalTiempo = setInterval(() => this.actualizarTiemposEspera(), 30000);
  }

  ngOnDestroy(): void {
    if (this.intervalRefresco) clearInterval(this.intervalRefresco);
    if (this.intervalTiempo) clearInterval(this.intervalTiempo);
  }

  // Español: cargar items desde el endpoint unificado de cocina
  // English: load items from the unified kitchen endpoint
  cargarItems(): void {
    this.http.get<IRespuestaCocina>(`${this.apiUrl}/kitchen/pendientes`).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success') {
          this.items.set(respuesta.items);
          this.actualizarTiemposEspera();
        }
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('[Cocina] Error al cargar items:', err);
        this.error.set('Error al cargar los pedidos de cocina. Verifica la conexión.');
        this.cargando.set(false);
      },
    });
  }

  // Español: actualizar tiempos de espera | English: update wait times
  private actualizarTiemposEspera(): void {
    this.items.update(items =>
      items.map(item => ({
        ...item,
        tiempo_espera: this.calcularTiempoEspera(item.fecha),
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

  // Español: actualizar estado de un item (comanda o pedido) | English: update item status
  cambiarEstado(item: IItemCocina, nuevoEstado: string): void {
    this.http.put(`${this.apiUrl}/kitchen/${item.id}/estado`, {
      tipo: item.tipo,
      estado: nuevoEstado,
    }).subscribe({
      next: (respuesta: any) => {
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`✅ ${respuesta.message}`);
          this.cargarItems();
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

  // Español: iniciar preparación | English: start preparation
  iniciarPreparacion(item: IItemCocina): void {
    this.cambiarEstado(item, 'en_preparacion');
  }

  // Español: marcar como despachado (listo) | English: mark as dispatched (ready)
  marcarDespachado(item: IItemCocina): void {
    this.cambiarEstado(item, 'despachado');
  }

  // Español: establecer filtro por origen | English: set origin filter
  setFiltroOrigen(origen: string | null): void {
    this.filtroOrigen.set(origen);
  }

  // Español: volver al menú principal | English: return to main menu
  salir(): void {
    this.auth.cerrarSesion();
  }
}
