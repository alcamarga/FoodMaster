import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OrderService, Pedido } from '../../services/order.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-mis-pedidos',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './mis-pedidos.component.html',
  styleUrls: ['./mis-pedidos.component.css']
})
export class MisPedidosComponent implements OnInit {
  private orderService = inject(OrderService);
  pedidos: Pedido[] = [];
  cargando = true;

  ngOnInit(): void {
    this.cargarPedidos();
  }

  cargarPedidos(): void {
    this.orderService.obtenerPedidos().subscribe({
      next: (res) => {
        this.pedidos = res.pedidos || [];
        this.cargando = false;
      },
      error: (err) => {
        console.error('Error al cargar pedidos:', err);
        this.cargando = false;
      }
    });
  }

  getBadgeClass(estado: string): string {
    switch (estado.toLowerCase()) {
      case 'pendiente': return 'badge-pendiente';
      case 'preparando': return 'badge-preparando';
      case 'enviado': return 'badge-enviado';
      case 'entregado': return 'badge-entregado';
      case 'cancelado': return 'badge-cancelado';
      default: return 'badge-secondary';
    }
  }
}
