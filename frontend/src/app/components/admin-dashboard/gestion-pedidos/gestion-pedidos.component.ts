// **Actualizado:** 17 de junio de 2026 — Tarea #6: Refinamiento Gestión de Pedidos
// Español: tabla profesional con IVA dinámico, estados mapeados, detalle de productos y origen claro

import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrderService, Pedido, ItemPedido } from '../../../services/order.service';
import { FormsModule } from '@angular/forms';
import { catchError } from 'rxjs/operators';
import { throwError, Subscription } from 'rxjs';
import { AuthService } from '../../../services/auth.service';
import { ConfiguracionService } from '../../../services/configuracion.service';

@Component({
  selector: 'app-gestion-pedidos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './gestion-pedidos.component.html',
  styleUrls: ['./gestion-pedidos.component.css']
})
export class GestionPedidosComponent implements OnInit, OnDestroy {
  private orderService = inject(OrderService);
  private authService = inject(AuthService);
  private configService = inject(ConfiguracionService);

  pedidos: Pedido[] = [];
  cargando = true;

  // Español: IVA dinámico desde configuración | English: dynamic VAT from config
  ivaDecimal = 0.19;

  // Signals para UI
  mostrarToast = signal(false);
  mensajeToast = signal('');

  // Detalle del pedido
  pedidoDetalle: Pedido | null = null;
  mostrarDetalle = false;

  // Español: estados mapeados para gestión de pedidos | English: mapped states for order management
  // Pendiente → pedido recién creado (visible en cocina como 'pendiente')
  // En Preparación → cocina está trabajando en él (visible en cocina como 'en_preparacion')
  // Pagado → pedido completado/pagado
  estadosDisponibles = ['PENDIENTE', 'EN_PREPARACION', 'PAGADO'];

  private sub: Subscription | null = null;

  // Filtro de tipo de pedido | Order type filter
  filtroTipo: string = 'todos';

  get pedidosFiltrados(): Pedido[] {
    if (this.filtroTipo === 'todos') return this.pedidos;
    return this.pedidos.filter(p => this.getTipoPedido(p) === this.filtroTipo);
  }

  getTipoPedido(pedido: Pedido): string {
    if (pedido.tipo) return pedido.tipo;
    return pedido.direccion_entrega ? 'domicilio' : 'mesa';
  }

  getTipoLabel(pedido: Pedido): string {
    return this.getTipoPedido(pedido) === 'domicilio' ? '🚚 Domicilio' : '🪑 Mesa';
  }

  getTipoClase(pedido: Pedido): string {
    return this.getTipoPedido(pedido) === 'domicilio' ? 'badge-delivery' : 'badge-mesa';
  }

  // Español: obtener nombre legible del cliente según tipo de pedido
  // English: get readable client name based on order type
  getClienteLabel(pedido: Pedido): string {
    if (pedido.cliente) return pedido.cliente;
    const id = pedido.cliente_id ?? pedido.usuario_id;
    if (!id) return '—';
    return `Usuario #${id}`;
  }

  // Español: resumen de productos para la tabla (primeros 2 artículos + contador)
  // English: product summary for the table (first 2 items + counter)
  getResumenProductos(articulos: ItemPedido[] | undefined): string {
    if (!articulos || articulos.length === 0) return '—';
    const primeros = articulos.slice(0, 2);
    const resumen = primeros.map(a => `${a.nombre || 'Producto'} x${a.cantidad || 1}`).join(', ');
    if (articulos.length > 2) {
      return `${resumen} y ${articulos.length - 2} más`;
    }
    return resumen;
  }

  ngOnInit(): void {
    // Español: cargar IVA dinámico desde configuración | English: load dynamic VAT from config
    this.configService.obtener().subscribe({
      next: (resp) => {
        if (resp.status === 'success') {
          this.ivaDecimal = (resp.configuracion.porcentaje_iva || 19) / 100;
        }
      },
      error: () => {
        this.ivaDecimal = 0.19; // fallback
      },
    });

    this.sub = this.authService.sesionActiva$.subscribe(sesion => {
      if (sesion) {
        this.cargarTodosLosPedidos();
      } else {
        this.cargando = false;
      }
    });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }

  cargarTodosLosPedidos(): void {
    this.cargando = true;
    this.orderService.obtenerPedidos().subscribe({
      next: (res) => {
        this.pedidos = res?.pedidos || [];
        this.cargando = false;
      },
      error: (err) => {
        console.error('❌ Error al cargar pedidos:', err);
        this.pedidos = [];
        this.cargando = false;
      }
    });
  }

  // Español: cambiar estado del pedido | English: change order status
  cambiarEstado(pedido: Pedido, nuevoEstado: string): void {
    this.orderService.actualizarEstado(pedido.id, nuevoEstado).pipe(
      catchError(err => {
        this.lanzarToast('❌ Error al actualizar el estado');
        return throwError(() => err);
      })
    ).subscribe(() => {
      pedido.estado = nuevoEstado;
      this.lanzarToast(`✅ Estado actualizado: ${this.getEstadoLabel(nuevoEstado)}`);
    });
  }

  // Español: obtener etiqueta legible para un estado | English: readable label for a status
  getEstadoLabel(estado: string | undefined): string {
    const e = (estado || '').toUpperCase();
    const mapa: Record<string, string> = {
      'PENDIENTE': '⏳ Pendiente',
      'EN_PREPARACION': '👨‍🍳 En Preparación',
      'PAGADO': '✅ Pagado',
      'PAGADA': '✅ Pagado',
      'ENTREGADO': '✅ Entregado',
      'LISTO': '✅ Listo',
    };
    return mapa[e] || estado || 'Pendiente';
  }

  // Español: clase CSS para el badge de estado | English: CSS class for status badge
  getEstadoClase(estado: string | undefined): string {
    const e = (estado || '').toLowerCase();
    if (e === 'pendiente') return 'badge-pendiente';
    if (e === 'en_preparacion') return 'badge-preparacion';
    if (e === 'pagado' || e === 'pagada' || e === 'entregado' || e === 'listo') return 'badge-pagado';
    return 'badge-default';
  }

  verDetalle(pedido: Pedido): void {
    this.pedidoDetalle = pedido;
    this.mostrarDetalle = true;
  }

  cerrarDetalle(): void {
    this.mostrarDetalle = false;
    this.pedidoDetalle = null;
  }

  // Español: subtotal desde el backend (respuesta ya incluye IVA dinámico)
  // English: subtotal from backend (response already includes dynamic VAT)
  subtotalPedido(pedido: Pedido): number {
    if (pedido.subtotal !== undefined) return pedido.subtotal;
    // Español: fallback con IVA dinámico | English: fallback with dynamic VAT
    return Math.round((pedido.total ?? 0) / (1 + this.ivaDecimal));
  }

  ivaPedido(pedido: Pedido): number {
    if (pedido.iva !== undefined) return pedido.iva;
    // Español: fallback con IVA dinámico | English: fallback with dynamic VAT
    return Math.round((pedido.total ?? 0) - this.subtotalPedido(pedido));
  }

  // Español: porcentaje de IVA para mostrar en UI | English: VAT percentage for UI
  get ivaPorcentaje(): number {
    return Math.round(this.ivaDecimal * 100);
  }

  private lanzarToast(mensaje: string): void {
    this.mensajeToast.set(mensaje);
    this.mostrarToast.set(true);
    setTimeout(() => this.mostrarToast.set(false), 3000);
  }
}
