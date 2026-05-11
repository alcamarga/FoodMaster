// Módulo de Rentabilidad — Admin Dashboard
// Autor: Camilo Martinez | Fecha: 01/05/2026

import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  RentabilidadService,
  RentabilidadItem,
  ResumenRentabilidad
} from '../../../services/rentabilidad.service';

@Component({
  selector: 'app-rentabilidad',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rentabilidad.component.html',
  styleUrls: ['./rentabilidad.component.css']
})
export class RentabilidadComponent implements OnInit {
  private rentabilidadService = inject(RentabilidadService);

  productos = signal<RentabilidadItem[]>([]);
  resumen = signal<ResumenRentabilidad | null>(null);
  cargando = signal(true);
  error = signal<string | null>(null);
  
  tamanos = ['Pequeña', 'Mediana', 'Familiar'];
  tamanoSeleccionado = 'Pequeña';

  // Computed: productos ordenados por margen descendente (ya vienen ordenados del backend)
  productosFiltrados = computed(() => this.productos());

  ngOnInit(): void {
    this.cargar();
  }

  cambiarTamano(): void {
    this.cargar();
  }

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.rentabilidadService.obtenerRentabilidad(this.tamanoSeleccionado).subscribe({
      next: (res) => {
        this.productos.set(res.productos);
        this.resumen.set(res.resumen);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set('No se pudo cargar el análisis de rentabilidad.');
        console.error('[Rentabilidad]', err);
        this.cargando.set(false);
      }
    });
  }

  /** Clase CSS según el margen de ganancia */
  claseMargen(margen: number): string {
    if (margen >= 50) return 'margen-alto';
    if (margen >= 30) return 'margen-medio';
    return 'margen-bajo';
  }

  /** Clase de badge para la barra de progreso */
  claseBarra(margen: number): string {
    if (margen >= 50) return 'bg-success';
    if (margen >= 30) return 'bg-warning';
    return 'bg-danger';
  }

  /** Ancho de la barra de progreso (máx 100%) */
  anchoBarra(margen: number): string {
    return Math.min(Math.max(margen, 0), 100) + '%';
  }
}
