// Componente de seguimiento de pedido con timeline y QR.
// Español: muestra el estado del pedido en una línea de tiempo y genera un código QR | English: shows order status in a timeline and generates a QR code

import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { DeliveryService, SeguimientoPedido } from '../../services/delivery.service';
import * as QRCode from 'qrcode';

@Component({
  selector: 'app-seguimiento-pedido',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './seguimiento-pedido.component.html',
  styleUrls: ['./seguimiento-pedido.component.css'],
})
export class SeguimientoPedidoComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private deliveryService = inject(DeliveryService);

  pedido = signal<SeguimientoPedido | null>(null);
  cargando = signal(true);
  error = signal<string | null>(null);
  qrDataUrl = signal<string | null>(null);
  qrGenerado = signal(false);

  ngOnInit(): void {
    const pedidoId = Number(this.route.snapshot.paramMap.get('id'));
    if (!pedidoId) {
      this.error.set('ID de pedido inválido');
      this.cargando.set(false);
      return;
    }

    this.deliveryService.obtenerSeguimiento(pedidoId).subscribe({
      next: (data) => {
        this.pedido.set(data);
        this.cargando.set(false);
        // Español: generar QR con la URL del pedido | English: generate QR with order URL
        this.generarQR(pedidoId);
      },
      error: (err) => {
        console.error('[Seguimiento] Error:', err);
        this.error.set('No se pudo cargar la información del pedido.');
        this.cargando.set(false);
      },
    });
  }

  private async generarQR(pedidoId: number): Promise<void> {
    try {
      // Español: URL de seguimiento (relativa, se renderiza completa en QR) | English: tracking URL (relative, rendered as full URL in QR)
      const url = `${window.location.origin}/seguimiento/${pedidoId}`;
      const dataUrl = await QRCode.toDataURL(url, {
        width: 220,
        margin: 2,
        color: { dark: '#10b981', light: '#1a1a2e' },
      });
      this.qrDataUrl.set(dataUrl);
      this.qrGenerado.set(true);
    } catch (err) {
      console.error('[Seguimiento] Error al generar QR:', err);
    }
  }

  getEstadoIcon(estado: string): string {
    const iconos: Record<string, string> = {
      pendiente: '📝',
      en_preparacion: '👨‍🍳',
      listo: '✅',
      en_camino: '🚚',
      entregado: '📦',
    };
    return iconos[estado.toLowerCase()] || '📋';
  }
}
