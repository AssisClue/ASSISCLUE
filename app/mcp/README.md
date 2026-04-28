# MCP / Memory / Qdrant - Estado actual

## Resumen general

Este proyecto es un asistente local por bloques.  
La idea general del sistema es separar bien cada parte para que sea fácil de mantener, mejorar o reemplazar sin romper todo.

Hoy, de forma resumida, tenemos:

- entrada de voz / texto
- listeners y routing de eventos
- capa LLM
- salida por texto / voz / UI
- capa de memoria
- runtime files para debug y estado del sistema
- nueva capa MCP para exponer herramientas de forma ordenada

## Estado general de este bloque

Este bloque está en una etapa inicial pero útil.

Hoy **MCP ya está empezado y funcionando** como capa de integración.
Todavía no reemplaza el sistema entero ni toda la memoria, pero ya expone partes reales del proyecto de forma prolija.

La decisión actual es:

- **MCP sí**
- **Qdrant sí, como base para memoria semántica**
- **Mem0 más adelante**
- **JSON sigue siendo el fallback sano por ahora**

---

# Qué es MCP en este proyecto

## Qué hace

MCP es la capa que permite exponer funciones del sistema como herramientas estándar.

En criollo:
antes, cada bloque podía terminar conectado de forma medio manual o desordenada;
ahora, con MCP, el asistente puede hablar con ciertos bloques usando una puerta común.

## Para qué está

MCP está para:

- ordenar las integraciones
- evitar pegamento raro entre bloques
- exponer herramientas reutilizables
- hacer más fácil conectar memoria, runtime, browser, display y otras capacidades
- preparar el sistema para crecer sin meter lógica por todos lados

## Qué NO hace

MCP:

- no reemplaza el modelo
- no reemplaza la memoria
- no reemplaza Qdrant
- no reemplaza la UI
- no reemplaza STT/TTS

MCP solo da una forma estándar de acceder a cosas que ya existen o que iremos sumando.

---

# Estado actual de MCP

## Qué ya tenemos

En este chat se dejó empezado el bloque MCP y ya se sumó soporte real para inspeccionar `router_dispatch`.

Se agregaron tools para leer estado y colas del router.

### Tools actuales de este bloque

- `read_router_dispatch_status`
- `tail_router_dispatch_queue`

## Qué permiten hacer

### `read_router_dispatch_status`
Lee el estado actual de `router_dispatch`.

Sirve para:
- ver si el router está vivo
- inspeccionar estado general
- entender qué está pasando sin abrir archivos manualmente

### `tail_router_dispatch_queue`
Lee los últimos items de una cola de `router_dispatch`.

Colas soportadas:
- `router_input`
- `action`
- `response`

Sirve para:
- debug rápido
- ver qué está entrando
- ver qué acciones se encolan
- ver qué respuestas salen
- seguir el flujo del sistema

## Cómo está armado

La estructura quedó separada así:

- `app/mcp/tools/runtime_tools.py`
- `app/mcp/services/router_dispatch_mcp_service.py`
- `app/mcp/adapters/router_dispatch_adapter.py`

### Rol de cada archivo

#### `app/mcp/tools/runtime_tools.py`
Registra los tools MCP del bloque runtime.

#### `app/mcp/services/router_dispatch_mcp_service.py`
Es la capa MCP prolija:
- normaliza inputs
- valida la cola
- devuelve resultados MCP consistentes

#### `app/mcp/adapters/router_dispatch_adapter.py`
Lee los archivos reales del runtime en modo read-only.

---

# Cómo se usa hoy este bloque

## Qué puede consultar

Este bloque hoy consulta archivos dentro de:

- `runtime/status/router_dispatch/router_status.json`
- `runtime/queues/router_dispatch/router_input_queue.jsonl`
- `runtime/queues/router_dispatch/action_queue.jsonl`
- `runtime/queues/router_dispatch/response_queue.jsonl`

## Qué devuelve

### Estado
Devuelve el contenido actual de `router_status.json`.

### Cola
Devuelve:
- items
- count
- limit
- invalid_line_count
- dropped_incomplete_line
- queue
- path

## Protecciones que ya tiene

Este bloque ya contempla:

- queue inválida
- archivo faltante
- JSON roto
- JSONL con última línea incompleta
- límite controlado para no leer colas absurdamente grandes

---

# Qué ganamos con esto

Con este bloque ya ganamos algo concreto:

- `router_dispatch` dejó de ser solo runtime interno
- ahora también es una capacidad visible por MCP
- podemos inspeccionarlo sin ir a mano a los archivos
- queda listo para:
  - UI futura
  - debug mejor
  - uso por agentes
  - uso por otros bloques

En resumen:

**router_dispatch ya está expuesto por MCP en modo lectura.**

---

# Qué falta todavía en MCP

Este bloque todavía NO hace:

- escritura en colas
- métricas más completas
- resúmenes de rutas
- integración visible en UI local
- browser tools
- display tools
- memory tools completos

O sea:
está bien empezado, útil, pero todavía es una primera base.

---

# Qdrant - Estado actual

## Qué es en este proyecto

Qdrant es la base pensada para memoria semántica / vectorial.

Sirve para guardar embeddings y luego buscar recuerdos o contexto por similitud semántica.

## Estado actual

Qdrant está contemplado como parte del diseño de memoria, pero todavía no es el backend dominante del sistema en uso normal.

La arquitectura ya lo contempla como base seria para la parte semántica, pero el sistema todavía sigue apoyándose en JSON como fallback/default para varias partes del runtime y memoria.

## Decisión actual

Qdrant sí se considera parte importante del sistema.

Pero hoy la estrategia correcta es:

- mantenerlo como base preparada
- no forzar todavía toda la memoria encima de Qdrant
- dejar JSON como respaldo simple y estable

# Resumen de decisiones tomadas en este chat

## Ya hecho
- se avanzó con MCP
- se agregó soporte MCP read-only para `router_dispatch`
- se dejó una base útil y correcta para crecer
- se confirmó que Qdrant sigue siendo parte importante del diseño
- se aclaró que Mem0 requiere modelo y no conviene enchufarlo a ciegas

## Decisiones actuales
- MCP: seguir
- router_dispatch por MCP: sí
- Qdrant: sí
- JSON: fallback sano por ahora

---

# Cómo aprovechar este bloque ahora

Hoy este bloque sirve para:

- inspeccionar el sistema más fácil
- ver colas del router sin entrar manualmente a runtime
- entender si el pipeline está moviéndose
- preparar la base para futuros tools MCP
- tener una arquitectura más ordenada

