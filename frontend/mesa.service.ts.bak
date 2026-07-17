async function confirmarPago(subcuentaId: number): Promise<void> {
    const response = await fetch(`/pagar_subcuenta/${subcuentaId}`, { method: 'POST' });
    if (response.ok) {
        this.estadoMesa = 'OCUPADA';
    } else {
        alert('Error al procesar el pago');
    }
}