# live_listeners/shared

Bloque compartido para todos los listeners que leen el transcript sagrado.

## Qué contiene

### transcript_reader.py
Lee `runtime/sacred/live_transcript_history.jsonl` desde el cursor del listener.
No borra nada.
No consume destruyendo.
Solo lee lo nuevo.

### cursor_store.py
Lee y guarda cursores.
Cada listener debe tener su propio cursor.

Formato base:
- `byte_offset`
- `last_event_id`
- `updated_at`

### listener_record_utils.py
Helpers simples para trabajar con records del transcript:
- sacar text
- sacar event_id
- validar record mínimo

### listener_paths.py
Centraliza paths de runtime:
- transcript history
- transcript latest
- live moment history
- cursores
- status

## Regla principal

Todos los listeners leen el mismo transcript.
Ninguno lo modifica.

Cada listener:
- tiene su propio cursor
- lee a su propio ritmo
- no pisa a los demás

## Importante

El transcript:
- es append-only
- no es cola destructiva
- no se borra al leer

La rotación debe pensarse por sesión, no por silencios ni microcortes.