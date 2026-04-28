├── README.md
├── __init__.py
├── backends
│   ├── __init__.py
│   ├── context_bridge
│   │   ├── __init__.py
│   │   ├── context_memory_bridge.py
│   │   └── qdrant_bridge.py
│   └── json
│       ├── __init__.py
│       ├── index_job_store.py
│       ├── library_map_store.py
│       ├── reading_cache_store.py
│       └── summary_store.py
├── contracts
│   ├── __init__.py
│   ├── indexing_types.py
│   ├── library_types.py
│   ├── reading_types.py
│   └── service_interfaces.py
├── indexing
│   ├── __init__.py
│   ├── chunker.py
│   ├── index_decision.py
│   ├── index_pipeline.py
│   ├── summary_builder.py
│   └── vector_index_writer.py
├── library_map
│   ├── __init__.py
│   ├── file_registry.py
│   ├── folder_scanner.py
│   ├── library_map_builder.py
│   └── metadata_extractor.py
├── models
│   ├── __init__.py
│   ├── chapter_view.py
│   ├── indexing_job.py
│   ├── library_item.py
│   ├── library_map.py
│   ├── reading_session.py
│   └── summary_record.py
├── orchestration
│   ├── __init__.py
│   ├── index_file_pipeline.py
│   ├── library_scan_pipeline.py
│   ├── promote_to_context_pipeline.py
│   ├── read_file_pipeline.py
│   └── summarize_file_pipeline.py
├── reading
│   ├── __init__.py
│   ├── chapter_locator.py
│   ├── docx_reader.py
│   ├── file_loader.py
│   ├── paragraph_locator.py
│   ├── pdf_reader.py
│   └── text_reader.py
├── runtime
│   ├── __init__.py
│   ├── paths.py
│   └── storage_paths.py
└── services
    ├── __init__.py
    ├── indexing_service.py
    ├── knowledge_library_facade.py
    ├── library_admin_service.py
    ├── library_service.py
    ├── promotion_service.py
    └── reading_service.py


# Knowledge Library Block

## Qué es

`app/knowledge_library/` es el bloque separado de la app para manejar:

- carpetas del usuario
- biblioteca personal
- lectura de archivos bajo demanda
- resúmenes
- chunking
- promoción opcional hacia `context_memory`

No es el cerebro principal.  
No reemplaza `context_memory`.  
No reemplaza Qdrant.  
No reemplaza MCP.

---

## Idea principal

Este bloque existe para separar 4 niveles distintos:

### 1. Library Map
La app sabe qué archivos existen.

Ejemplo:
- nombre
- ruta
- extensión
- hash
- tamaño
- tags

Acá todavía no “aprendió” el libro.

### 2. Read On Demand
La app abre y lee un archivo cuando vos lo pedís.

Ejemplo:
- leer archivo completo
- leer capítulo 2
- buscar un párrafo que mencione Einstein

### 3. Index / Summary
La app puede:
- resumir un archivo
- partirlo en chunks
- guardar un manifest de chunks
- dejarlo listo para promoción futura

### 4. Promote To Context Memory
Si vos decidís que ese archivo vale la pena, el bloque:
- toma chunks + summary
- los promueve a `context_memory`
- y opcionalmente reconstruye Qdrant

---

## Qué NO hace este bloque

Este bloque NO:

- memoriza todo automáticamente
- lee todos los libros solo por existir
- reemplaza `context_memory`
- guarda directo en Qdrant como source of truth
- obliga a usar Docker

---

## Relación con los otros bloques

### `knowledge_library`
Dueño de:
- mapear
- leer
- resumir
- chunkear
- promover

### `context_memory`
Dueño de:
- memoria/contexto del sistema
- retrieval
- snapshots
- profile/session memory
- JSON backend
- Mem0 backend
- Qdrant backend

### `qdrant`
En este flujo:
- no es el origen principal
- se reconstruye desde el JSON canónico de `context_memory`

---

## Flujo real

### Flujo 1 — solo mapear
1. registrar carpeta
2. escanear
3. guardar `library_map.json`

Resultado:
la app sabe qué archivos existen

### Flujo 2 — leer bajo demanda
1. elegir archivo
2. abrirlo
3. leer texto / capítulo / párrafo

Resultado:
uso puntual, sin memorizar todavía

### Flujo 3 — resumir / indexar
1. leer archivo
2. resumir
3. chunkear
4. guardar manifests / jobs

Resultado:
archivo listo para promoción o uso posterior

### Flujo 4 — promover a memoria
1. tomar chunks + summary
2. guardar en `context_memory` JSON
3. opcional: reconstruir Qdrant

Resultado:
el archivo pasa a formar parte del contexto utilizable por el sistema

---

## Estructura

### App
- `contracts/` → tipos del bloque
- `models/` → modelos internos
- `library_map/` → escaneo y armado del mapa
- `reading/` → lectura de archivos
- `indexing/` → resumen + chunking + jobs
- `backends/json/` → stores JSON propios
- `backends/context_bridge/` → puente hacia `context_memory` y Qdrant
- `orchestration/` → pipelines
- `services/` → entrada limpia para el resto de la app
- `runtime/` → paths internos

### Data
- `data/knowledge_library/libraries/` → carpetas de archivos
- `data/knowledge_library/collections/` → futuras colecciones manuales
- `data/knowledge_library/manifests/` → roots registrados

### Runtime
- `runtime/knowledge_library/maps/` → mapa de biblioteca
- `runtime/knowledge_library/summaries/` → resúmenes
- `runtime/knowledge_library/indexing/` → jobs, manifests
- `runtime/knowledge_library/logs/` → logs del bloque

---

## Archivos runtime más importantes

### `runtime/knowledge_library/maps/library_map.json`
Mapa general de archivos encontrados.

### `runtime/knowledge_library/maps/file_hash_index.json`
Índice de hashes por item.

### `runtime/knowledge_library/maps/folder_scan_status.json`
Estado del último scan.

### `runtime/knowledge_library/summaries/file_summaries.jsonl`
Resúmenes guardados.

### `runtime/knowledge_library/indexing/jobs.jsonl`
Historial de jobs de indexado.

### `runtime/knowledge_library/indexing/chunk_manifests/<item_id>.json`
Chunks de un archivo ya indexado.

---

## Servicios principales

### `LibraryAdminService`
Sirve para:
- registrar roots
- listar roots
- eliminar roots

### `LibraryService`
Sirve para:
- escanear roots
- obtener `library_map`

### `ReadingService`
Sirve para:
- leer archivo
- leer capítulo
- buscar párrafos

### `IndexingService`
Sirve para:
- resumir archivo
- indexar archivo
- generar chunks

### `PromotionService`
Sirve para:
- promover archivo a `context_memory`
- opcionalmente reconstruir Qdrant

---

## Uso mental correcto

### Caso A
“Solo quiero que sepa que estos libros existen”
- registrar root
- escanear

### Caso B
“Quiero leer este archivo ahora”
- read_file
- read_chapter
- find_paragraphs

### Caso C
“Quiero un resumen”
- summarize_file

### Caso D
“Quiero dejarlo listo como conocimiento”
- index_file
- promote_to_context_memory

---

## Orden recomendado de uso

1. `register_root`
2. `scan_all`
3. `read_file` o `read_chapter`
4. `summarize_file`
5. `index_file`
6. `promote_to_context_memory`
7. opcional: `rebuild_qdrant=True`

---

## Qdrant en este bloque

Qdrant no es obligatorio para usar este bloque.

Este bloque funciona igual con:
- map
- read
- summarize
- index
- promote to JSON memory

Qdrant entra solo cuando querés reconstruir el índice semántico.

Además, en la arquitectura actual:
- JSON de `context_memory` sigue siendo el source of truth
- Qdrant se reconstruye desde ese JSON

---

## Estado actual del bloque

Hoy este bloque ya puede:

- registrar carpetas
- escanear archivos
- crear library map
- leer TXT
- leer PDF
- leer DOCX
- encontrar capítulos simples
- buscar párrafos
- resumir
- chunkear
- guardar manifests
- promover a `context_memory`
- reconstruir Qdrant opcionalmente

---

## Límite actual

Todavía falta más trabajo para:

- OCR
- mejores resúmenes
- indexado vectorial directo más rico
- collections manuales editables
- UI local del bloque
- tools MCP de este bloque
- mejores detectores de capítulos
- mejores búsquedas por heading / secciones

---

## Regla importante

Primero:
- saber qué existe

Después:
- leer cuando haga falta

Después:
- resumir o indexar

Y recién al final:
- memorizar lo que vale la pena

Ese es el comportamiento correcto de este bloque.