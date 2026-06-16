// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo
// Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

// Componente standalone para la gestión visual de mesas y comandas | Standalone component for visual table and order management

import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MesaService } from '../../services/mesa.service';
import { PizzaService } from '../../services/pizza.service';
import { AuthService } from '../../services/auth.service';
import { IMesa, IComanda, IArticuloComanda } from '../../models/mesa.model';
import { Pizza } from '../../models/pizza.model';

@Component({
  selector: 'app-mesas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './mesas.component.html',
  styleUrls: ['./mesas.component.css'],
})
export class MesasComponent implements OnInit {
  // Inyección de servicios | Service injection
  readonly mesaService = inject(MesaService);
  readonly pizzaService = inject(PizzaService);
  readonly auth = inject(AuthService);
  readonly esAdmin = computed(() => this.auth.obtenerUsuarioActual()?.rol === 'admin');

  // Estado principal | Main state
  mesas = signal<IMesa[]>([]);
  productos = signal<Pizza[]>([]);
  cargando = signal(true);
  error = signal<string | null>(null);
  mensajeExito = signal<string | null>(null);

  // Estado de acciones de pago | Payment action state
  cargandoAccionMesa = false;
  totalCuentaReal = 0;

  // Modal de nueva mesa | New table modal
  mostrarModalNuevaMesa = false;
  nuevaMesaNumero: number | null = null;
  creandoMesa = false;

  // Modal de comanda activa | Active comanda modal
  mesaSeleccionada = signal<IMesa | null>(null);
  comandaActiva = signal<IComanda | null>(null);
  mostrarModalComanda = false;

  // Modal para agregar producto | Add product modal
  mostrarModalProducto = false;
  productoSeleccionado: Pizza | null = null;
  cantidadProducto = 1;

  // Modal de historial de comandas | Comanda history modal
  historialComandas = signal<IComanda[]>([]);
  mostrarHistorial = false;

  // Búsqueda de productos | Product search
  busquedaProducto = '';

  ngOnInit(): void {
    this.cargarMesas();
    this.cargarProductos();
  }

  // Cargar lista de mesas desde el backend | Load table list from backend
  cargarMesas(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.mesaService.obtenerMesas().subscribe({
      next: (mesas) => {
        this.mesas.set(mesas);
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('[MesasComponent] Error al cargar mesas:', err);
        this.error.set('No se pudieron cargar las mesas. Verifica la conexión con el servidor.');
        this.cargando.set(false);
      },
    });
  }

  // Cargar catálogo de productos disponibles | Load available product catalog
  cargarProductos(): void {
    this.pizzaService.obtenerCatalogoPizzas().subscribe({
      next: (productos) => {
        this.productos.set(productos);
      },
      error: (err) => {
        console.error('[MesasComponent] Error al cargar productos:', err);
      },
    });
  }

  // Abrir el modal de comanda para una mesa | Open comanda modal for a table
  gestionarMesa(mesa: IMesa): void {
    this.mesaSeleccionada.set(mesa);
    this.mostrarModalComanda = true;
    this.comandaActiva.set(null);

    if (mesa.estado === 'OCUPADA') {
      this.mesaService.obtenerMesa(mesa.id).subscribe({
        next: (mesaCompleta) => {
          if (mesaCompleta.comanda_activa) {
            this.comandaActiva.set(mesaCompleta.comanda_activa);
            this.totalCuentaReal = mesaCompleta.comanda_activa.total;
            this.cargandoAccionMesa = false;
          }
        },
        error: (err) => {
          console.error('[MesasComponent] Error al obtener detalle de mesa:', err);
          this.cargandoAccionMesa = false;
        },
      });
    }
  }

  // Cerrar el modal de comanda | Close comanda modal
  cerrarModalComanda(): void {
    this.mostrarModalComanda = false;
    this.mesaSeleccionada.set(null);
    this.comandaActiva.set(null);
  }

  // Abrir una nueva comanda en la mesa seleccionada | Open a new order on the selected table
  abrirComanda(): void {
    const mesa = this.mesaSeleccionada();
    if (!mesa) return;

    this.mesaService.abrirComanda(mesa.id).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success' && respuesta.comanda) {
          this.comandaActiva.set(respuesta.comanda);
          this.mensajeExito.set(respuesta.message);
          this.cargarMesas();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      },
      error: (err) => {
        console.error('[MesasComponent] Error al abrir comanda:', err);
        this.error.set(err.error?.message || 'Error al abrir la comanda');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Abrir modal para agregar producto | Open add product modal
  abrirModalProducto(): void {
    this.mostrarModalProducto = true;
    this.productoSeleccionado = null;
    this.cantidadProducto = 1;
    this.busquedaProducto = '';
  }

  // Cerrar modal de producto | Close product modal
  cerrarModalProducto(): void {
    this.mostrarModalProducto = false;
    this.productoSeleccionado = null;
  }

  // Agregar producto seleccionado a la comanda | Add selected product to the comanda
  agregarProducto(): void {
    const mesa = this.mesaSeleccionada();
    const producto = this.productoSeleccionado;
    if (!mesa || !producto) return;

    const precio = producto.precio_1 || producto.precio_2 || producto.precio_3 || 0;

    this.mesaService.agregarProducto(mesa.id, {
      producto_id: producto.id,
      nombre: producto.nombre,
      precio: precio,
      cantidad: this.cantidadProducto,
    }).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success' && respuesta.comanda) {
          this.comandaActiva.set(respuesta.comanda);
          this.totalCuentaReal = respuesta.comanda.total;
          this.mensajeExito.set(`✅ ${producto.nombre} x${this.cantidadProducto} agregado`);
          this.cerrarModalProducto();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      },
      error: (err) => {
        console.error('[MesasComponent] Error al agregar producto:', err);
        this.error.set(err.error?.message || 'Error al agregar producto');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Pagar la comanda activa | Pay the active comanda
  pagarComanda(): void {
    const mesa = this.mesaSeleccionada();
    const comanda = this.comandaActiva();
    if (!mesa || !comanda) return;

    if (!confirm('¿Confirmar pago de la comanda? La mesa quedará libre.')) return;

    this.cargandoAccionMesa = true;

    this.mesaService.pagarComanda(mesa.id, comanda.id).subscribe({
      next: (respuesta) => {
        this.cargandoAccionMesa = false;
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`💰 ${respuesta.message}`);
          this.totalCuentaReal = 0;
          this.cerrarModalComanda();
          this.cargarMesas();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      },
      error: (err) => {
        this.cargandoAccionMesa = false;
        console.error('[MesasComponent] Error al pagar comanda:', err);
        this.error.set(err.error?.message || 'Error al procesar el pago');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Cerrar la comanda activa sin pago | Close the active comanda without payment
  cerrarComanda(): void {
    const mesa = this.mesaSeleccionada();
    const comanda = this.comandaActiva();
    if (!mesa || !comanda) return;

    if (!confirm('¿Cerrar la comanda sin pago? La mesa quedará libre.')) return;

    this.mesaService.cerrarComanda(mesa.id, comanda.id).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`🔒 ${respuesta.message}`);
          this.cerrarModalComanda();
          this.cargarMesas();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      },
      error: (err) => {
        console.error('[MesasComponent] Error al cerrar comanda:', err);
        this.error.set(err.error?.message || 'Error al cerrar la comanda');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Iniciar flujo de pago en efectivo | Start cash payment flow
  abrirPagoEfectivo(): void {
    this.cobrarYFacturarMesa('Efectivo');
  }

  // Cobrar y facturar la comanda según el tipo de pago | Charge and invoice the comanda by payment type
  cobrarYFacturarMesa(tipo: string): void {
    const mesa = this.mesaSeleccionada();
    const comanda = this.comandaActiva();
    if (!mesa || !comanda) return;

    if (!confirm(`¿Confirmar pago en ${tipo} por $${comanda.total}? La mesa quedará libre.`)) return;

    this.cargandoAccionMesa = true;

    this.mesaService.pagarComanda(mesa.id, comanda.id).subscribe({
      next: (respuesta) => {
        this.cargandoAccionMesa = false;
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`💰 ${tipo}: ${respuesta.message}`);
          this.totalCuentaReal = 0;
          this.cerrarModalComanda();
          this.cargarMesas();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      },
      error: (err) => {
        this.cargandoAccionMesa = false;
        console.error(`[MesasComponent] Error al cobrar (${tipo}):`, err);
        this.error.set(err.error?.message || `Error al procesar el pago en ${tipo}`);
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Ver historial de comandas de la mesa | View comanda history for the table
  verHistorial(): void {
    const mesa = this.mesaSeleccionada();
    if (!mesa) return;

    this.mesaService.obtenerComandasMesa(mesa.id).subscribe({
      next: (respuesta) => {
        this.historialComandas.set(respuesta.comandas);
        this.mostrarHistorial = true;
      },
      error: (err) => {
        console.error('[MesasComponent] Error al cargar historial:', err);
        this.error.set('Error al cargar el historial de comandas');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Cerrar modal de historial | Close history modal
  cerrarHistorial(): void {
    this.mostrarHistorial = false;
    this.historialComandas.set([]);
  }

  // Calcular subtotal de artículos | Calculate subtotal of items
  calcularSubtotal(articulos: IArticuloComanda[]): number {
    return articulos.reduce((total, art) => total + art.precio * art.cantidad, 0);
  }

  // Calcular IVA (19%) | Calculate VAT (19%)
  calcularIVA(articulos: IArticuloComanda[]): number {
    return Math.round(this.calcularSubtotal(articulos) * 0.19);
  }

  // Productos filtrados por búsqueda | Products filtered by search
  get productosFiltrados(): Pizza[] {
    const busqueda = this.busquedaProducto.toLowerCase().trim();
    if (!busqueda) return this.productos();
    return this.productos().filter(
      (p) =>
        p.nombre.toLowerCase().includes(busqueda) ||
        p.categoria?.toLowerCase().includes(busqueda)
    );
  }

  // Obtener clase CSS según estado de la mesa | Get CSS class based on table state
  claseEstadoMesa(estado: string): string {
    return estado === 'LIBRE' ? 'mesa-libre' : 'mesa-ocupada';
  }

  // Forzar liberación de mesa (solo admin) | Force table release (admin only)
  fuerzaLiberacionMesa(event: Event, mesaId: number): void {
    event.stopPropagation();
    if (!confirm('⚠️ ¿Forzar liberación de esta mesa? Se cerrarán todas las comandas activas.')) return;

    this.cargando.set(true);
    this.mesaService.limpiarMesa(mesaId).subscribe({
      next: (respuesta) => {
        this.cargando.set(false);
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`🧹 ${respuesta.resultado.mensaje}`);
          this.cargarMesas();
          setTimeout(() => this.mensajeExito.set(null), 5000);
        } else {
          this.error.set(respuesta.resultado?.mensaje || 'Error al limpiar la mesa');
          setTimeout(() => this.error.set(null), 5000);
        }
      },
      error: (err) => {
        this.cargando.set(false);
        console.error('[MesasComponent] Error al forzar liberación:', err);
        this.error.set('Error de conexión al forzar liberación. Verifica el servidor.');
        setTimeout(() => this.error.set(null), 5000);
      },
    });
  }

  // Abrir modal para crear nueva mesa | Open new table modal
  abrirModalNuevaMesa(): void {
    this.mostrarModalNuevaMesa = true;
    this.nuevaMesaNumero = null;
    this.creandoMesa = false;
  }

  // Cerrar modal de nueva mesa | Close new table modal
  cerrarModalNuevaMesa(): void {
    this.mostrarModalNuevaMesa = false;
    this.nuevaMesaNumero = null;
  }

  // Crear una nueva mesa | Create a new table
  crearMesa(): void {
    if (!this.nuevaMesaNumero || this.nuevaMesaNumero < 1) return;

    this.creandoMesa = true;
    this.mesaService.crearMesa(this.nuevaMesaNumero).subscribe({
      next: (respuesta) => {
        this.creandoMesa = false;
        if (respuesta.status === 'success') {
          this.mensajeExito.set(`✅ Mesa #${this.nuevaMesaNumero} creada exitosamente`);
          this.cerrarModalNuevaMesa();
          this.cargarMesas();
          setTimeout(() => this.mensajeExito.set(null), 3000);
        } else {
          this.error.set(respuesta.message || 'Error al crear la mesa');
          setTimeout(() => this.error.set(null), 3000);
        }
      },
      error: (err) => {
        this.creandoMesa = false;
        console.error('[MesasComponent] Error al crear mesa:', err);
        this.error.set(err.error?.message || 'Error de conexión al crear la mesa');
        setTimeout(() => this.error.set(null), 3000);
      },
    });
  }

  // Recargar datos desde el servidor | Reload data from server
  recargar(): void {
    this.cargarMesas();
    this.cargarProductos();
  }
}
