import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { PizzaService } from '../../services/pizza.service';
import { AuthService } from '../../services/auth.service';
import { CartService } from '../../services/cart.service';
import { GrupoProductoService } from '../../services/grupo_producto.service';
import { Pizza } from '../../models/pizza.model';
import { IGrupoProducto } from '../../models/grupo_producto.model';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-menu',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './menu.component.html',
  styleUrls: ['./menu.component.css']
})
export class MenuComponent implements OnInit {
  pizzaService = inject(PizzaService);
  auth = inject(AuthService);
  router = inject(Router);
  route = inject(ActivatedRoute);
  cartService = inject(CartService);
  grupoProductoService = inject(GrupoProductoService);

  pizzas = signal<Pizza[]>([]);
  grupos = signal<IGrupoProducto[]>([]);
  cargando = signal(true);
  cargandoCategorias = signal(true);
  error = signal<string | null>(null);
  estaAutenticado = computed(() => this.auth.estaAutenticado());
  usuarioActual = this.auth.obtenerUsuarioActual();
  mensajeExito = signal<string | null>(null);
  // Estado para animar el botón pulsado
  agregandoState = signal<{ [key: string]: boolean }>({});


  ngOnInit(): void {
    this.cargarMenu();
    this.cargarGrupos();
    this.manejarIntencionCompra();
  }

  private manejarIntencionCompra(): void {
    this.route.queryParams.subscribe(params => {
      const pizzaId = params['agregar'];
      const tamanoStr = params['tamano'];
      if (pizzaId && tamanoStr && this.estaAutenticado()) {
        const pizza = this.pizzas().find(p => p.id === Number(pizzaId));
        if (pizza) {
          const cat = pizza.categoria || 'Pizza';
          let precio = 0;
          const etiquetas = this.getEtiquetasPrecio(cat);
          if (tamanoStr === etiquetas[0]) precio = pizza.precio_1 ?? 0;
          else if (tamanoStr === etiquetas[1]) precio = pizza.precio_2 || 0;
          else if (tamanoStr === etiquetas[2]) precio = pizza.precio_3 || 0;

          this.cartService.agregarAlCarrito(pizza, tamanoStr, precio);
          this.mensajeExito.set('¡Producto agregado al carrito! 🎉');
          this.router.navigate(['/menu'], { replaceUrl: true });
          setTimeout(() => this.mensajeExito.set(null), 3000);
        }
      }
    });
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
        console.error('[Menu] Error al cargar grupos:', err);
        this.cargandoCategorias.set(false);
      },
    });
  }

  // Obtener etiquetas de precio para un grupo desde los datos dinámicos | Get price labels for a group from dynamic data
  getEtiquetasPrecio(nombreGrupo: string): string[] {
    const grupo = this.grupos().find((g) => g.nombre === nombreGrupo);
    if (grupo) {
      const etiquetas = [grupo.etiqueta_1];
      if (grupo.etiqueta_2) etiquetas.push(grupo.etiqueta_2);
      if (grupo.etiqueta_3) etiquetas.push(grupo.etiqueta_3);
      return etiquetas;
    }
    return ['Único'];
  }

  // Español: detecta si un producto tiene un solo precio (precio único) | English: detect if a product has a single price
  esPrecioUnico(pizza: Pizza): boolean {
    const tienePrecio2 = pizza.precio_2 !== undefined && pizza.precio_2 !== null && pizza.precio_2 > 0;
    const tienePrecio3 = pizza.precio_3 !== undefined && pizza.precio_3 !== null && pizza.precio_3 > 0;
    return !tienePrecio2 && !tienePrecio3;
  }

  // Español: obtener etiqueta de precio considerando precio único (muestra "Plato") | English: get price label considering single price (shows "Plato")
  getLabelPrecio(pizza: Pizza, index: number): string {
    const etiquetas = this.getEtiquetasPrecio(pizza.categoria || 'Pizza');
    // Español: para productos de un solo precio, mostrar "Plato" en el primer slot | English: for single-price products, show "Plato" on the first slot
    if (index === 0 && this.esPrecioUnico(pizza)) {
      return 'Plato';
    }
    return etiquetas[index] || '';
  }

  cargarMenu(): void {
    this.cargando.set(true);
    this.pizzaService.obtenerCatalogoPizzas().subscribe({
      next: (pizzas) => {
        // Agregamos 'pizzas &&' para asegurar que existan antes de filtrar
        if (pizzas && Array.isArray(pizzas)) {
          // El backend PostgreSQL ya no manda el campo 'activo', así que lo omitimos
          this.pizzas.set(pizzas);
          // Español: depuración de rutas de imagen | English: debug image paths
          pizzas.forEach(p => {
            if (p.imagen_url || p.imagen) {
              console.log(`[Menu] Imagen para "${p.nombre}":`, p.imagen_url || p.imagen);
            }
          });
        } else {
          this.pizzas.set([]); // Si no hay nada, lista vacía
        }
        this.cargando.set(false);
      },
      error: (err) => {
        this.cargando.set(false);
        console.error('[Menu] Error al cargar productos:', err);
      }
    });
  }

  agregarAlCarrito(pizza: Pizza, tamanoLabel: string, precio: number): void {
    if (!this.estaAutenticado()) {
      this.router.navigate(['/login']);
      return;
    }

    const key = `${pizza.id}-${tamanoLabel}`;

    // Feedback visual en el botón
    this.agregandoState.update(prev => ({ ...prev, [key]: true }));

    // Llamada al servicio
    this.cartService.agregarAlCarrito(pizza, tamanoLabel, precio);

    // Mensaje global
    this.mensajeExito.set(`¡${pizza.nombre} (${tamanoLabel}) agregado! 🍽️`);

    // Resetear estados después de 1.5 segundos
    setTimeout(() => {
      this.agregandoState.update(prev => ({ ...prev, [key]: false }));
      this.mensajeExito.set(null);
    }, 1500);
  }


  // --- FUNCIONES PARA TAGS ---
  agregarTag(): void {
    const tag = this.nuevoTag.trim().toLowerCase();
    if (tag && !this.nuevaPizza.tags.includes(tag)) {
      this.nuevaPizza.tags = [...this.nuevaPizza.tags, tag];
      this.nuevoTag = '';
    }
  }

  eliminarTag(tag: string): void {
    this.nuevaPizza.tags = this.nuevaPizza.tags.filter((t: string) => t !== tag);
  }

  // --- FUNCIONES PARA EL ADMIN ---
  irAlDashboard(): void {
    this.router.navigate(['/admin/dashboard']);
  }

  // Control del formulario de edición
  mostrarFormulario = false;
  pizzaEnEdicionId: number | null = null;

  // Nombres de grupos dinámicos desde el backend | Dynamic group names from backend
  get gruposPosibles(): string[] {
    return this.grupos().map((g) => g.nombre);
  }

  // Español: inyección para subida de imágenes | English: injection for image upload
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  nuevaPizza: any = {
    nombre: '',
    descripcion: '',
    categoria: '',
    tags: [],
    imagen_url: '',
    precio_1: 0,
    precio_2: 0,
    precio_3: 0
  };
  nuevoTag = '';
  preciosPersonalizados: { label: string; precio: number }[] = [];
  // Español: estado de subida de imagen | English: image upload state
  imagenPreview: string | ArrayBuffer | null = null;
  subiendoImagen = false;

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

  getEtiquetaPrecioForm(index: number): string {
    const regla = this.obtenerReglaVisualizacion();
    if (regla) {
      return regla.etiquetas[index - 1] || '';
    }
    return '';
  }

  mostrarCampoPrecioForm(index: number): boolean {
    const regla = this.obtenerReglaVisualizacion();
    if (regla) {
      return index <= regla.campos;
    }
    return index === 1;
  }

  toggleFormulario(): void {
    this.mostrarFormulario = !this.mostrarFormulario;
    if (!this.mostrarFormulario) this.pizzaEnEdicionId = null;
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
        console.error('[Menu] Error al subir imagen:', err);
        this.subiendoImagen = false;
        alert('Error al subir la imagen. Intenta de nuevo.');
      },
    });
  }

  modificarPizza(id: number): void {
    const pizza = this.pizzas().find(p => p.id === id);
    if (pizza) {
      this.pizzaEnEdicionId = pizza.id;
      this.imagenPreview = null;
      this.nuevaPizza = {
        nombre: pizza.nombre,
        descripcion: pizza.descripcion,
        categoria: pizza.categoria || this.gruposPosibles[0] || 'General',
        tags: pizza.tags || [],
        imagen_url: pizza.imagen_url || pizza.imagen || '',
        precio_1: pizza.precio_1,
        precio_2: pizza.precio_2,
        precio_3: pizza.precio_3
      };
      this.mostrarFormulario = true;
    }
  }

  guardarPizza(): void {
    if (this.pizzaEnEdicionId) {
      // Español: enviar solo los campos de precio visibles | English: send only visible price fields
      const payload = { ...this.nuevaPizza };
      if (!this.mostrarCampoPrecioForm(1)) payload.precio_1 = undefined;
      if (!this.mostrarCampoPrecioForm(2)) payload.precio_2 = undefined;
      if (!this.mostrarCampoPrecioForm(3)) payload.precio_3 = undefined;
      // Español: incluir precios personalizados si el grupo lo permite | English: include custom prices if group allows
      if (this.puedeTenerPreciosPersonalizados() && this.preciosPersonalizados.length > 0) {
        const disponibles = [1, 2, 3].filter(i => !payload[`precio_${i}`] || payload[`precio_${i}`] === 0);
        for (let i = 0; i < this.preciosPersonalizados.length && i < disponibles.length; i++) {
          payload[`precio_${disponibles[i]}`] = this.preciosPersonalizados[i].precio;
        }
      }

      this.pizzaService.actualizarPizza(this.pizzaEnEdicionId, payload).subscribe({
        next: () => {
          this.cargarMenu();
          this.cancelarFormulario();
        },
        error: (err) => {
          console.error('Error al actualizar producto:', err);
          alert('No se pudo actualizar el producto.');
        }
      });
    }
  }

  // Agregar un campo de precio personalizado | Add a custom price field
  agregarPrecioPersonalizado(): void {
    this.preciosPersonalizados.push({ label: '', precio: 0 });
  }

  eliminarPrecioPersonalizado(index: number): void {
    this.preciosPersonalizados.splice(index, 1);
  }

  // Español: limpiar precios personalizados al cambiar de grupo | English: clear custom prices when switching groups
  cambiarGrupo(): void {
    this.preciosPersonalizados = [];
  }

  puedeTenerPreciosPersonalizados(): boolean {
    const regla = this.obtenerReglaVisualizacion();
    if (regla) {
      return regla.permitirPersonalizados;
    }
    return false;
  }

  cancelarFormulario(): void {
    const grupos = this.grupos();
    const fallback = grupos.length > 0 ? grupos[0].nombre : 'General';
    this.nuevaPizza = { nombre: '', descripcion: '', categoria: fallback, tags: [], imagen_url: '', precio_1: 0, precio_2: 0, precio_3: 0 };
    this.preciosPersonalizados = [];
    this.imagenPreview = null;
    this.pizzaEnEdicionId = null;
    this.mostrarFormulario = false;
  }
}
