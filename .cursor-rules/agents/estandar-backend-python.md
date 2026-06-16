> **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
> **Fecha:** 11 de abril de 2026
> **Estado:** Estándar de Backend Validado

🐍 Estándar de Desarrollo Backend (Python)
Este archivo guía a los agentes sobre cómo construir la lógica y las APIs del Framework FoodMaster.

1. Arquitectura de Negocio (Core Logic)
Modularidad: Toda funcionalidad debe estar encapsulada en módulos independientes (Blueprints).

Dualidad de Operaciones:

Comandas: Gestión de mesas y consumo presencial (lógica de estado de mesa).

Pedidos: Gestión de domicilios y pedidos externos (conservar la estructura original de Pedido).

Framework: FastAPI o Flask.

Entorno: Verificar siempre que el .venv esté activo.

2. Base de Datos y Modelos
Abstracción: Los modelos deben permitir coexistencia entre Comanda y Pedido sin colisión de lógica.

Tipado: Usar Pydantic para esquemas de validación.

3. Manejo de Puertos y CORS
CORS: Configurar para permitir peticiones desde el origen definido en la configuración global.

Puertos: Default 5000 o 8000; incluir siempre lógica de liberación de puertos (fuser -k [PUERTO]/tcp).

4. Documentación y Estilo
Formato Espejo: Comentarios obligatorios # Español | English.

Logs: Mensajes operativos claros diferenciando origen (ej: "Comanda creada en Mesa #5" | "Pedido recibido vía Domicilio ID #123").

5. Protocolo de Encabezado (Header Requirement)
Obligatorio: Todo archivo nuevo de Python debe iniciar con el siguiente bloque de comentarios:

Python
# **Creado por:** Camilo Martinez Galarza (CMG-Solutions)
# **Fecha:** [Fecha actual]
# **Estado:** [Estado del archivo: Ej. Desarrollo/Validado]
Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

Lead Architect: Camilo
"Lógica sólida, flexibilidad total en cada venta. 🐍💻"