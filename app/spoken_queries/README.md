# spoken_queries

## Objetivo

Procesar preguntas habladas simples ya enrutadas por `router_dispatch`.

Esta rama:

- no ejecuta acciones de PC
- no toma screenshots
- no decide routing
- no lee transcript sagrado directo
- no usa memoria automáticamente
- decide entre:
  - respuesta simple
  - requiere memoria
  - rechazo simple

## Entrada

Lee desde:

`runtime/queues/router_dispatch/response_queue.jsonl`

Solo procesa eventos con:

- `target_runner = "spoken_queries"`

## Salidas

Escribe en:

`runtime/queues/spoken_queries/spoken_query_results.jsonl`

## Flujo

response_queue.jsonl
-> spoken_query_router.py
-> matchers
-> runner elegido
-> spoken_query_results.jsonl

## Regla importante

`use_memory` es flag.

No cambia la ruta.
La ruta sigue siendo `spoken_queries`.
Lo que cambia es qué runner responde.

## Estado actual

- preguntas simples: sí
- preguntas con memoria: placeholder controlado
- rechazos simples: sí

## Nota

La rama queda lista para crecer sin romper el carril:

- luego podés conectar memoria real
- luego podés conectar LLM
- luego podés meter contexto

Pero hoy queda sana, simple y testeable.








-------------

