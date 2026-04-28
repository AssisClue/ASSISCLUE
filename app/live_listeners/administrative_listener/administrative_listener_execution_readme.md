# Administrative Listener Execution

## Qué cambia en esta etapa

El administrative listener ya no solo detecta comandos.
Ahora también puede ejecutarlos cuando están habilitados por config.

## Política actual

### Habilitación
- `ADMINISTRATIVE_EXECUTE_COMMANDS=1`
- `ADMINISTRATIVE_EXECUTE_BROWSER_COMMANDS=1`

### Dedupe
El listener usa un guard en memoria para no volver a ejecutar el mismo comando exacto de la misma ventana/párrafo dentro del proceso actual.

## Qué ejecuta hoy

### Browser commands
- `open_browser`
- `open_url`
- `look_for`
- `browser_screenshot`

## Qué guarda en metadata

Además del comando detectado, ahora el live moment guarda:

- `administrative_execution_fingerprint`
- `administrative_execution_guard_allowed`
- `administrative_execution_reason`
- `administrative_execution_result`
- `administrative_execution_ok`

## Importante

La persistencia del browser sigue siendo por proceso.
Eso significa que para continuidad real:
- el listener vivo
- el router vivo
- la sesión web viva

deben convivir dentro del mismo proceso del sistema, no en `python -c` separados.