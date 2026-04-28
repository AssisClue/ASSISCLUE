# Administrative Commands - Usage Notes

## Qué hace esta etapa

Esta etapa conecta el catálogo administrativo al `administrative_listener`, pero solo en modo **detección**.

Eso significa:

- el listener ya reconoce comandos administrativos
- los marca en metadata del `live_moment`
- agrega hints de routing
- separa comandos browser vs no-browser
- todavía NO ejecuta acciones

## Por qué así

El `administrative_listener` hoy es un listener tranquilo.

Su rol actual es:
- leer transcript
- formar párrafo
- decidir si hay presente útil
- escribir `live_moment`

No conviene en esta etapa convertirlo en ejecutor directo.

## Qué metadata agrega

Si detecta un comando, el live moment guarda:

- `administrative_command`
- `has_administrative_command`
- `administrative_action_name`
- `administrative_is_browser_command`
- `administrative_routing_hint`
- `listener_execution_policy = detect_only_no_execution`

## Comandos browser actuales

Los comandos browser administrativos definidos son:

- `open_browser`
- `open_url`
- `look_for`
- `browser_screenshot`

## Qué significa routing_hint

Es solo una pista para la siguiente etapa.

Ejemplos:

### `browser_screenshot`
```json
{
  "route_family": "display_actions",
  "target_runner": "display_actions",
  "handler_key": "browser_screenshot"
}