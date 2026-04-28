C:\AI\ASSISCLUE\app\context_memory\
│
├── README.md
├── __init__.py
│
├── contracts\
│   ├── __init__.py
│   ├── context_types.py
│   ├── input_types.py
│   ├── retrieval_types.py
│   ├── task_types.py
│   ├── backend_interfaces.py
│   └── service_interfaces.py
│
├── ingest\
│   ├── __init__.py
│   ├── chat_history_reader.py
│   ├── session_events_reader.py
│   ├── screenshot_notes_reader.py
│   ├── file_context_reader.py
│   ├── runtime_state_reader.py
│   └── input_assembler.py
│
├── normalize\
│   ├── __init__.py
│   ├── text_cleaner.py
│   ├── event_normalizer.py
│   ├── metadata_normalizer.py
│   ├── memory_text_normalizer.py
│   └── dedupe_keys.py
│
├── classify\
│   ├── __init__.py
│   ├── memory_kind_classifier.py
│   ├── source_classifier.py
│   ├── importance_scorer.py
│   ├── recency_scorer.py
│   ├── promotion_rules.py
│   └── task_context_router.py
│
├── extract\
│   ├── __init__.py
│   ├── fact_extractor.py
│   ├── profile_extractor.py
│   ├── project_extractor.py
│   ├── topic_extractor.py
│   ├── timeline_extractor.py
│   └── relation_extractor.py
│
├── summarize\
│   ├── __init__.py
│   ├── live_context_summary.py
│   ├── recent_context_summary.py
│   ├── daily_context_summary.py
│   ├── project_context_summary.py
│   └── session_rollup.py
│
├── models\
│   ├── __init__.py
│   ├── memory_item.py
│   ├── memory_fact.py
│   ├── memory_relation.py
│   ├── session_snapshot.py
│   ├── live_context_snapshot.py
│   ├── recent_context_snapshot.py
│   ├── user_profile_snapshot.py
│   └── task_context_packet.py
│
├── builders\
│   ├── __init__.py
│   ├── memory_record_builder.py
│   ├── live_context_builder.py
│   ├── recent_context_builder.py
│   ├── user_profile_builder.py
│   ├── project_context_builder.py
│   ├── task_context_builder.py
│   └── context_packet_builder.py
│
├── linking\
│   ├── __init__.py
│   ├── relation_linker.py
│   ├── duplicate_linker.py
│   ├── timeline_linker.py
│   └── project_linker.py
│
├── compact\
│   ├── __init__.py
│   ├── memory_compactor.py
│   ├── recent_context_compactor.py
│   ├── profile_compactor.py
│   ├── session_compactor.py
│   └── archive_compactor.py
│
├── retrieval\
│   ├── __init__.py
│   ├── lexical_retrieval.py
│   ├── semantic_retrieval.py
│   ├── hybrid_retrieval.py
│   ├── retrieval_ranker.py
│   ├── retrieval_filters.py
│   ├── task_context_retrieval.py
│   └── memory_search_service.py
│
├── backends\
│   ├── __init__.py
│   ├── registry.py
│   │
│   ├── json\
│   │   ├── __init__.py
│   │   ├── json_memory_store.py
│   │   ├── json_profile_store.py
│   │   ├── json_snapshot_store.py
│   │   └── json_index_store.py
│   │
│   ├── mem0\
│   │   ├── __init__.py
│   │   ├── mem0_adapter.py
│   │   ├── mem0_memory_store.py
│   │   ├── mem0_profile_store.py
│   │   └── mem0_snapshot_store.py
│   │
│   └── qdrant\
│       ├── __init__.py
│       ├── qdrant_memory_index.py
│       ├── qdrant_search_adapter.py
│       └── qdrant_collection_manager.py
│
├── snapshots\
│   ├── __init__.py
│   ├── live_snapshot_service.py
│   ├── recent_snapshot_service.py
│   ├── daily_snapshot_service.py
│   └── project_snapshot_service.py
│
├── session\
│   ├── __init__.py
│   ├── session_memory.py
│   ├── short_term_memory.py
│   ├── current_activity_state.py
│   └── session_window_manager.py
│
├── profile\
│   ├── __init__.py
│   ├── user_profile_memory.py
│   ├── preference_store.py
│   ├── stable_fact_store.py
│   └── profile_merge_rules.py
│
├── orchestration\
│   ├── __init__.py
│   ├── ingest_pipeline.py
│   ├── memory_update_pipeline.py
│   ├── snapshot_pipeline.py
│   ├── retrieval_pipeline.py
│   └── context_pipeline.py
│
├── services\
│   ├── __init__.py
│   ├── context_memory_service.py
│   ├── live_context_service.py
│   ├── recent_context_service.py
│   ├── profile_context_service.py
│   ├── task_context_service.py
│   └── memory_admin_service.py
│
└── runtime\
    ├── __init__.py
    ├── paths.py
    ├── storage_paths.py
    └── source_registry.py

    # Context Memory Block




## Objetivo

Este bloque es el dueño de **contexto y memoria** del sistema.

Su trabajo es:

- recibir entradas crudas
- transformarlas en contexto útil
- guardar memoria
- recuperar memoria según tarea
- entregar paquetes listos para otros bloques

Este bloque debe funcionar **separado del resto de la app**.

La app no debe depender de Mem0 directamente.
La app no debe conocer detalles internos de storage, retrieval o snapshots.

La app solo consume servicios de este bloque.

---

## Principio principal

**Context Memory no es Mem0.**

Mem0 es solo un posible backend interno.

La arquitectura de este bloque, sus productos, sus tipos de contexto, sus reglas de promoción y sus modos de retrieval son responsabilidad de este bloque.

---

## Responsabilidades del bloque

### 1. Ingesta
Leer y unificar entradas como:

- historial de chat
- eventos de sesión
- notas de screenshots
- archivos de contexto
- runtime state
- actividad reciente

### 2. Normalización
Limpiar texto, metadata y eventos para que el sistema procese todo con formatos consistentes.

### 3. Clasificación
Decidir qué representa cada dato:

- memoria persistente
- contexto reciente
- perfil de usuario
- evento de sesión
- hecho técnico
- información descartable

### 4. Extracción
Sacar valor estructurado de entradas crudas:

- facts
- preferencias
- proyectos
- relaciones
- timeline
- temas

### 5. Resumen
Construir productos internos como:

- live context
- recent context
- daily context
- project context

### 6. Persistencia
Guardar memoria y snapshots usando backends desacoplados.

### 7. Retrieval
Buscar memoria según la tarea actual:

- screenshot analysis
- coding help
- timeline questions
- project follow-up
- user preference recall

---

## Lo que este bloque produce

Este bloque debe poder producir, como mínimo:

### Live Context
Qué está pasando ahora.

Ejemplos:
- tarea actual
- tema activo
- eventos recientes
- screenshot notes recientes
- último problema detectado

### Recent Context
Qué pasó en la ventana reciente.

Ejemplos:
- últimas horas
- hoy
- actividad por bloques
- cambios recientes
- errores recientes

### User Profile
Memoria estable y preferencias.

Ejemplos:
- estilo de respuesta
- proyectos principales
- forma de trabajo
- preferencias técnicas

### Project Context
Contexto filtrado por proyecto o tema.

Ejemplos:
- ASSISCLUE
- LIVEKIT
- TTS
- Mem0
- STT

### Task Context
Contexto armado para una tarea puntual.

Ejemplos:
- analyze screenshot using coding memory
- answer using timeline memory
- retrieve user preference memory
- use recent troubleshooting context

### Memory Search
Búsqueda puntual en memoria persistente.

---

## Qué NO debe pasar

- La app no debe hablar directo con Mem0
- La app no debe leer stores internos
- La app no debe decidir qué backend usar
- Los runners no deben reconstruir contexto por su cuenta
- Cada bloque no debe tener su propia memoria paralela sin pasar por esta capa

---

## Regla de integración

La integración correcta es:

app -> services/context_memory_service.py -> pipelines -> retrieval/builders/backends

Nunca:

app -> mem0 directo

---

## Separación por capas

### contracts
Tipos e interfaces oficiales.

### ingest
Lectores de inputs crudos.

### normalize
Limpieza y unificación.

### classify
Reglas de clasificación y promoción.

### extract
Extracción de facts, topics, relations y timeline.

### summarize
Resúmenes internos.

### models
Modelos propios del bloque.

### builders
Armado de productos finales.

### linking
Relaciones y uniones entre recuerdos y contextos.

### compact
Deduplicación, priorización y archivo.

### retrieval
Búsqueda y ranking por tarea.

### backends
Storage e indexado desacoplado.

### snapshots
Contexto ya cocinado y persistido.

### session
Memoria de sesión y estado volátil.

### profile
Preferencias y facts estables.

### orchestration
Pipelines internos del bloque.

### services
API interna estable para el resto de la app.

### runtime
Paths y registros internos.

---

## Backend policy

Este bloque debe soportar múltiples backends.

### JSON
Fallback local, simple y robusto.

### Mem0
Backend de memoria persistente y retrieval.

### Qdrant
Backend de indexado/vector search cuando se necesite.

El bloque debe poder seguir funcionando aunque Mem0 no esté listo.

---

## Regla importante sobre retrieval

No existen “memorias distintas” por feature.

Existe una sola arquitectura de memoria/contexto, pero con diferentes formas de consulta.

Ejemplos:

- screenshot de código -> retrieval filtrado para coding/task context
- reuniones semana pasada -> retrieval filtrado para timeline/recent context
- preferencias del usuario -> retrieval filtrado para profile memory

El cambio ocurre en el **retrieval mode**, no en duplicar memorias.

---

## Inputs oficiales esperados

- chat history
- session events
- screenshot notes
- file context
- runtime state
- manual notes
- structured actions

---

## Outputs oficiales esperados

- live context snapshot
- recent context snapshot
- user profile snapshot
- project context packet
- task context packet
- memory search results

---

## Servicio principal esperado

El resto del sistema debe entrar por servicios estables, por ejemplo:

- `get_live_context()`
- `get_recent_context()`
- `get_user_profile_context()`
- `get_project_context(project_name)`
- `get_task_context(task_type, query, hints)`
- `search_memory(query, filters)`

---

## Decisiones de diseño

1. Este bloque es dueño de la lógica de contexto y memoria
2. Mem0 es backend, no arquitectura
3. El historial es input principal, pero no único
4. Los snapshots deben existir para no recalcular siempre
5. El retrieval debe cambiar según tarea
6. La app solo consume servicios estables
7. El fallback JSON debe seguir vivo
8. Nada crítico debe depender solo de Mem0

---

## Meta final

Tener un bloque que pueda:

- cambiar de backend sin romper la app
- cambiar de fuentes de input sin reescribir la arquitectura
- producir contexto útil para múltiples tareas
- escalar desde fallback JSON hasta Mem0 + Qdrant
- seguir funcionando aunque una parte falle





Carpetas
contracts
models
services
runtime
backends
orchestration
Archivos
contracts/context_types.py
contracts/input_types.py
contracts/retrieval_types.py
contracts/task_types.py
contracts/backend_interfaces.py
contracts/service_interfaces.py
models/memory_item.py
models/task_context_packet.py
models/live_context_snapshot.py
models/recent_context_snapshot.py
models/user_profile_snapshot.py
services/context_memory_service.py
runtime/paths.py
runtime/storage_paths.py
backends/registry.py

Objetivo: dejar definidos tipos, contratos y puerta de entrada.

Tanda 2 — Session y Profile

Mover y ordenar lo que ya tenés.

Archivos
session/session_memory.py
session/short_term_memory.py
session/current_activity_state.py
session/session_window_manager.py
profile/user_profile_memory.py
profile/preference_store.py
profile/stable_fact_store.py
profile/profile_merge_rules.py

Objetivo: separar memoria volátil de memoria estable.

Tanda 3 — Ingest + Normalize

Entrada limpia del bloque.

Archivos
ingest/chat_history_reader.py
ingest/session_events_reader.py
ingest/screenshot_notes_reader.py
ingest/file_context_reader.py
ingest/runtime_state_reader.py
ingest/input_assembler.py
normalize/text_cleaner.py
normalize/event_normalizer.py
normalize/metadata_normalizer.py
normalize/memory_text_normalizer.py
normalize/dedupe_keys.py

Objetivo: dejar una entrada única y consistente.

Tanda 4 — Classify + Extract

La lógica de producto real.

Archivos
classify/memory_kind_classifier.py
classify/source_classifier.py
classify/importance_scorer.py
classify/recency_scorer.py
classify/promotion_rules.py
classify/task_context_router.py
extract/fact_extractor.py
extract/profile_extractor.py
extract/project_extractor.py
extract/topic_extractor.py
extract/timeline_extractor.py
extract/relation_extractor.py

Objetivo: decidir qué significa cada dato.

Tanda 5 — Linking + Compact + Builders

Transformar piezas en productos útiles.

Archivos
linking/relation_linker.py
linking/duplicate_linker.py
linking/timeline_linker.py
linking/project_linker.py
compact/memory_compactor.py
compact/recent_context_compactor.py
compact/profile_compactor.py
compact/session_compactor.py
compact/archive_compactor.py
builders/memory_record_builder.py
builders/live_context_builder.py
builders/recent_context_builder.py
builders/user_profile_builder.py
builders/project_context_builder.py
builders/task_context_builder.py
builders/context_packet_builder.py

Objetivo: producir objetos finales bien armados.

Tanda 6 — Retrieval

Acá vive la diferencia entre “usar memoria para código” y “usar memoria para timeline”.

Archivos
retrieval/lexical_retrieval.py
retrieval/semantic_retrieval.py
retrieval/hybrid_retrieval.py
retrieval/retrieval_ranker.py
retrieval/retrieval_filters.py
retrieval/task_context_retrieval.py
retrieval/memory_search_service.py

Objetivo: retrieval por tarea, no memoria duplicada.

Tanda 7 — Backends reales

Donde enchufamos JSON, Mem0 y Qdrant.

Archivos
backends/json/json_memory_store.py
backends/json/json_profile_store.py
backends/json/json_snapshot_store.py
backends/json/json_index_store.py
backends/mem0/mem0_adapter.py
backends/mem0/mem0_memory_store.py
backends/mem0/mem0_profile_store.py
backends/mem0/mem0_snapshot_store.py
backends/qdrant/qdrant_memory_index.py
backends/qdrant/qdrant_search_adapter.py
backends/qdrant/qdrant_collection_manager.py

Objetivo: desacoplar storage del resto.

Tanda 8 — Summaries + Snapshots + Pipelines

Contexto vivo y acumulado.

Archivos
summarize/live_context_summary.py
summarize/recent_context_summary.py
summarize/daily_context_summary.py
summarize/project_context_summary.py
summarize/session_rollup.py
snapshots/live_snapshot_service.py
snapshots/recent_snapshot_service.py
snapshots/daily_snapshot_service.py
snapshots/project_snapshot_service.py
orchestration/ingest_pipeline.py
orchestration/memory_update_pipeline.py
orchestration/snapshot_pipeline.py
orchestration/retrieval_pipeline.py
orchestration/context_pipeline.py

