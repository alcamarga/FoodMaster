// Componente de inicio de sesión con formularios reactivos.
// Autor: Camilo Martinez
// Fecha: 15/04/2026
// Estética: Crema/Dorado con transparencia y bordes redondeados

import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { LoginCargaUtil, RespuestaAutenticacion } from '../../models/usuario.model';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  private fb = inject(FormBuilder);
  private auth = inject(AuthService);
  private router = inject(Router);

  // Formulario reactivo con validaciones | Reactive form with validations
  formulario: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    contrasena: ['', [Validators.required, Validators.minLength(6)]]
  });

  redirectUrl: string | null = null;

  ngOnInit(): void {
    // Español: leer redirect de queryParams (ej: /resumen) | English: read redirect from queryParams (e.g. /resumen)
    this.router.routerState.root.queryParams.subscribe(params => {
      this.redirectUrl = params['redirect'] || null;
      if (this.redirectUrl) {
        console.log('[Login] Redirigirá a', this.redirectUrl, 'tras login exitoso');
      }
    });
    console.log('[Login] Limpieza de sesión previa (sin tocar el carrito)');
    // Español: limpiar solo datos de sesión, conservar carrito | English: clear only session data, preserve cart
    const carritoGuardado = localStorage.getItem('carrito');
    this.auth.limpiarSesion();
    if (carritoGuardado) {
      localStorage.setItem('carrito', carritoGuardado);
    }
  }

  enviando = false;
  errorMensaje: string | null = null;

  // Accesos rápidos a los controles para el template | Quick access to controls for template
  get email() { return this.formulario.get('email')!; }
  get contrasena() { return this.formulario.get('contrasena')!; }

  // Envía las credenciales al AuthService y redirige según intención de compra
  // Sends credentials to AuthService and redirects based on purchase intention
  iniciarSesion(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    this.enviando = true;
    this.errorMensaje = null;
    
    // Limpiar sesión previa para evitar datos corruptos
    this.auth.limpiarSesion();

    const payload: LoginCargaUtil = this.formulario.value as LoginCargaUtil;

    this.auth.iniciarSesion(payload).subscribe({
      next: (respuesta) => {
        // Redirigir según el rol usando la respuesta directa del servidor
        const usuario = respuesta.usuario;
        console.log('[LoginComponent] Login exitoso. Usuario:', usuario.nombre, 'Rol:', usuario.rol);
        
        if (usuario.rol === 'admin' || usuario.rol === 'cocinero' || usuario.email === 'admin@foodmaster.com') {
          console.log('[LoginComponent] Login exitoso. Refrescando aplicación hacia el Dashboard...');
          window.location.href = '/admin/dashboard';
        } else {
          // Español: redirigir a la URL guardada (si existe) o al menú | English: redirect to saved URL (if exists) or to menu
          if (this.redirectUrl) {
            console.log('[Login] Redirigiendo a:', this.redirectUrl);
            this.router.navigateByUrl(this.redirectUrl);
          } else {
            this.router.navigate(['/menu']);
          }
        }
      },
      error: (err: { status: number }) => {
        this.enviando = false;
        this.errorMensaje = err.status === 401
          ? 'Credenciales incorrectas. Verifica tu email y contraseña.'
          : 'Error de conexión. Intenta de nuevo más tarde.';
      }
    });
  }
}
