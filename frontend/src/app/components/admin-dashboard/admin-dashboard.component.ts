import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth.service';
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
import { MesasComponent } from '../mesas/mesas.component';
import { FinanzasComponent } from '../finanzas/finanzas.component';

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
    RentabilidadComponent,
    MesasComponent,
    FinanzasComponent
  ],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {
  pestanaActiva: string = 'pedidos';
  usuario: Usuario | null = null;

  constructor(
    private auth: AuthService,
  ) {
    this.usuario = this.auth.obtenerUsuarioActual();
    if (this.usuario?.rol === 'cocinero') {
      this.pestanaActiva = 'pedidos';
    }
  }

  ngOnInit() {
    // No se cargan KPIs redundantes — los reportes están en la pestaña Cierre y Finanzas
    // No redundant KPIs loaded — reports are in the Cierre y Finanzas tab
  }

  cambiarPestana(nombrePestana: string) {
    this.pestanaActiva = nombrePestana;
  }
}