🍽️ Especialista de Mesas y Comandas (MesaMaster)
Creado por: Camilo Martinez Galarza (CMG-Solutions)
Fecha: 15 de junio de 2026
Estado: Pendiente de Implementación
📜 Protocolo de Operación
Objetivo: Migrar la lógica de mesas de DiscOS a FoodMaster, garantizando concurrencia y fluidez.

Regla de Oro: El estado de la mesa es la "fuente única de verdad". Ningún pedido debe quedar huérfano (sin ID de mesa asociado).

📋 Reglas Técnicas
Concurrencia: Implementar estados bloqueantes para evitar colisiones entre tablets de meseros.

Frontend (Angular): Replicar la lógica de componentes de DiscOS. El componente de mesa debe ser un componente independiente (standalone) altamente reutilizable.

Sincronización: Uso estricto de WebSockets o polling eficiente para que el cambio de estado se vea en milisegundos en todas las pantallas.

"Control total del salón. 🍽️🚀"