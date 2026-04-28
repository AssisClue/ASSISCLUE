app/
├── knowledge_library/
│   └── workspace_marks/
│       ├── __init__.py                 → exporta el bloque
│       ├── marks_store.py              → guarda/carga marked_items.json
│       ├── marks_service.py            → lógica de marcar, desmarcar, listar, actualizar estado
│       └── marks_types.py              → estructura del mark

├── ui_local/
│   └── library_ui/
│       ├── workspace/
│       │   ├── app_workspace.py        → levanta la página workspace
│       │   ├── routes_workspace.py     → rutas del workspace
│       │   ├── services_workspace.py   → trae marks y dispara acciones
│       │   ├── templates/
│       │   │   ├── workspace_home.html → pantalla principal del workspace
│       │   │   └── partials/
│       │   │       ├── workspace_section.html  → bloque por sección
│       │   │       └── workspace_item_row.html → fila de cada item marcado
│       │   └── static/
│       │       └── css/
│       │           └── workspace.css   → estilos del workspace
│       │
│       └── ... UI actual ...

runtime/
└── knowledge_library/
    └── workspace/
        └── marked_items.json           → lista real de items marcados


        MARKED ITEMS DATA

En simple
mark_id → id del mark
source_type → de dónde vino
section → en qué sección mostrarlo
file_name/path/extension → identificarlo bien
item_id → si ya existe en library_map
root_name → root conocida
created_at/updated_at → cuándo se marcó
exists → si sigue existiendo
sha1/size_bytes → validar archivo
status → estado general
summary_ready/index_ready/promoted → progreso real
notes/tags → detalle extra
last_error → si algo falló

####
mark_id
source_type
section
file_name
path
extension
item_id
root_name
created_at
updated_at
exists
sha1
size_bytes
status
summary_ready
index_ready
promoted
notes
tags
last_error
#####
