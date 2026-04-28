# display_actions

## Objetivo

Ejecutar acciones de pantalla ya enrutadas por `router_dispatch`.

Esta rama:

- ejecuta acciones de display
- produce un resultado estable
- define `speech_text`
- no decide routing
- no lee transcript sagrado
- no mezcla preguntas habladas

## Entrada

Lee desde:

`runtime/queues/router_dispatch/action_queue.jsonl`

Solo procesa eventos con:

- `target_runner = "display_actions"`

## Salidas

Escribe en:

- `runtime/display_actions/results/display_action_results.jsonl`

Y guarda screenshots en:

- `runtime/display_actions/screenshots/`

## Acciones actuales

- `take_screenshot`
- `take_full_screenshot`
- `analyze_screen`
- `analyze_last_screenshot`

## Reglas actuales

### take_screenshot
- crea screenshot
- guarda resultado
- genera `speech_text = "Screenshot captured."`

### take_full_screenshot
- crea screenshot full
- guarda resultado
- genera `speech_text = "Full screenshot captured."`

### analyze_screen
- si hay screenshot reciente, usa esa
- si no hay, captura una nueva
- analiza
- genera respuesta corta para speech

### analyze_last_screenshot
- usa la última screenshot existente
- si no existe, falla con:
  - `ok = false`
  - `error_code = "no_previous_screenshot"`
  - `speech_text = "No previous screenshot available."`

## Nota importante

La captura y análisis real todavía pueden estar en placeholder.
La estructura ya queda lista para reemplazar backend después sin romper el carril.

## Status

Escribe:

`runtime/display_actions/status/display_action_runner_status.json`
