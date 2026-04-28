# moment_memory

Lee principalmente `live_moment_history.jsonl` y arma snapshots simples y rápidos de contexto basado en live moments.

Este bloque NO es el motor de memoria real del sistema.
El motor real vive en `app/context_memory/`.

## Qué hace

- leer live moments nuevos
- mantener una ventana de momentos recientes
- construir resumen corto
- construir world state simple
- escribir snapshots rápidos

## Qué escribe

- `runtime/sacred/context_snapshot.json`
- `runtime/sacred/memory_snapshot.json`
- `runtime/sacred/world_state.json`

## Qué no hace

- no toca el transcript original
- no responde
- no usa LLM en esta etapa base
- no ejecuta acciones
- no hace retrieval/ranking/promotion
- no guarda memoria persistente de largo plazo

## Archivos

### context_runner_service.py
Loop principal.

### context_runner_config.py
Tunables del runner.

### context_window_builder.py
Mantiene ventana de live moments recientes.

### summary_builder.py
Arma resumen simple.

### world_state_builder.py
Arma estado simple del mundo actual.

### memory_snapshot_writer.py
Escribe snapshots y status.

## Regla principal

Mira el río desde afuera.
No reacciona como el primary listener.
No agrupa como el administrative listener.
Construye contexto.
