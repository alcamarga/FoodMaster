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

  // ----------------------------------------------------------------
  // FILTRO DE TIPO DE PEDIDO | ORDER TYPE FILTER
  // ----------------------------------------------------------------
  // Español: El campo 'tipo' en el modelo Pedido puede ser:
  //   - 'mesa'      → pedido de salón
  //   - 'domicilio' → pedido de delivery
  //   - null/undefined → pedidos antiguos: fallback heurístico por direccion_entrega
  //
  // English: The 'tipo' field in the Pedido model can be:
  //   - 'mesa'      → dine-in order
  //   - 'domicilio' → delivery order
  //   - null/undefined → legacy orders: heuristic fallback by direccion_entrega
  //
  // Flujo de creación de pedidos:
  //
  //   🚚 Domicilio (tipo='domicilio'):
  //     1. Cliente agrega productos al carrito en menu.component
  //     2. Cliente confirma pedido en resumen-pedido.component
  //     3. CartService.confirmarPedido() → POST /api/pedidos
  //     4. Backend: pedido_routes.py asigna tipo='domicilio' por defecto
  //     5. Aparece en Gestión de Pedidos con badge 🚚 Domicilio
  //
  //   🪑 Mesa (tipo='mesa'):
  //     Opción A — Desde Comanda (recomendado):
  //       1. Mesero abre comanda → POST /api/mesas/<id>/comanda
  //       2. Agrega productos → POST /api/mesas/<id>/agregar
  //       3. Cliente paga → POST /api/mesas/<id>/comanda/<id>/pagar
  //       4. Backend: mesa_routes.py crea Pedido con tipo='mesa'
  //       5. Aparece en Gestión de Pedidos con badge 🪑 Mesa
  //
  //     Opción B — Directo (admin):
  //       1. POST /api/pedidos con {"tipo":"mesa", ...}
  //       2. Backend: pedido_routes.py acepta el tipo explícito
  //
  //   Filtro reactivo:
  //     - 'todos':    muestra todos los pedidos sin filtrar
  //     - 'mesa':     filtra pedidos donde getTipoPedido() === 'mesa'
  //     - 'domicilio': filtra pedidos donde getTipoPedido() === 'domicilio'
  //     - El getter pedidosFiltrados se recalcula automáticamente
  //       cuando cambia filtroTipo o pedidos (reactividad de Angular)
  // ----------------------------------------------------------------
  filtroTipo: string = 'todos'; // 'todos' | 'mesa' | 'domicilio'

  // Español: getter reactivo — se actualiza automáticamente al cambiar filtroTipo o pedidos | English: reactive getter — auto-updates on filtroTipo or pedidos change
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

  // Español: usar subtotal/IVA calculados por el backend desde articulos_json | English: use subtotal/VAT calculated by backend from articulos_json
  subtotalPedido(pedido: Pedido): number {
    if (pedido.subtotal !== undefined) return pedido.subtotal;
    // Español: fallback para pedidos antiguos sin subtotal en el payload | English: fallback for old orders without subtotal in payload
    return Math.round((pedido.total ?? 0) / 1.19);
  }

  ivaPedido(pedido: Pedido): number {
    if (pedido.iva !== undefined) return pedido.iva;
    // Español: fallback para pedidos antiguos sin iva en el payload | English: fallback for old orders without iva in payload
    return Math.round((pedido.total ?? 0) - this.subtotalPedido(pedido));
  }

  private lanzarToast(mensaje: string): void {
    this.mensajeToast.set(mensaje);
    this.mostrarToast.set(true);
    setTimeout(() => this.mostrarToast.set(false), 3000);
  }
}