// **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
// **Fecha:** 17 de junio de 2026
// **Tarea #5:** Configuración y Personalización del Negocio

// Componente standalone para gestionar la configuración global del negocio
// Standalone component for managing global business configuration

import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ConfiguracionService, Configuracion } from '../../../services/configuracion.service';

@Component({
  selector: 'app-configuracion',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracion.component.html',
  styleUrls: ['./configuracion.component.css'],
})
export class ConfiguracionComponent implements OnInit {
  private configService = inject(ConfiguracionService);

  config = signal<Configuracion | null>(null);
  cargando = signal(true);
  guardando = signal(false);
  error = signal<string | null>(null);
  mensajeExito = signal<string | null>(null);

  ngOnInit(): void {
    this.cargarConfiguracion();
  }

  cargarConfiguracion(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.configService.obtener().subscribe({
      next: (resp) => {
        if (resp.status === 'success') {
          this.config.set(resp.configuracion);
        }
        this.cargando.set(false);
      },
      error: (err) => {
        console.error('[Configuracion] Error al cargar:', err);
        this.error.set('Error al cargar la configuración');
        this.cargando.set(false);
      },
    });
  }

  guardar(): void {
    const datos = this.config();
    if (!datos) return;

    // Validaciones
    if (!datos.nombre_negocio?.trim()) {
      this.error.set('El nombre del negocio es obligatorio');
      setTimeout(() => this.error.set(null), 3000);
      return;
    }
    if (datos.porcentaje_iva < 0 || datos.porcentaje_iva > 100) {
      this.error.set('El IVA debe estar entre 0 y 100');
      setTimeout(() => this.error.set(null), 3000);
      return;
    }

    this.guardando.set(true);
    this.error.set(null);
    this.mensajeExito.set(null);

    this.configService.actualizar(datos).subscribe({
      next: (resp) => {
        this.guardando.set(false);
        if (resp.status === 'success') {
          this.config.set(resp.configuracion);
          this.mensajeExito.set('✅ Configuración guardada correctamente');
          setTimeout(() => this.mensajeExito.set(null), 4000);
        }
      },
      error: (err) => {
        this.guardando.set(false);
        console.error('[Configuracion] Error al guardar:', err);
        this.error.set(err.error?.message || 'Error al guardar la configuración');
        setTimeout(() => this.error.set(null), 5000);
      },
    });
  }

  cancelar(): void {
    this.cargarConfiguracion();
  }
}
