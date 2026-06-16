import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegistroComponent } from './components/registro/registro.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { MenuComponent } from './components/menu/menu.component';
import { AdminDashboardComponent } from './components/admin-dashboard/admin-dashboard.component';
import { ResumenPedidoComponent } from './components/resumen-pedido/resumen-pedido.component';
import { MisPedidosComponent } from './components/mis-pedidos/mis-pedidos.component';
import { GestionPedidosComponent } from './components/admin-dashboard/gestion-pedidos/gestion-pedidos.component';
import { MesasComponent } from './components/mesas/mesas.component';
import { CocinaComponent } from './components/cocina/cocina.component';
import { RoleGuard } from './guards/role.guard';

export const routes: Routes = [
  // 1. Entrada principal (Pública) | Main entry (Public)
  { path: '', component: MenuComponent, pathMatch: 'full' },

  // 2. Rutas públicas | Public routes
  { path: 'menu', component: MenuComponent },
  { path: 'login', component: LoginComponent },
  { path: 'registro', component: RegistroComponent },

  // 3. Dashboard de administración (solo admin) | Admin dashboard (admin only)
  {
    path: 'admin/dashboard',
    component: AdminDashboardComponent,
    canActivate: [RoleGuard],
    data: { roles: ['admin'] },
  },

  // 4. Panel de cocina (solo cocinero) | Kitchen panel (cook only)
  {
    path: 'cocina',
    component: CocinaComponent,
    canActivate: [RoleGuard],
    data: { roles: ['cocinero', 'admin'] },
  },

  // 5. Gestión de mesas (mesero o admin) | Table management (waiter or admin)
  {
    path: 'admin/mesas',
    component: MesasComponent,
    canActivate: [RoleGuard],
    data: { roles: ['mesero', 'admin'] },
  },

  // 6. Gestión de pedidos (admin, cocinero) | Order management
  {
    path: 'admin/pedidos',
    component: GestionPedidosComponent,
    canActivate: [RoleGuard],
    data: { roles: ['admin', 'cocinero'] },
  },

  // 7. Dashboard de usuario (requiere login) | User dashboard (requires login)
  { path: 'dashboard', component: DashboardComponent, canActivate: [RoleGuard], data: { roles: [] } },
  { path: 'resumen', component: ResumenPedidoComponent, canActivate: [RoleGuard], data: { roles: [] } },
  { path: 'mis-pedidos', component: MisPedidosComponent, canActivate: [RoleGuard], data: { roles: [] } },

  // 8. Comodín | Fallback
  { path: '**', redirectTo: '' },
];
