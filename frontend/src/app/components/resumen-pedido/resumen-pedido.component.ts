import { Component, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CartService } from '../../services/cart.service';
import { AuthService } from '../../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-resumen-pedido',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './resumen-pedido.component.html',
  styleUrls: ['./resumen-pedido.component.css']
})
export class ResumenPedidoComponent {
  cartService = inject(CartService);
  authService = inject(AuthService);
  router = inject(Router);

  // 1. Acceso a los items con una señal computada para asegurar que siempre sea un array
  items = computed(() => this.cartService.items() || []);
  
  total = this.cartService.totalCarrito;
  iva = this.cartService.ivaCarrito;
  totalConIva = this.cartService.totalConIva;
  totalItems = this.cartService.totalArticulos;

  // Español: estado del formulario de entrega | English: delivery form state
  direccion = '';
  telefono = '';
  metodoPago: string | null = null;

  aumentar(idx: number) {
    this.cartService.aumentarCantidad(idx);
  }

  disminuir(idx: number) {
    this.cartService.disminuirCantidad(idx);
  }

  eliminar(idx: number) {
    this.cartService.quitarArticulo(idx);
  }

  cancelarPedido() {
    if (confirm('¿Estás seguro de que deseas cancelar el pedido y vaciar el carrito?')) {
      this.cartService.vaciarCarrito();
    }
  }

  confirmarPedido() {
    const usuario = this.authService.obtenerUsuarioActual();
    
    if (!usuario) {
      alert('Debes iniciar sesión para confirmar el pedido.');
      this.router.navigate(['/login']);
      return;
    }

    if (this.items().length === 0) {
      alert('Tu carrito está vacío.');
      return;
    }

    // Español: validar campos de entrega | English: validate delivery fields
    if (!this.direccion.trim()) {
      alert('Por favor ingresa una dirección de entrega.');
      return;
    }
    if (!this.telefono.trim()) {
      alert('Por favor ingresa un teléfono de contacto.');
      return;
    }
    if (!this.metodoPago) {
      alert('Por favor selecciona un método de pago.');
      return;
    }

    // Español: incluir datos de delivery en el pedido | English: include delivery data in the order
    this.cartService.confirmarPedido(usuario.id, {
      direccion: this.direccion.trim(),
      telefono: this.telefono.trim(),
      metodo_pago: this.metodoPago,
    }).subscribe({
      next: (res: any) => {
        alert('✅ ¡Pedido recibido con éxito! Pronto recibirás tu pedido.');
        this.cartService.vaciarCarrito();
        this.router.navigate(['/menu']);
      },
      error: (err) => {
        console.error('Error al confirmar pedido:', err);
        alert('❌ Hubo un problema al procesar tu pedido. Por favor, intenta de nuevo.');
      }
    });
  }

  volverAlMenu() {
    this.router.navigate(['/menu']);
  }
}