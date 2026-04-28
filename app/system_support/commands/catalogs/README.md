# Administrative Command Catalogs

## Qué son

Estos archivos contienen los catálogos de comandos que puede consumir el sistema para listeners tranquilos / administrativos.

La idea es que los listeners **lean** estos catálogos, pero no sean dueños de ellos.

## Regla de arquitectura

- `administrative_listener` puede consumir estos catálogos
- `primary_listener` también podría consumirlos más adelante si hiciera falta
- pero los catálogos viven en `app/system_support/commands/catalogs/`
- porque el dueño conceptual de los comandos es el bloque `system_support/commands`

## Archivos

### `administrative_core_commands.json`
Comandos administrativos / generales / no-web.

Incluye ejemplos como:
- screenshot display
- screenshot analysis
- stop talking
- runtime status
- modes
- chat control
- persona control

### `administrative_web_commands.json`
Comandos administrativos relacionados a browser / webautomation.

Incluye:
- `open_browser`
- `open_url`
- `look_for`
- `browser_screenshot`

## Separación importante

### Screenshot display
Comandos como:
- `take screenshot`
- `capture screenshot`

siguen siendo del bloque display / screen capture.

### Screenshot browser
Comandos como:
- `browser screenshot`
- `website screenshot`

apuntan al bloque webautomation.

No se debe usar alias ambiguo como solo `screenshot` para browser.

## Formato esperado

Cada archivo contiene una lista de secciones.

Cada sección tiene:
- `section`
- `commands`

Cada command tiene, como mínimo:
- `command_id`
- `action_name`
- `requires_wakeword`
- `allow_without_wakeword`
- `aliases`

Y opcionalmente:
- `capability_id`

## Ejemplo de command

```json
{
  "command_id": "browser_screenshot",
  "action_name": "browser_screenshot",
  "requires_wakeword": false,
  "allow_without_wakeword": true,
  "aliases": [
    "browser screenshot",
    "take browser screenshot"
  ]
}