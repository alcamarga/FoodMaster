🛡️ Estándar de Seguridad y Protección de Datos
Creado por: Camilo Martinez Galarza (CMG-Solutions)
Fecha: 15 de junio de 2026
Estado: Validado
Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

📜 Protocolo de Seguridad Corporativa
Lead Architect: Camilo Martinez Galarza

Asistente de Arquitectura: Gemini/Cami

"La seguridad no es una opción, es la base del sistema FoodMaster. Toda violación a este estándar se considera un error crítico."

1. Gestión de Secretos y Variables
Cero Hardcoding: Prohibido escribir claves API, tokens, contraseñas o URIs de bases de datos directamente en el código.

Uso de .env: Toda configuración sensible debe residir exclusivamente en variables de entorno.

Git Hygiene: El archivo .env debe estar permanentemente incluido en el .gitignore.

2. Defensa contra Ataques Comunes
Validación de Inputs: Sanitizar y validar toda entrada en Frontend (Angular) y obligatoriamente en Backend (Python/Flask) para prevenir SQL Injection y XSS.

Arquitectura Segura: El Frontend jamás se conecta directamente a la base de datos; toda comunicación debe ser mediada por el Backend.

CORS: Prohibido aceptar peticiones de dominios abiertos. Se debe configurar una whitelist estricta.

3. Control de Acceso y Sesiones
Rutas Protegidas: Acceso privado condicionado a autenticación válida.

Validación en Servidor: El servidor es la única autoridad para validar roles y permisos. Confiar en la lógica del frontend está estrictamente prohibido.

Rate Limiting: Implementar límites de peticiones por IP para mitigar ataques de fuerza bruta.

4. Auditoría y Manejo de Datos
Errores Seguros: Mensajes de error genéricos para el usuario. No exponer rutas, versiones de software o estructuras de DB.

Logs Limpios: Queda prohibido registrar datos sensibles (contraseñas, tokens, tarjetas) en consola o archivos de log.

Higiene de Dependencias: Ejecutar periódicamente npm audit y pip audit para mitigar vulnerabilidades.

"Seguridad por diseño. 🔐"