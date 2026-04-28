# administrative_listener

Es el listener tranquilo del sistema.

Lee el transcript sagrado, arma ventanas de presente, forma un párrafo simple y decide si eso parece:
- `response_candidate`
- `context_only`
- `ignore`

## Qué hace

- leer transcript nuevo
- agrupar records cercanos
- formar un bloque de texto
- filtrar intención presente
- escribir `live_moment_history.jsonl`

## Qué no hace

- no ejecuta acciones
- no responde directo
- no usa LLM
- no toca el transcript original

## Archivos

### administrative_listener_service.py
Loop principal del listener.

### administrative_listener_config.py
Tunables: poll, ventana, mínimos de párrafo.

### moment_window_builder.py
Arma ventana de records recientes.

### paragraph_builder.py
Convierte la ventana en párrafo.

### present_intent_filter.py
Decide si el párrafo merece respuesta, solo contexto o nada.

### live_moment_writer.py
Escribe `runtime/sacred/live_moment_history.jsonl`.

## Regla principal

No reacciona a todo.
Agrupa mejor el presente.