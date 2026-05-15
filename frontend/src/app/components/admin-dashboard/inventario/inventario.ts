import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

// --- INTERFACES CORREGIDAS ---
interface Insumo {
  id: number;
  nombre: string;
  cantidad: number;
  unidad: string;
  precio: number;
  stock_minimo: number;
}

interface InsumoPayload {
  nombre: string;
  cantidad: number;
  unidad: string;
  precio: number;
  stock_minimo: number;
}

@Component({
  selector: 'app-inventario',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './inventario.html',
  styleUrls: ['./inventario.css'] // <-- Cambiado de .scss a .css
})
export class InventarioComponent implements OnInit {
  insumos = signal<Insumo[]>([]);
  cargando = signal<boolean>(false);
  mensajeExito = signal<string | null>(null);
  mensajeError = signal<string | null>(null);

  mostrarFormulario = false;
  editandoId: number | null = null;

  // Opciones para el select de unidades
  unidades = ['gr', 'ml', 'und', 'oz', 'lb', 'kg'];

  nuevoInsumo: InsumoPayload = {
    nombre: '',
    cantidad: 0,
    unidad: 'gr',
    precio: 0,
    stock_minimo: 0
  };

  edicion: any = {};

  private apiUrl = 'http://localhost:5000/api/insumos';

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.cargarInsumos();
  }

  cargarInsumos() {
    this.cargando.set(true);
    this.http.get<Insumo[]>(this.apiUrl).subscribe({
      next: (data) => {
        this.insumos.set(data);
        this.cargando.set(false);
      },
      error: () => {
        this.mensajeError.set('Error al conectar con el servidor');
        this.cargando.set(false);
      }
    });
  }

  toggleFormulario() {
    this.mostrarFormulario = !this.mostrarFormulario;
  }

  agregarInsumo() {
    if (!this.nuevoInsumo.nombre) {
      this.mensajeError.set('El nombre es obligatorio');
      return;
    }

    this.http.post<Insumo>(this.apiUrl, this.nuevoInsumo).subscribe({
      next: (insumo) => {
        this.insumos.set([...this.insumos(), insumo]);
        this.resetFormulario();
        this.mensajeExito.set('Insumo agregado correctamente');
        this.mostrarFormulario = false;
      },
      error: (err) => this.mensajeError.set('Error al guardar el insumo')
    });
  }

  iniciarEdicion(insumo: Insumo) {
    this.editandoId = insumo.id;
    this.edicion = { ...insumo };
  }

  cancelarEdicion() {
    this.editandoId = null;
    this.edicion = {};
  }

  guardarEdicion(id: number) {
    this.http.put(`${this.apiUrl}/${id}`, this.edicion).subscribe({
      next: () => {
        const actualizados = this.insumos().map(i => i.id === id ? { ...this.edicion } : i);
        this.insumos.set(actualizados);
        this.cancelarEdicion();
        this.mensajeExito.set('Insumo actualizado');
      },
      error: () => this.mensajeError.set('No se pudo actualizar')
    });
  }

  eliminarInsumo(id: number) {
    if (confirm('¿Estás seguro de eliminar este insumo?')) {
      this.http.delete(`${this.apiUrl}/${id}`).subscribe({
        next: () => {
          this.insumos.set(this.insumos().filter(i => i.id !== id));
          this.mensajeExito.set('Insumo eliminado');
        }
      });
    }
  }

  estadoStock(insumo: Insumo): string {
    return insumo.cantidad <= insumo.stock_minimo ? 'bajo' : 'ok';
  }

  private resetFormulario() {
    this.nuevoInsumo = {
      nombre: '',
      cantidad: 0,
      unidad: 'gr',
      precio: 0,
      stock_minimo: 0
    };
  }
}