# Administrative Command Execution

## Qué hace esta etapa

Ahora el bloque administrativo ya puede ejecutar browser commands por una ruta controlada.

## Flujo

1. `administrative_listener` detecta comando
2. guarda metadata con `administrative_command`
3. otra capa puede pasar ese objeto a:
   - `route_administrative_command(command)`

## Qué ejecuta hoy

### Browser
- `browser_screenshot`
- `open_browser`
- `open_url`
- `look_for`

## Cómo ejecuta

### `browser_screenshot`
Usa el runner ya existente de display/browser screenshot.

### `open_browser`
- si ya hay sesión web, la reutiliza
- si no hay, crea una nueva

### `open_url`
- usa la primera sesión activa
- si no hay sesión, intenta crear una
- requiere `payload_text` como URL

### `look_for`
- usa la primera sesión activa
- si no hay, crea una en DuckDuckGo
- escribe en `input[name=q]`
- presiona Enter
- espera 1200ms

## Qué NO hace todavía

- no ejecuta comandos no-browser
- no valida URLs complejas
- no limpia payloads raros
- no hace confirmación
- no lo enchufamos todavía al loop final del listener

## Estado

Este bloque ya sirve para:
- probar ejecución administrativa browser
- validar continuidad con sesión persistente
- preparar el dispatch final de comandos administrativos