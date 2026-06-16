import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

import { AuthService } from '../../services/auth.service';
import { PizzaService } from '../../services/pizza.service';
import { GrupoProductoService } from '../../services/grupo_producto.service';
import { Pizza } from '../../models/pizza.model';
import { IGrupoProducto } from '../../models/grupo_producto.model';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  // Inyecciones públicas para que el HTML pueda acceder a ellas sin errores TS2341
  public readonly auth = inject(AuthService);
  public readonly router = inject(Router);
  private readonly pizzaService = inject(PizzaService);
  private readonly grupoProductoService = inject(GrupoProductoService);

  // Variables de estado
  listaPizzas = signal<Pizza[]>([]);
  grupos = signal<IGrupoProducto[]>([]);
  
  cargandoInventario = true;
  cargandoCategorias = signal(true);
  errorInventario: string | null = null;

  ngOnInit(): void {
    // 1. Verificación de seguridad inmediata
    if (!this.auth.estaAutenticado()) {
      this.router.navigate(['/login']);
      return;
    }

    // 2. Cargar catálogos
    this.cargarInventario();
    this.cargarGrupos();
  }

  // Carga el catálogo de pizzas (Inventario)
  private cargarInventario(): void {
    this.cargandoInventario = true;
    this.pizzaService.obtenerCatalogoPizzas().subscribe({
      next: (pizzas: Pizza[]) => {
        this.listaPizzas.set(pizzas);
        this.cargandoInventario = false;
      },
      error: (err) => {
        if (err.status === 401 || err.status === 403) {
          console.error('[AUTH ERROR] Sesión inválida al cargar inventario:', err);
        } else {
          console.error('Error al cargar inventario:', err);
        }
        this.errorInventario = 'Error al cargar el inventario. Inténtalo de nuevo.';
        this.cargandoInventario = false;
      }
    });
  }

  // Función para volver al menú público
  volverAlMenu(): void {
    this.router.navigate(['/menu']);
  }

  // Inyección para subida de imágenes | Injection for image upload
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  // --- FORMULARIO NUEVA PIZZA ---
  mostrarFormulario = false;
  nuevaPizza: any = { nombre: '', descripcion: '', categoria: '', tags: [], imagen_url: '', precio_1: 0, precio_2: 0, precio_3: 0 };
  nuevoTag = '';
  // Precios adicionales para grupos que permiten tamaños personalizados | Extra prices for groups that allow custom sizes
  preciosPersonalizados: { label: string; precio: number }[] = [];
  // Estado de subida de imagen | Image upload state
  imagenPreview: string | ArrayBuffer | null = null;
  subiendoImagen = false;


  toggleFormulario(): void {
    this.mostrarFormulario = !this.mostrarFormulario;
  }

  // Agregar una etiqueta tags al formulario | Add a tag to the form
  agregarTag(): void {
    const tag = this.nuevoTag.trim().toLowerCase();
    if (tag && !this.nuevaPizza.tags.includes(tag)) {
      this.nuevaPizza.tags = [...this.nuevaPizza.tags, tag];
      this.nuevoTag = '';
    }
  }

  // Eliminar una etiqueta tags | Remove a tag
  eliminarTag(tag: string): void {
    this.nuevaPizza.tags = this.nuevaPizza.tags.filter((t: string) => t !== tag);
  }

  // Agregar un campo de precio personalizado | Add a custom price field
  agregarPrecioPersonalizado(): void {
    this.preciosPersonalizados.push({ label: '', precio: 0 });
  }

  // Eliminar un campo de precio personalizado | Remove a custom price field
  eliminarPrecioPersonalizado(index: number): void {
    this.preciosPersonalizados.splice(index, 1);
  }

  // Español: limpiar precios personalizados al cambiar de grupo | English: clear custom prices when switching groups
  cambiarGrupo(): void {
    this.preciosPersonalizados = [];
  }

  // Español: seleccionar imagen y mostrar preview | English: select image and show preview
  onImagenSeleccionada(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) return;

    const archivo = input.files[0];
    const tiposPermitidos = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!tiposPermitidos.includes(archivo.type)) {
      alert('Tipo de archivo no permitido. Usa PNG, JPG, GIF o WebP.');
      return;
    }

    // Español: mostrar preview local | English: show local preview
    const lector = new FileReader();
    lector.onload = () => {
      this.imagenPreview = lector.result;
    };
    lector.readAsDataURL(archivo);

    // Español: subir al servidor | English: upload to server
    this.subiendoImagen = true;
    const formData = new FormData();
    formData.append('file', archivo);

    this.http.post<{ status: string; url: string }>(`${this.apiUrl}/upload`, formData).subscribe({
      next: (respuesta) => {
        if (respuesta.status === 'success') {
          this.nuevaPizza.imagen_url = respuesta.url;
        }
        this.subiendoImagen = false;
      },
      error: (err) => {
        console.error('[Dashboard] Error al subir imagen:', err);
        this.subiendoImagen = false;
        alert('Error al subir la imagen. Intenta de nuevo.');
      },
    });
  }

  guardarPizza(): void {
    if(!this.nuevaPizza.nombre) {
      alert('El nombre del producto es obligatorio');
      return;
    }

    // Español: enviar solo los campos de precio visibles (no enviar 0 si el campo está oculto) | English: send only visible price fields (don't send 0 if field is hidden)
    const payload = {
      ...this.nuevaPizza,
    };

    // Limpiar precios no visibles | Clean up non-visible prices
    if (!this.mostrarCampoPrecio(1)) payload.precio_1 = undefined;
    if (!this.mostrarCampoPrecio(2)) payload.precio_2 = undefined;
    if (!this.mostrarCampoPrecio(3)) payload.precio_3 = undefined;

    // Español: incluir precios personalizados si el grupo lo permite | English: include custom prices if the group allows
    if (this.puedeTenerPreciosPersonalizados() && this.preciosPersonalizados.length > 0) {
      // Usar el siguiente slot disponible | Use the next available slot
      const disponibles = [1, 2, 3].filter(i => !payload[`precio_${i}`] || payload[`precio_${i}`] === 0);
      for (let i = 0; i < this.preciosPersonalizados.length && i < disponibles.length; i++) {
        payload[`precio_${disponibles[i]}`] = this.preciosPersonalizados[i].precio;
      }
    }

    this.pizzaService.crearPizza(payload).subscribe({
      next: (res) => {
        this.cargarInventario();
        this.cancelarFormulario();
      },
      error: (err) => {
        console.error('Error al guardar producto', err);
        alert('Error al guardar el producto.');
      }
    });
  }

  cancelarFormulario(): void {
    const grupos = this.grupos();
    const fallback = grupos.length > 0 ? grupos[0].nombre : 'General';
    this.nuevaPizza = { nombre: '', descripcion: '', categoria: fallback, tags: [], imagen_url: '', precio_1: 0, precio_2: 0, precio_3: 0 };
    this.preciosPersonalizados = [];
    this.imagenPreview = null;
    this.mostrarFormulario = false;
  }

  // Eliminar pizza físicamente | Delete pizza physically
  eliminarPizza(id: number): void {
    if (confirm('¿Realmente deseas eliminar esta pizza de la base de datos?')) {
      this.pizzaService.eliminarPizza(id).subscribe({
        next: () => {
          // Refresco automático usando el Signal | Auto-refresh using Signal
          this.listaPizzas.update(actuales => actuales.filter(p => p.id !== id));
        },
        error: (err) => {
          console.error('Error al eliminar pizza:', err);
          alert('Hubo un error al eliminar la pizza.');
        }
      });
    }
  }

  // Cargar grupos dinámicos desde el backend | Load dynamic groups from backend
  cargarGrupos(): void {
    this.cargandoCategorias.set(true);
    this.grupoProductoService.obtenerGrupos().subscribe({
      next: (grupos) => {
        this.grupos.set(grupos);
        this.cargandoCategorias.set(false);
        if (!this.nuevaPizza.categoria && grupos.length > 0) {
          this.nuevaPizza.categoria = grupos[0].nombre;
        }
      },
      error: (err) => {
        console.error('[Dashboard] Error al cargar grupos:', err);
        this.cargandoCategorias.set(false);
      },
    });
  }

  // Español: reglas de visualización por grupo (anulan etiquetas de BD) | English: display rules per group (override DB labels)
  private readonly REGLAS_VISUALIZACION: Record<string, { campos: number; etiquetas: string[]; permitirPersonalizados: boolean }> = {
    'Entradas':  { campos: 1, etiquetas: ['Precio Único'],              permitirPersonalizados: true },
    'Bebidas':   { campos: 1, etiquetas: ['Precio Único'],              permitirPersonalizados: true },
    'Otros':     { campos: 1, etiquetas: ['Precio Único'],              permitirPersonalizados: true },
    'Platos Fuertes': { campos: 1, etiquetas: ['Individual'],           permitirPersonalizados: true },
    'Postres':   { campos: 1, etiquetas: ['Individual'],                permitirPersonalizados: true },
    'Licores':   { campos: 2, etiquetas: ['Individual', 'Botella'],     permitirPersonalizados: true },
    'Lasaña':    { campos: 2, etiquetas: ['Pequeña', 'Grande'],         permitirPersonalizados: false },
  };

  // Obtener regla de visualización para el grupo actual | Get display rule for current group
  private obtenerReglaVisualizacion(): { campos: number; etiquetas: string[]; permitirPersonalizados: boolean } | null {
    const nombreGrupo = this.nuevaPizza.categoria;
    if (!nombreGrupo) return null;
    const regla = this.REGLAS_VISUALIZACION[nombreGrupo];
    if (regla) return regla;

    // Si no hay regla específica, usar las etiquetas de la BD | If no specific rule, use DB labels
    const grupo = this.grupos().find((g) => g.nombre === nombreGrupo);
    if (!grupo) return null;
    const etiquetas = [grupo.etiqueta_1];
    if (grupo.etiqueta_2) etiquetas.push(grupo.etiqueta_2);
    if (grupo.etiqueta_3) etiquetas.push(grupo.etiqueta_3);
    return {
      campos: etiquetas.length,
      etiquetas,
      permitirPersonalizados: etiquetas.length <= 2,
    };
  }

  // Obtener etiquetas de precio desde reglas o datos dinámicos | Get price labels from rules or dynamic data
  getEtiquetaPrecio(index: number): string {
    const regla = this.obtenerReglaVisualizacion();
    if (regla) {
      return regla.etiquetas[index - 1] || '';
    }
    return '';
  }

  // Mostrar campo de precio según reglas o etiquetas del grupo | Show price field based on rules or group labels
  mostrarCampoPrecio(index: number): boolean {
    const regla = this.obtenerReglaVisualizacion();
    if (regla) {
      return index <= regla.campos;
    }
    return index === 1;
  }

  // Verificar si el grupo permite añadir tamaños personalizados con botón + | Check if group allows adding custom sizes
  puedeTenerPreciosPersonalizados(): boolean {
    const regla = this.obtenerReglaVisualizacion();
    if (regla) {
      return regla.permitirPersonalizados;
    }
    return false;
  }



  // Nombres de grupos dinámicos | Dynamic group names
  get gruposPosibles(): string[] {
    return this.grupos().map((g) => g.nombre);
  }

  // Función para cerrar sesión con redirección limpia y refresco forzado
  cerrarSesion(): void {
    this.auth.cerrarSesion();
  }
}
