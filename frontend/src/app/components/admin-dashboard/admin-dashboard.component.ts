import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
import { PizzaService } from '../../services/pizza.service';
import { Usuario } from '../../models/usuario.model';

// Importa los componentes hijos para que el HTML los reconozca (Errores NG8001)
// Subimos un nivel a 'components' y entramos a las carpetas correspondientes
import { DashboardComponent } from '../dashboard/dashboard.component';
import { InventarioComponent } from './inventario/inventario';

// Los demás están dentro de la subcarpeta de admin-dashboard (según tu explorador)
import { GestionPedidosComponent } from './gestion-pedidos/gestion-pedidos.component';
import { ConfiguracionRecetasComponent } from './configuracion-recetas/configuracion-recetas.component';
import { GestionPersonalComponent } from './gestion-personal/gestion-personal.component';
import { RentabilidadComponent } from './rentabilidad/rentabilidad.component';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  // Añadimos todos los componentes aquí para que dejen de salir en rojo
  imports: [
    CommonModule,
    DashboardComponent,
    InventarioComponent,
    GestionPedidosComponent,
    ConfiguracionRecetasComponent,
    GestionPersonalComponent,
    RentabilidadComponent
  ],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  ventasDelDia: number = 0;
  pedidosPendientes: number = 0;
  inventarioPizzas: number = 0;
  pedidosRecientes: any[] = [];

  // Usamos 'pestanaActiva' sin la ñ si tu HTML lo tiene así, 
  // o 'pestañaActiva' según lo que diga el error TS2551. 
  // Viendo tu error, el HTML busca 'pestanaActiva'.
  pestanaActiva: string = 'pedidos';
  usuario: Usuario | null = null;
  
  // Variables para Modal de Detalle
  pedidoDetalle: any = null;
  mostrarDetalle = false;

  constructor(
    private auth: AuthService,
    private pizzaService: PizzaService
  ) {
    this.usuario = this.auth.obtenerUsuarioActual();
    if (this.usuario?.rol === 'cocinero') {
      this.pestanaActiva = 'pedidos';
    }
  }

  ngOnInit() {
    this.cargarPedidosDesdeDB();
  }

  // Esta es la función que te faltaba (Error TS2339)
  cambiarPestana(nombrePestana: string) {
    this.pestanaActiva = nombrePestana;
  }

  cargarPedidosDesdeDB() {
    this.pizzaService.obtenerTodosLosPedidos().subscribe({
      next: (pedidos: any[]) => {
        this.pedidosRecientes = pedidos || [];
        this.pedidosPendientes = pedidos ? pedidos.length : 0;
        this.ventasDelDia = 12450;
        this.inventarioPizzas = 150;
      },
      error: (err) => {
        console.error('Error conectando con el backend de PizzaOS:', err);
      }
    });
  }

  // --- MÉTODOS PARA EL MODAL DE DETALLE ---
  verDetalle(pedido: any): void {
    this.pedidoDetalle = pedido;
    this.mostrarDetalle = true;
  }

  cerrarDetalle(): void {
    this.mostrarDetalle = false;
    this.pedidoDetalle = null;
  }

  subtotalPedido(pedido: any): number {
    return Math.round((pedido.total ?? 0) / 1.19);
  }

  ivaPedido(pedido: any): number {
    return Math.round((pedido.total ?? 0) - this.subtotalPedido(pedido));
  }
}