// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 15 de junio de 2026
// **Estado:** Desarrollo

// Guard de rutas basado en roles | Role-based route guard

import { Injectable, inject } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({ providedIn: 'root' })
export class RoleGuard implements CanActivate {
  private auth = inject(AuthService);
  private router = inject(Router);

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const sesion = this.auth.obtenerUsuarioActual();
    const token = this.auth.obtenerTokenAcceso();

    if (!sesion || !token) {
      // Español: no autenticado → redirigir al login | English: not authenticated → redirect to login
      this.router.navigate(['/login']);
      return false;
    }

    // Español: roles permitidos definidos en la ruta | English: allowed roles defined in the route
    const rolesPermitidos: string[] | undefined = route.data?.['roles'];
    if (!rolesPermitidos || rolesPermitidos.length === 0) {
      return true; // Sin restricción de rol, solo autenticación
    }

    if (rolesPermitidos.includes(sesion.rol)) {
      return true;
    }

    // Español: rol no autorizado → redirigir según su rol | English: unauthorized role → redirect based on role
    this.redirigirPorRol(sesion.rol);
    return false;
  }

  // Español: redirigir al usuario a su vista principal según su rol | English: redirect user to their main view based on role
  private redirigirPorRol(rol: string): void {
    const rutas: Record<string, string> = {
      admin: '/admin/dashboard',
      cocinero: '/cocina',
      mesero: '/admin/mesas',
      domiciliario: '/mis-pedidos',
      cliente: '/menu',
    };
    this.router.navigate([rutas[rol] || '/menu']);
  }
}
