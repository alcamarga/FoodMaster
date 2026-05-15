// Gestión de Personal — Admin Dashboard
// Autor: Camilo Martinez | Fecha: 01/05/2026

import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { UserService, PersonalPayload } from '../../../services/user.service';
import { Usuario, RolUsuario } from '../../../models/usuario.model';

@Component({
  selector: 'app-gestion-personal',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './gestion-personal.component.html',
  styleUrls: ['./gestion-personal.component.css']
})
export class GestionPersonalComponent implements OnInit {
  private userService = inject(UserService);

  // --- Estado principal ---
  // Inicializamos con un array vacío para que personal().length nunca falle
  personal = signal<Usuario[]>([]);
  cargando = signal(false);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  // --- Formulario crear/editar ---
  mostrarFormulario = false;
  editandoId: number | null = null;
  formulario: PersonalPayload = this.formularioVacio();

  // --- Modal reset password ---
  mostrarResetModal = false;
  usuarioResetId: number | null = null;
  usuarioResetNombre = '';
  nuevaContrasena = '';
  confirmarContrasena = '';

  // --- Selector de rol inline ---
  rolEditandoId: number | null = null;
  rolTemporal: RolUsuario = 'cliente';

  rolesDisponibles: RolUsuario[] = ['cocinero', 'domiciliario', 'mesero', 'admin', 'cliente'];

  ngOnInit(): void {
    this.cargarPersonal();
  }

  cargarPersonal(): void {
    this.cargando.set(true);
    this.userService.obtenerPersonal().subscribe({
      next: (res) => {
        // BLINDAJE: Verificamos si res es el array directo o viene dentro de un objeto
        const lista = Array.isArray(res) ? res : (res?.usuarios || []);
        this.personal.set(lista);
        this.cargando.set(false);
        console.log('Personal cargado:', lista.length);
      },
      error: (err) => {
        console.error('Error cargando personal:', err);
        this.mostrarError('No se pudo cargar el personal');
        this.personal.set([]); // Ante error, vaciamos para evitar undefined
        this.cargando.set(false);
      }
    });
  }

  // --- Crear / Editar ---

  abrirModalNuevo(): void {
    this.editandoId = null;
    this.formulario = this.formularioVacio();
    this.mostrarFormulario = true;
  }

  prepararEdicion(usuario: Usuario): void {
    this.editandoId = usuario.id;
    this.formulario = {
      nombre: usuario.nombre,
      email: usuario.email,
      rol: usuario.rol,
      password: ''
    };
    this.mostrarFormulario = true;
  }

  guardarPersonal(): void {
    if (!this.formulario.nombre.trim() || !this.formulario.email.trim()) {
      this.mostrarError('Nombre y email son obligatorios');
      return;
    }

    if (this.editandoId) {
      const payload: PersonalPayload = { ...this.formulario };
      if (!payload.password) delete payload.password;

      this.userService.actualizarPersonal(this.editandoId, payload).subscribe({
        next: () => {
          this.mostrarExito('✅ Empleado actualizado correctamente');
          this.cerrarFormulario();
          this.cargarPersonal();
        },
        error: (err) => this.mostrarError('❌ ' + (err.error?.error || 'No se pudo actualizar'))
      });
    } else {
      if (!this.formulario.password || this.formulario.password.length < 6) {
        this.mostrarError('La contraseña debe tener al menos 6 caracteres');
        return;
      }
      this.userService.crearPersonal(this.formulario).subscribe({
        next: () => {
          this.mostrarExito('✅ Empleado registrado correctamente');
          this.cerrarFormulario();
          this.cargarPersonal();
        },
        error: (err) => this.mostrarError('❌ ' + (err.error?.error || 'No se pudo registrar'))
      });
    }
  }

  cerrarFormulario(): void {
    this.mostrarFormulario = false;
    this.editandoId = null;
    this.formulario = this.formularioVacio();
  }

  // --- Cambio de rol inline ---

  activarSelectorRol(usuario: Usuario): void {
    this.rolEditandoId = usuario.id;
    this.rolTemporal = usuario.rol;
  }

  confirmarCambioRol(usuario: Usuario): void {
    if (this.rolTemporal === usuario.rol) {
      this.rolEditandoId = null;
      return;
    }
    this.userService.cambiarRol(usuario.id, this.rolTemporal).subscribe({
      next: (res) => {
        this.mostrarExito(`✅ ${res.mensaje}`);
        this.rolEditandoId = null;
        this.cargarPersonal();
      },
      error: (err) => {
        this.mostrarError('❌ ' + (err.error?.error || 'No se pudo cambiar el rol'));
        this.rolEditandoId = null;
      }
    });
  }

  cancelarCambioRol(): void {
    this.rolEditandoId = null;
  }

  // --- Eliminar ---

  eliminarUsuario(usuario: Usuario): void {
    if (!confirm(`¿Eliminar a ${usuario.nombre}? Esta acción no se puede deshacer.`)) return;
    this.userService.eliminarPersonal(usuario.id).subscribe({
      next: () => {
        this.mostrarExito(`🗑️ ${usuario.nombre} eliminado`);
        this.cargarPersonal();
      },
      error: (err) => this.mostrarError('❌ ' + (err.error?.error || 'No se pudo eliminar'))
    });
  }

  // --- Reset Password ---

  abrirResetModal(usuario: Usuario): void {
    this.usuarioResetId = usuario.id;
    this.usuarioResetNombre = usuario.nombre;
    this.nuevaContrasena = '';
    this.confirmarContrasena = '';
    this.mostrarResetModal = true;
  }

  cerrarResetModal(): void {
    this.mostrarResetModal = false;
    this.usuarioResetId = null;
    this.nuevaContrasena = '';
    this.confirmarContrasena = '';
  }

  confirmarReset(): void {
    if (this.nuevaContrasena.length < 6) {
      this.mostrarError('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    if (this.nuevaContrasena !== this.confirmarContrasena) {
      this.mostrarError('Las contraseñas no coinciden');
      return;
    }
    this.userService.resetPassword(this.usuarioResetId!, this.nuevaContrasena).subscribe({
      next: (res) => {
        this.mostrarExito(`🔑 ${res.mensaje}`);
        this.cerrarResetModal();
      },
      error: (err) => this.mostrarError('❌ ' + (err.error?.error || 'No se pudo resetear la contraseña'))
    });
  }

  // --- Helpers ---

  private formularioVacio(): PersonalPayload {
    return { nombre: '', email: '', rol: 'cocinero', password: '' };
  }

  private mostrarExito(msg: string): void {
    this.mensajeExito.set(msg);
    this.mensajeError.set(null);
    setTimeout(() => this.mensajeExito.set(null), 4000);
  }

  private mostrarError(msg: string): void {
    this.mensajeError.set(msg);
    this.mensajeExito.set(null);
    setTimeout(() => this.mensajeError.set(null), 5000);
  }

  badgeRol(rol: string): string {
    const mapa: Record<string, string> = {
      admin: 'bg-danger',
      cocinero: 'bg-info text-dark',
      domiciliario: 'bg-warning text-dark',
      mesero: 'bg-primary',
      cliente: 'bg-secondary'
    };
    return mapa[rol] ?? 'bg-secondary';
  }
}