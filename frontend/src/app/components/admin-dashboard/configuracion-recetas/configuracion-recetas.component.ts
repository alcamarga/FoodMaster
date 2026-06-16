import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RecipeService, RecetaItem } from '../../../services/recipe.service';
import { PizzaService } from '../../../services/pizza.service';
import { InsumosService, Insumo } from '../../../services/insumos';
import { AuthService } from '../../../services/auth.service';
import { GrupoProductoService } from '../../../services/grupo_producto.service';
import { Pizza } from '../../../models/pizza.model';
import { IGrupoProducto } from '../../../models/grupo_producto.model';

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
  private authService = inject(AuthService);
  private grupoProductoService = inject(GrupoProductoService);

  // Estados
  pizzas = signal<Pizza[]>([]);
  insumosDisponibles = signal<Insumo[]>([]);
  grupos = signal<IGrupoProducto[]>([]);
  cargando = signal(false);
  
  pizzaSeleccionadaId: number | null = null;
  recetaActual: RecetaItem[] = [];
  tamanos: string[] = []; // Se llena dinámicamente
  tamanoSeleccionado = '';
  
  nuevoIngrediente = {
    insumo_id: 0,
    cantidad_gastada: 0
  };

  ngOnInit(): void {
    // Escuchamos la sesión para cargar los datos iniciales
    this.authService.sesionActiva$.subscribe(sesion => {
      if (sesion) {
        this.cargarCatalogos();
      }
    });
  }

  cargarCatalogos(): void {
    this.pizzaService.obtenerCatalogoPizzas().subscribe(res => this.pizzas.set(res));
    this.insumosService.getInsumos().subscribe(res => this.insumosDisponibles.set(res));
    this.grupoProductoService.obtenerGrupos().subscribe(res => this.grupos.set(res));
  }

  seleccionarPizza(id: number): void {
    const pizza = this.pizzas().find(p => p.id === id);
    if (!pizza) return;

    this.pizzaSeleccionadaId = id;
    
    // Generamos los tamaños dinámicamente según la categoría y precios definidos
    const cat = pizza.categoria || 'Pizza';
    const etiquetasPosibles = this.obtenerEtiquetasPorGrupo(cat);
    
    this.tamanos = [];
    if (pizza.precio_1 && pizza.precio_1 > 0 && etiquetasPosibles[0]) this.tamanos.push(etiquetasPosibles[0]);
    if (pizza.precio_2 && pizza.precio_2 > 0 && etiquetasPosibles[1]) this.tamanos.push(etiquetasPosibles[1]);
    if (pizza.precio_3 && pizza.precio_3 > 0 && etiquetasPosibles[2]) this.tamanos.push(etiquetasPosibles[2]);

    // Si no hay precios definidos, al menos uno
    if (this.tamanos.length === 0) this.tamanos = [etiquetasPosibles[0] || 'Único'];

    this.tamanoSeleccionado = this.tamanos[0];
    this.cargarReceta();
  }

  private obtenerEtiquetasPorGrupo(nombreGrupo: string): string[] {
    const grupo = this.grupos().find((g) => g.nombre === nombreGrupo);
    if (grupo) {
      const etiquetas = [grupo.etiqueta_1];
      if (grupo.etiqueta_2) etiquetas.push(grupo.etiqueta_2);
      if (grupo.etiqueta_3) etiquetas.push(grupo.etiqueta_3);
      return etiquetas;
    }
    return ['Único'];
  }

  cambiarTamano(): void {
    if (this.pizzaSeleccionadaId) {
      this.cargarReceta();
    }
  }

  cargarReceta(): void {
    if (!this.pizzaSeleccionadaId) return;
    this.cargando.set(true);
    this.recipeService.obtenerReceta(this.pizzaSeleccionadaId, this.tamanoSeleccionado).subscribe({
      next: (res) => {
        // Si el backend devuelve la receta en res.receta o directo en res
        this.recetaActual = res.receta || res || [];
        this.cargando.set(false);
      },
      error: () => {
        this.recetaActual = [];
        this.cargando.set(false);
      }
    });
  }

  // --- Lógica de la Tabla de Ingredientes ---

  agregarIngrediente(): void {
    // Validaciones básicas
    if (this.nuevoIngrediente.insumo_id === 0) {
        alert("Por favor selecciona un insumo");
        return;
    }
    if (this.nuevoIngrediente.cantidad_gastada <= 0) {
        alert("La cantidad debe ser mayor a 0");
        return;
    }

    const listaInsumos = this.insumosDisponibles();
    
    // Seguridad: verificamos que la lista no esté vacía
    if (!listaInsumos || listaInsumos.length === 0) return;

    const insumoInfo = listaInsumos.find(i => i.id == this.nuevoIngrediente.insumo_id);
    
    if (!insumoInfo) {
        alert("Error: No se encontró la información del insumo");
        return;
    }

    // Buscamos si ya existe para actualizarlo o agregarlo
    const indexExistente = this.recetaActual.findIndex(r => r.insumo_id == this.nuevoIngrediente.insumo_id);

    if (indexExistente !== -1) {
      // Si ya existe, sumamos la cantidad
      this.recetaActual[indexExistente].cantidad_gastada = this.nuevoIngrediente.cantidad_gastada;
    } else {
      // Si no existe, lo agregamos a la lista local
      this.recetaActual.push({
        pizza_id: this.pizzaSeleccionadaId!,
        insumo_id: Number(this.nuevoIngrediente.insumo_id),
        insumo_nombre: insumoInfo.nombre,
        cantidad_gastada: this.nuevoIngrediente.cantidad_gastada,
        unidad_medida: insumoInfo.unidad_medida || 'gr'
      });
    }
    
    // Limpiamos el formulario pequeño
    this.nuevoIngrediente = { insumo_id: 0, cantidad_gastada: 0 };
  }

  quitarIngrediente(index: number): void {
    this.recetaActual.splice(index, 1);
  }

  guardarReceta(): void {
    if (!this.pizzaSeleccionadaId) {
        alert('Selecciona una pizza primero');
        return;
    }
    
    if (this.recetaActual.length === 0) {
        if (!confirm('La receta está vacía. ¿Deseas guardar una receta sin ingredientes?')) return;
    }

    this.cargando.set(true);
    this.recipeService.guardarReceta(
        this.pizzaSeleccionadaId, 
        this.recetaActual, 
        this.tamanoSeleccionado
    ).subscribe({
      next: () => {
        this.cargando.set(false);
        alert('✅ ¡Receta de ' + this.tamanoSeleccionado + ' guardada con éxito!');
      },
      error: (err) => {
        this.cargando.set(false);
        console.error('Error:', err);
        alert('❌ Error al guardar: ' + (err.error?.error || 'Problema de conexión'));
      }
    });
  }
}