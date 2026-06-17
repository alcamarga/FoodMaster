🛠️ Instrucciones Generales del Sistema
Creado por: Camilo Martinez Galarza (CMG-Solutions)
Fecha: 15 de junio de 2026
Estado: Validado
Modificaciones: Al realizar modificaciones significativas, el agente debe mantener o actualizar este encabezado.

📜 Control de Autoría y Arquitectura
Lead Architect: Camilo Martinez Galarza

Asistente de Arquitectura: Gemini/Cami

"Este documento es la ley operativa en el ecosistema FoodMaster. Toda desviación de las reglas aquí descritas debe ser consultada con el Lead Architect."

Este archivo guía a los agentes sobre cómo operar en el entorno de desarrollo (WSL/Ubuntu).

1. Gestión de Entorno (Python)
Siempre verificar que el entorno virtual .venv esté activo antes de ejecutar comandos.

Comando de activación: source backend/.venv/bin/activate.

2. Permisos y Ejecución
Preferir el uso de comandos sin sudo a menos que sea estrictamente necesario para instalaciones del sistema en Ubuntu/WSL.

Prohibido: Modificar manualmente archivos dentro de la carpeta .venv.

3. Resolución de Conflictos (Puertos)
Diagnóstico: Utilizar sudo lsof -i :[PUERTO] para identificar procesos.

Liberación: Utilizar fuser -k [PUERTO]/tcp para vaciar puertos ocupados.

Nota: Esta política es la fuente única de verdad para la gestión de puertos en FoodMaster.

4. Protocolo de Documentación
Encabezado Obligatorio: Todo archivo nuevo debe incluir el bloque de autoría (Camilo Martinez Galarza / CMG-Solutions) definido en los estándares específicos de Backend y Frontend.

Tablero de Tareas: Actualizar tasks.md tras cada hito importante de desarrollo.

5. Política de Idiomas (Formato Espejo)
Todo comentario dentro del código es obligatorio bajo el formato: # [Español] | [English] (o //, /*, <!-- según el lenguaje).

Ejemplo: // Inicializar controlador | Initialize controller

6. Alcance y Seguridad
Alcance: Este archivo aplica de forma transversal a todo el proyecto FoodMaster (/backend, /frontend, y scripts de utilería). Es la normativa superior que rige el comportamiento de los agentes en el sistema.

Protocolo de Seguridad: Toda implementación relacionada con autenticación, manejo de secretos, o exposición de APIs debe cumplir estrictamente con los lineamientos definidos en el archivo seguridad.md. Ante la duda, el agente debe detenerse y consultar seguridad.md antes de escribir código.

### PROTOCOLO DE DOCUMENTACIÓN OBLIGATORIO
Al finalizar CUALQUIER tarea, el agente DEBE ejecutar automáticamente:
1. **Actualizar `tasks.md`**: Mover la tarea a 'Completada' y añadir un resumen.
2. **Actualizar `project_memory.ts`**: Registrar cambios en endpoints, nueva lógica o cambios en modelos de datos.
3. **Actualizar `README.md`**: Documentar nuevas funcionalidades para el usuario final.
4. **Verificación**: No se considerará la tarea finalizada hasta que estos 3 archivos estén actualizados.

"Lógica sólida, orden total, seguridad blindada. 🚀"