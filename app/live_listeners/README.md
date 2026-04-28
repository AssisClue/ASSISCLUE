# live_listeners

Este bloque contiene los lectores del transcript sagrado.

## Idea principal

`inputfeed_to_text` escribe.

`live_listeners` leen.

Ningún listener toca ni modifica el transcript original.

## Bloques

### primary_listener
Escucha rápida:
- wakeword
- comando claro
- quick question

### administrative_listener
Lectura más tranquila:
- agrupa records
- arma párrafo
- decide intención presente
- escribe live moments

### moment_memory
Lee preferentemente live moments:
- arma contexto
- resumen
- world state
- snapshots

## Regla más importante

Cada listener tiene su propio cursor.

Nunca compartir cursor.

## Cursores recomendados

- `byte_offset`
- `last_event_id`

## Transcript

El transcript:
- es append-only
- no es cola destructiva
- no se borra al leer
- se rota por sesión, no por silencio

## Filosofía

Un solo writer.
Muchos lectores.
Cada uno a su ritmo.
