// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

// Componente standalone para gestión financiera y cierre de caja | Standalone component for financial management and cash closure

import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

// Interfaces para datos financieros | Interfaces for financial data
export interface IVentaItem {
  tipo: 'pedido' | 'comanda';
  id: number;
  origen: string;
  total: number;
  estado: string;
  fecha: string;
  articulos: any[];
}

export interface IRespuestaVentas {
  status: string;
  fecha: string;
  total_ventas: number;
  cantidad_ventas: number;
  ventas: IVentaItem[];
}

export interface IResumenCierre {
  fecha: string;
  usuario_id: number | null;
  total_ventas_sistema: number;
  efectivo_declarado: number;
  digital_declarado: number;
  total_ingresos: number;
  egresos: number;
  total_esperado: number;
  diferencia: number;
  estado: string;
  notas: string;
  cantidad_transacciones: number;
}

export interface IRespuestaCierre {
  status: string;
  message: string;
  resumen: IResumenCierre;
}

@Component({
  selector: 'app-finanzas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './finanzas.component.html',
  styleUrls: ['./finanzas.component.css'],
})
export class FinanzasComponent implements OnInit {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // Estados principales | Main states
  ventas = signal<IVentaItem[]>([]);
  totalVentas = signal(0);
  cantidadVentas = signal(0);
  cargando = signal(true);
  error = signal<string | null>(null);
  mensajeExito = signal<string | null>(null);

  // Filtro de fecha | Date filter
  fechaActual = signal(new Date().toISOString().split('T')[0]);

  // Estado del modal de cierre | Closure modal state
  mostrarModalCierre = false;
  efectivoIngresado = 0;
  digitalIngresado = 0;
  egresosIngresados = 0;
  notasCierre = '';
  procesandoCierre = signal(false);

  // Resultado del cierre | Closure result
  resultadoCierre = signal<IResumenCierre | null>(null);

  // Español: estado del modal de detalle de venta | English: sale detail modal state
  ventaDetalle = signal<IVentaItem | null>(null);
  mostrarDetalleVenta = false;

  ngOnInit(): void {
    this.cargarVentas();
  }

  // Cargar ventas desde el backend | Load sales from backend
  cargarVentas(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.http.get<IRespuestaVentas>(`${this.apiUrl}/caja/ventas?fecha=${this.fechaActual()}`).subscribe({
      next: (respuesta) => {
        this.ventas.set(respuesta.ventas);
        this.totalVentas.set(respuesta.total_ventas);
        this.cantidadVentas.set(respuesta.cantidad_ventas);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('[Finanzas] Error al cargar ventas:', err);
        this.error.set('No se pudieron cargar las ventas. Verifica la conexión con el servidor.');
        this.cargando.set(false);
      },
    });
  }

  // Cambiar fecha de filtro | Change filter date
  cambiarFecha(): void {
    this.cargarVentas();
  }

  // Abrir modal de cierre de caja | Open cash closure modal
  abrirModalCierre(): void {
    this.mostrarModalCierre = true;
    this.efectivoIngresado = Math.round(this.totalVentas() * 0.6);
    this.digitalIngresado = Math.round(this.totalVentas() * 0.4);
    this.egresosIngresados = 0;
    this.notasCierre = '';
    this.resultadoCierre.set(null);
  }

  // Cerrar modal de cierre | Close cash closure modal
  cerrarModalCierre(): void {
    this.mostrarModalCierre = false;
    this.resultadoCierre.set(null);
  }

  // Ejecutar cierre de caja (POST al backend) | Execute cash closure (POST to backend)
  ejecutarCierre(): void {
    if (!confirm('⚠️ ¿Estás seguro de realizar el cierre de caja? Los registros del día quedarán bloqueados.')) {
      return;
    }

    this.procesandoCierre.set(true);
    const payload = {
      efectivo: this.efectivoIngresado,
      digital: this.digitalIngresado,
      egresos: this.egresosIngresados,
      notas: this.notasCierre,
    };

    this.http.post<IRespuestaCierre>(`${this.apiUrl}/caja/cierre`, payload).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success') {
          this.resultadoCierre.set(respuesta.resumen);
          this.mensajeExito.set(respuesta.message);
          setTimeout(() => this.mensajeExito.set(null), 5000);
        }
        this.procesandoCierre.set(false);
      },
      error: (err) => {
        console.error('[Finanzas] Error al realizar cierre:', err);
        this.error.set(err.error?.message || 'Error al procesar el cierre de caja');
        this.procesandoCierre.set(false);
        setTimeout(() => this.error.set(null), 5000);
      },
    });
  }

  // Calcular subtotal de artículos | Calculate subtotal of items
  calcularSubtotal(articulos: any[]): number {
    return (articulos || []).reduce((sum, a) => {
      return sum + (a.precio || a.precio_unitario || 0) * (a.cantidad || 1);
    }, 0);
  }

  // Calcular IVA (19%) | Calculate VAT (19%)
  calcularIVA(subtotal: number): number {
    return Math.round(subtotal * 0.19);
  }

  // Español: abrir detalle de venta | English: open sale detail
  abrirDetalle(venta: IVentaItem): void {
    this.ventaDetalle.set(venta);
    this.mostrarDetalleVenta = true;
  }

  // Español: cerrar detalle de venta | English: close sale detail
  cerrarDetalle(): void {
    this.mostrarDetalleVenta = false;
    this.ventaDetalle.set(null);
  }

  // Formatear fecha ISO a legible | Format ISO date to readable
  formatearFecha(iso: string): string {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleString('es-CO', {
      hour: '2-digit',
      minute: '2-digit',
      day: '2-digit',
      month: '2-digit',
    });
  }
}
