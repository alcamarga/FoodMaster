import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RecipeService, RecetaItem } from '../../../services/recipe.service';
import { PizzaService } from '../../../services/pizza.service';
import { InsumosService, Insumo } from '../../../services/insumos';
import { AuthService } from '../../../services/auth.service';
import { Pizza } from '../../../models/pizza.model';

@Component({
  selector: 'app-configuracion-recetas',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './configuracion-recetas.component.html',
  styleUrls: ['./configuracion-recetas.component.css']
})
export class ConfiguracionRecetasComponent implements OnInit {
  private recipeService = inject(RecipeService);
  private pizzaService = inject(PizzaService);
  private insumosService = inject(InsumosService);

  pizzas = signal<Pizza[]>([]);
  insumosDisponibles = signal<Insumo[]>([]);
  
  pizzaSeleccionadaId: number | null = null;
  recetaActual: RecetaItem[] = [];
  tamanos = ['Pequeña', 'Mediana', 'Familiar'];
  tamanoSeleccionado = 'Pequeña';
  
  nuevoIngrediente = {
    insumo_id: 0,
    cantidad_gastada: 0
  };

  private authService = inject(AuthService);

  ngOnInit(): void {
    this.authService.sesionActiva$.subscribe(sesion => {
      if (sesion) {
        console.log('[ConfigRecetas] Sesión detectada, cargando catálogos...');
        this.cargarPizzas();
        this.cargarInsumos();
      }
    });
  }

  cargarPizzas(): void {
    this.pizzaService.obtenerCatalogoPizzas().subscribe(res => this.pizzas.set(res));
  }

  cargarInsumos(): void {
    this.insumosService.getInsumos().subscribe(res => this.insumosDisponibles.set(res));
  }

  seleccionarPizza(id: number): void {
    this.pizzaSeleccionadaId = id;
    this.cargarReceta();
  }

  cambiarTamano(): void {
    if (this.pizzaSeleccionadaId) {
      this.cargarReceta();
    }
  }

  cargarReceta(): void {
    if (!this.pizzaSeleccionadaId) return;
    this.recipeService.obtenerReceta(this.pizzaSeleccionadaId, this.tamanoSeleccionado).subscribe(res => {
      this.recetaActual = res.receta;
    });
  }

  agregarIngrediente(): void {
    if (this.nuevoIngrediente.insumo_id === 0 || this.nuevoIngrediente.cantidad_gastada <= 0) return;
    
    const insumo = this.insumosDisponibles().find(i => i.id == this.nuevoIngrediente.insumo_id);
    
    // Evitar duplicados
    const existe = this.recetaActual.find(r => r.insumo_id == this.nuevoIngrediente.insumo_id);
    if (existe) {
      existe.cantidad_gastada = this.nuevoIngrediente.cantidad_gastada;
    } else {
      this.recetaActual.push({
        pizza_id: this.pizzaSeleccionadaId!,
        insumo_id: this.nuevoIngrediente.insumo_id,
        insumo_nombre: insumo?.nombre,
        cantidad_gastada: this.nuevoIngrediente.cantidad_gastada,
        unidad_medida: insumo?.unidad_medida
      });
    }
    
    this.nuevoIngrediente = { insumo_id: 0, cantidad_gastada: 0 };
  }

  quitarIngrediente(index: number): void {
    this.recetaActual.splice(index, 1);
  }

  guardarReceta(): void {
    if (!this.pizzaSeleccionadaId) return;
    
    this.recipeService.guardarReceta(this.pizzaSeleccionadaId, this.recetaActual, this.tamanoSeleccionado).subscribe({
      next: () => {
        alert('✅ Receta guardada con éxito');
      },
      error: (err) => {
        console.error('Error al guardar receta:', err);
        alert('❌ Error al guardar la receta');
      }
    });
  }
}
