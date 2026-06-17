/**
 * Project Memory — FoodMaster
 * 
 * Este archivo mantiene el estado actual del sistema, las tareas completadas
 * y la arquitectura para referencia entre sesiones del agente.
 */

export const PROJECT_MEMORY = {
  version: '1.0.0',
  lastUpdate: '17 de junio de 2026',
  lastTask: 'Tarea #7 — Monitor de Cocina',

  roles: {
    admin: 'Acceso completo a dashboard, cocina, configuración',
    cocinero: 'Monitor de Cocina, Gestión de Pedidos',
    mesero: 'Gestión de Mesas y Comandas',
    domiciliario: 'Delivery Activos, Mis Pedidos',
    cliente: 'Menú, Mis Pedidos, Seguimiento',
  },

  routes: {
    cocina: { path: '/cocina', roles: ['admin', 'cocinero'], description: 'Monitor de Cocina (KDS)' },
    adminDashboard: { path: '/admin/dashboard', roles: ['admin'], description: 'Panel de Administración' },
    adminMesas: { path: '/admin/mesas', roles: ['admin', 'mesero'], description: 'Gestión de Mesas' },
    adminPedidos: { path: '/admin/pedidos', roles: ['admin', 'cocinero'], description: 'Gestión de Pedidos' },
    deliveryActivos: { path: '/delivery/activos', roles: ['admin', 'domiciliario'], description: 'Delivery Activos' },
  },

  tasks: {
    completed: [
      'Tarea #1-2: Configuración inicial, CORS, estructura Angular + Flask',
      'Tarea #3: Identidad de Usuario (JWT, fix User #undefined)',
      'Tarea #4: Flujo de Cocina Unificado (KDS)',
      'Tarea #5: Configuración del Negocio (IVA dinámico)',
      'Tarea #6: Refinamiento Gestión de Pedidos',
      'Tarea #7: Monitor de Cocina (vista independiente, roles, solo activos)',
    ],
    pending: [
      'Implementar actualización de estados de pedidos',
      'Pruebas de integración finales',
      'Tickets/facturas con datos del negocio',
    ],
  },

  // Monitor de Cocina — Flujo operativo
  monitorDeCocina: {
    description: 'Vista en tiempo real para cocina. Solo muestra pedidos activos (Pendiente + En Preparación).',
    rolesPermitidos: ['admin', 'cocinero'],
    estadosIncluidos: ['pendiente', 'en_preparacion'],
    flujo: {
      registro: 'El pedido aparece automáticamente cuando el mesero registra la comanda (abierta → pendiente)',
      preparacion: 'El cocinero hace clic en "Iniciar Preparación" (pendiente → en_preparacion)',
      despacho: 'El cocinero hace clic en "Despachar" (en_preparacion → listo/despachado). El item desaparece del monitor.',
      consolidacion: 'El pedido se consolida en Gestión de Pedidos solo cuando el estado final es "Pagado"',
    },
    endpoint: '/api/kitchen/pendientes',
    refresco: 'Automático cada 15 segundos',
  },
};
