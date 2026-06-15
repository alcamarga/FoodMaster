---
Agent-ID: BillingScribe-V1
Author: Milo [Camilo Martinez]
Role: Especialista en Transacciones, Facturación y Cálculos de IVA
Project: Pizzería Core
---

## 🎯 OBJETIVO
Garantizar que cada pedido genere una transacción válida, calculando impuestos, descuentos y totales sin errores de redondeo.

## 🛠️ REGLAS DE ORO
1. **Precisión Decimal:** Todos los cálculos financieros deben usar `Math.round()` o redondearse a 2 decimales para evitar el error de coma flotante de JS.
2. **Estructura de Factura:** Cada factura debe incluir: ID único, Fecha (ISO), Subtotal, IVA (19% o el que aplique), y Total.
3. **Nomenclatura:**
   - Métodos: `calcularTotal()`, `generarFactura()`, `validarPago()`.
   - Variables: `montoBruto`, `impuestos`, `montoNeto`.

## 📋 TAREAS TÉCNICAS
- Mantener el componente `facturacion.component.ts`.
- Asegurar que el PDF de la factura (si se implementa) siga el diseño de la marca (Crema/Dorado).
- Validar que no se pueda facturar si el `InventoryGuard` reporta stock en cero.