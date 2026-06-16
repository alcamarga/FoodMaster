import { Component, OnInit, OnDestroy, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrderService, Pedido } from '../../../services/order.service';
import { FormsModule } from '@angular/forms';
import { catchError } from 'rxjs/operators';
import { throwError, Subscription } from 'rxjs';
import { AuthService } from '../../../services/auth.service';

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
  
  // BLINDAJE: Inicializamos como arreglo vacío para evitar error de .length
  pedidos: Pedido[] = [];
  cargando = true;

  // Signals para UI
  mostrarToast = signal(false);
  mensajeToast = signal('');

  // Detalle del pedido
  pedidoDetalle: Pedido | null = null;
  mostrarDetalle = false;

  estadosDisponibles = ['Pendiente', 'Preparando', 'Enviado', 'Entregado', 'Cancelado'];
  private sub: Subscription | null = null;

  // Español: filtro de tipo de pedido | English: order type filter
  filtroTipo: string = 'todos'; // 'todos' | 'mesa' | 'domicilio'

  // Español: obtener pedidos filtrados por tipo | English: get orders filtered by type
  get pedidosFiltrados(): Pedido[] {
    if (this.filtroTipo === 'todos') return this.pedidos;
    return this.pedidos.filter(p => this.getTipoPedido(p) === this.filtroTipo);
  }

  // Español: determinar tipo de pedido (Mesa o Domicilio) usando el campo explícito 'tipo' | English: determine order type (Table or Delivery) using explicit 'tipo' field
  getTipoPedido(pedido: Pedido): string {
    // Español: usar el campo 'tipo' si existe; fallback a heurística por direccion_entrega | English: use 'tipo' field if present; fallback to direccion_entrega heuristic
    if (pedido.tipo) return pedido.tipo;
    return pedido.direccion_entrega ? 'domicilio' : 'mesa';
  }

  getTipoLabel(pedido: Pedido): string {
    return this.getTipoPedido(pedido) === 'domicilio' ? '🚚 Domicilio' : '🪑 Mesa';
  }

  getTipoClase(pedido: Pedido): string {
    return this.getTipoPedido(pedido) === 'domicilio' ? 'badge-delivery' : 'badge-mesa';
  }

  ngOnInit(): void {
    // Nos suscribimos al estado de la sesión para cargar los pedidos apenas el admin entre
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
        // Verificamos que la respuesta traiga la propiedad 'pedidos'
        // Si no existe o es nula, asignamos un arreglo vacío
        if (res && res.pedidos) {
          this.pedidos = res.pedidos;
        } else {
          this.pedidos = [];
        }
        this.cargando = false;
        console.log('📦 Pedidos cargados con éxito:', this.pedidos.length);
      },
      error: (err) => {
        console.error('❌ Error al cargar pedidos:', err);
        this.pedidos = []; // Mantenemos el arreglo vacío en caso de error
        this.cargando = false;
      }
    });
  }

  cambiarEstado(pedido: Pedido, nuevoEstado: string): void {
    this.orderService.actualizarEstado(pedido.id, nuevoEstado).pipe(
      catchError(err => {
        this.lanzarToast('❌ Error al actualizar el estado');
        return throwError(() => err);
      })
    ).subscribe(() => {
      pedido.estado = nuevoEstado;
      this.lanzarToast(`✅ Estado actualizado: ${nuevoEstado}`);
    });
  }

  verDetalle(pedido: Pedido): void {
    this.pedidoDetalle = pedido;
    this.mostrarDetalle = true;
  }

  cerrarDetalle(): void {
    this.mostrarDetalle = false;
    this.pedidoDetalle = null;
  }

  subtotalPedido(pedido: Pedido): number {
    return Math.round((pedido.total ?? 0) / 1.19);
  }

  ivaPedido(pedido: Pedido): number {
    return Math.round((pedido.total ?? 0) - this.subtotalPedido(pedido));
  }

  private lanzarToast(mensaje: string): void {
    this.mensajeToast.set(mensaje);
    this.mostrarToast.set(true);
    setTimeout(() => this.mostrarToast.set(false), 3000);
  }
}