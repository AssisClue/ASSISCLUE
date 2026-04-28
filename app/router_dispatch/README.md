# router_dispatch

## Objetivo

Recibir eventos persistidos por los listeners y repartirlos al carril correcto.

El router:

- no ejecuta acciones
- no usa memoria
- no decide contenido
- no responde preguntas
- no piensa más de la cuenta

Solo decide:

- action_queue
- response_queue
- ignore

## Entrada

Lee desde:

runtime/queues/router_dispatch/router_input_queue.jsonl

## Salidas

Escribe en:

- runtime/queues/router_dispatch/action_queue.jsonl
- runtime/queues/router_dispatch/response_queue.jsonl

## Reglas actuales

- `primary_command` con acción conocida de display -> `action_queue`
- `primary_quick_question` -> `response_queue`
- `primary_wakeword_only` -> `ignore`
- desconocido -> `ignore`

## Archivos

- `router_service.py`  
  loop principal del router

- `route_rules.py`  
  lógica pura de routing

- `route_event_builder.py`  
  arma el evento enrutado de salida

- `schemas/`  
  shapes mínimos de entrada/salida

## Status

Escribe:

runtime/status/router_dispatch/router_status.json

Campos base:

- `ok`
- `state`
- `updated_at`
- `last_event_id`
- `last_processed_line_number`
