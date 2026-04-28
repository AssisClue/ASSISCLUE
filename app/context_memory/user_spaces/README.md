# user_spaces

Este sub-bloque guarda **memoria manual/fija editable** (prompts, rules, notes, ideas).

## Que es

- Un store simple (JSON) con items creados a mano.
- Items consultables por `space_id` (ej: `prompts`, `rules`, `notes`).
- Devuelve resultados como `MemoryItem` (para integrarse despues con `ContextMemoryService`).

## Que NO es

- No reemplaza la memoria inferida (la que se genera del uso del sistema).
- No hace ingestion automatica, promotion, ranking fino, ni backends avanzados.
- No lee carpetas “al azar”: solo lee `runtime/memory/user_spaces/*.json`.

## Runtime

- `runtime/memory/user_spaces/<space_id>.json`

Cada archivo es una lista de items:

```json
[
  {
    "item_id": "usit_...",
    "space_id": "prompts",
    "title": "Cook profile",
    "text": "You are COOK. Always answer with recipes...",
    "tags": ["cook"],
    "ts": 1712345678.9,
    "metadata": {"pinned": true}
  }
]
```

## Convencion de sources

- `user_spaces.prompts`
- `user_spaces.rules`
- `user_spaces.notes`

