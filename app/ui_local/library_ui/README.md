# Knowledge Library UI

## Qué es esta sección

`app/ui_local/library_ui/` es la interfaz visual separada del bloque `knowledge_library`.

Esta sección existe para dar una **vista visual, cómoda y clara** de la biblioteca del usuario y de los archivos que el sistema puede leer, resumir, indexar o promover a memoria.

---

# Por qué está esto acá

La idea del sistema es separar bien los bloques.

Ya existe un bloque funcional de backend:

- `app/knowledge_library/`

Ese bloque ya sabe:

- registrar roots
- escanear carpetas
- mapear archivos
- leer archivos
- leer capítulos
- buscar párrafos
- resumir
- chunkear
- indexar
- promover a `context_memory`
- reconstruir Qdrant opcionalmente

Pero todo eso, desde consola o scripts, es incómodo de mirar.

Entonces esta carpeta existe para resolver eso:

## objetivo principal
dar una **interfaz visual separada** para:

- ver roots
- ver archivos
- abrir archivos
- previsualizar contenido
- entender estado
- después disparar acciones como summarize / index / promote

---

# Qué NO debe confundirse

## `knowledge_library`
Es el bloque lógico/funcional.

## `library_ui`
Es la capa visual de ese bloque.

## `context_memory`
Es el dueño real de memoria/contexto del sistema.

## `Qdrant`
Es el índice semántico, no la fuente principal de verdad.

## `MCP`
Es la puerta estandarizada para exponer tools del sistema.

---

# Relación entre bloques

## 1. knowledge_library
Este bloque maneja:

- library map
- lectura bajo demanda
- summary
- chunking
- index jobs
- promoción

## 2. context_memory
Este bloque maneja:

- memoria del sistema
- snapshots
- retrieval
- profile
- session
- backend JSON
- backend Mem0
- backend Qdrant

## 3. library_ui
Esta UI:

- no inventa lógica nueva
- no guarda memoria por su cuenta
- no indexa por sí sola
- no parsea archivos directamente

Solo llama al backend ya existente y lo muestra mejor.

---

# Idea central de esta UI

Esta UI está pensada primero para:

## visualización
- ver roots
- ver estructura
- ver archivos
- ver detalles
- abrir preview

## después acciones
- refresh
- summarize
- index
- promote

## más adelante
- add / move / remove
- búsqueda
- filtros
- drag & drop
- integración más profunda con comandos o voz

---

# Regla mental importante

Esta UI no existe para “hacer inteligencia”.

Existe para:

- mostrar
- abrir
- inspeccionar
- disparar acciones del bloque

La inteligencia real sigue estando en:

- `knowledge_library`
- `context_memory`
- `retrieval`
- `Qdrant`
- el LLM

---

# Cómo pensar el sistema completo

## nivel 1 — library map
El sistema sabe qué archivos existen.

Todavía no significa que los “aprendió”.

## nivel 2 — read on demand
El sistema abre y lee un archivo cuando se lo pedís.

## nivel 3 — summarize / index
El sistema prepara el archivo para uso posterior.

## nivel 4 — promote to memory
El contenido pasa al sistema de memoria real.

## nivel 5 — qdrant
Qdrant reconstruye o indexa semánticamente desde memoria.

---

# Dónde entra Qdrant realmente

Esto es clave para no perderse:

## Qdrant NO es el inicio del flujo
Primero:
- root
- scan
- read
- summary / index
- promote to context memory

## Qdrant viene después
Qdrant entra como:

- índice semántico
- recuperación más rápida / más rica
- backend derivado

## fuente principal de verdad
Hoy, en este diseño:

- `context_memory` JSON sigue siendo la base canónica
- Qdrant se reconstruye desde ahí

Entonces:

**si un archivo está solo en la library UI, no significa que ya esté en Qdrant**

---

# Dónde entra MCP

MCP no reemplaza esta UI.

MCP sirve para exponer tools limpias del bloque.

Ejemplos de tools ya pensadas para este bloque:

- `list_library_roots`
- `scan_library`
- `read_library_map`
- `read_library_file`
- `read_library_chapter`
- `find_library_paragraphs`
- `summarize_library_file`
- `index_library_file`
- `promote_library_file_to_memory`

## Entonces
- la UI es para humanos
- MCP tools son para uso interno / agentes / integración limpia

---

# Qué hace esta carpeta hoy

`app/ui_local/library_ui/` hoy está encargada de:

- levantar una web UI separada
- usar la misma familia visual de la UI principal
- mostrar roots
- mostrar archivos
- abrir detalle de archivo
- mostrar preview básico
- ofrecer una base para acciones futuras

---

# Qué NO debe pasar acá

- no leer JSON del runtime a mano desde cualquier lado
- no meter lógica pesada de memoria dentro de la UI
- no duplicar lógica que ya existe en `knowledge_library`
- no hablar directo con Qdrant desde templates
- no meter lógica de voz acá por ahora
- no mezclar esta UI con la principal innecesariamente

---

# Ubicación dentro del proyecto

Esta UI vive dentro de:

- `app/ui_local/`

porque sigue siendo una UI local del sistema.

Pero vive en subcarpeta separada:

- `app/ui_local/library_ui/`

para mantenerla claramente independiente de la app principal.

---

# Estructura esperada de esta carpeta

## backend ui
- `appdocs.py`
- `routes.py`
- `services.py`
- `view_models.py`

## templates
- `templates/library_layout.html`
- `templates/library_home.html`
- `templates/library_file.html`
- `templates/partials/*`

## static
- `static/css/library_ui.css`
- `static/js/library_ui.js`
- `static/js/pdf_viewer.js`

## runtime helpers
- `runtime/ui_paths.py`

---

# Rol de cada archivo principal

## `appdocs.py`
Levanta la app FastAPI de esta UI.

## `routes.py`
Define endpoints de la UI.

## `services.py`
Habla con `KnowledgeLibraryFacade`.

## `view_models.py`
Prepara datos para render cómodo.

## `templates/`
Render visual de la UI.

## `static/css/library_ui.css`
Mantiene paleta, cards, spacing y coherencia visual.

## `static/js/`
Comportamiento visual, y después viewers o acciones.

---

# Cómo nos manejamos en esta sección

## Regla 1
La UI llama al bloque, no al revés.

## Regla 2
Toda acción importante debería pasar por:
- `KnowledgeLibraryFacade`
o por una capa intermedia clara.

## Regla 3
La UI no debe duplicar lógica de:
- scan
- read
- summarize
- index
- promote

## Regla 4
Si algo es visual, va acá.
Si algo es lógica de biblioteca, va en `app/knowledge_library/`.

## Regla 5
Si algo es memoria/contexto general, va en `app/context_memory/`.

## Regla 6
Si algo es tool estándar para integración/agentes, va por MCP.

---

# Cómo comunicarnos cuando trabajamos esta carpeta

Para mantener orden, usar siempre este lenguaje mental:

## si hablamos de visualización
decimos:
- home
- detail view
- preview
- file panel
- roots panel
- actions bar

## si hablamos de backend del bloque
decimos:
- scan
- read
- summarize
- index
- promote

## si hablamos de memoria
decimos:
- promote to context memory
- rebuild qdrant
- retrieval
- snapshot
- memory backend

## si hablamos de integración
decimos:
- facade
- MCP tools
- route
- service
- template
- partial

---

# Qué ya está integrado

## YA está integrado
- `knowledge_library` backend
- `KnowledgeLibraryFacade`
- MCP tools del bloque
- promote hacia `context_memory`
- Qdrant opcional
- web UI separada básica

## NO está completo todavía
- preview real de PDF
- preview real de imágenes
- botones activos de summarize/index/promote desde UI
- estado visual del archivo
- filtros / búsqueda / refresh parcial
- add / move / remove desde la UI
- edición real de roots
- integración de voz para esta UI

---

# Cómo levantar esta UI

Ejemplo:

```powershell
cd C:\AI\ASSISCLUE
.\.venv\Scripts\Activate.ps1
uvicorn app.ui_local.library_ui.appdocs:app --host 127.0.0.1 --port 8001 --reload
