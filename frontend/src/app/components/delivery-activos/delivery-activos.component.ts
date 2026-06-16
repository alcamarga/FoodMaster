// Componente de pedidos activos para domiciliarios.
// Español: lista pedidos pendientes de entrega y permite asignarse y registrar pagos | English: lists pending deliveries and allows assignment and payment registration

import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { DeliveryService, DeliveryPedido } from '../../services/delivery.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-delivery-activos',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './delivery-activos.component.html',
  styleUrls: ['./delivery-activos.component.css'],
})
export class DeliveryActivosComponent implements OnInit {
  private deliveryService = inject(DeliveryService);
  private auth = inject(AuthService);

  pedidos = signal<DeliveryPedido[]>([]);
  cargando = signal(true);
  error = signal<string | null>(null);
  usuario = this.auth.obtenerUsuarioActual();

  // Estado para modales
  pedidoPago: DeliveryPedido | null = null;
  metodoPagoSeleccionado: string = 'Efectivo';
  procesando = signal(false);
  mensajeExito = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarActivos();
  }

  cargarActivos(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.deliveryService.obtenerActivos().subscribe({
      next: (res) => {
        this.pedidos.set(res.pedidos);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('[DeliveryActivos] Error:', err);
        this.error.set('No se pudieron cargar los pedidos activos.');
        this.cargando.set(false);
      },
    });
  }

  asignar(pedidoId: number): void {
    if (!confirm('¿Asignarte este pedido?')) return;
    this.procesando.set(true);
    this.deliveryService.asignarPedido(pedidoId).subscribe({
      next: () => {
        this.mensajeExito.set('✅ Pedido asignado correctamente');
        this.procesando.set(false);
        this.cargarActivos();
        setTimeout(() => this.mensajeExito.set(null), 3000);
      },
      error: (err) => {
        alert(err.error?.error || 'Error al asignar pedido');
        this.procesando.set(false);
      },
    });
  }

  liberar(pedidoId: number): void {
    if (!confirm('¿Liberar este pedido?')) return;
    this.procesando.set(true);
    this.deliveryService.liberarPedido(pedidoId).subscribe({
      next: () => {
        this.mensajeExito.set('✅ Pedido liberado');
        this.procesando.set(false);
        this.cargarActivos();
        setTimeout(() => this.mensajeExito.set(null), 3000);
      },
      error: (err) => {
        alert(err.error?.error || 'Error al liberar pedido');
        this.procesando.set(false);
      },
    });
  }

  abrirModalPago(pedido: DeliveryPedido): void {
    this.pedidoPago = pedido;
    this.metodoPagoSeleccionado = 'Efectivo';
  }

  cerrarModalPago(): void {
    this.pedidoPago = null;
  }

  confirmarPago(): void {
    if (!this.pedidoPago) return;
    this.procesando.set(true);
    this.deliveryService.registrarPago(this.pedidoPago.id, this.metodoPagoSeleccionado).subscribe({
      next: () => {
        this.mensajeExito.set(`✅ Pago registrado: ${this.metodoPagoSeleccionado}`);
        this.procesando.set(false);
        this.cerrarModalPago();
        this.cargarActivos();
        setTimeout(() => this.mensajeExito.set(null), 3000);
      },
      error: (err) => {
        alert(err.error?.error || 'Error al registrar pago');
        this.procesando.set(false);
      },
    });
  }

  getBadgeClass(estado: string): string {
    const clases: Record<string, string> = {
      listo: 'badge-success',
      en_camino: 'badge-info',
      en_preparacion: 'badge-warning',
    };
    return clases[estado.toLowerCase()] || 'badge-secondary';
  }
}
