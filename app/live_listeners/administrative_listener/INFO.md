# WEB AUTOMATION + ADMINISTRATIVE LISTENER + MCP
# Estado actual, uso y mapa rápido

## Qué agregamos

Se sumó una nueva línea de trabajo para que el sistema pueda usar browser automation de forma ordenada, sin mezclarlo con screenshot de pantalla normal.

La idea quedó separada en 3 capas:

1. **Web tools / Playwright**
2. **MCP webautomation**
3. **Administrative listener como detector/ejecutor de comandos browser**

Hoy esta parte ya puede:

- abrir una sesión browser
- buscar en DuckDuckGo
- sacar browser screenshot
- detectar comandos browser desde texto assembled
- ejecutar esos comandos desde `administrative_listener`

---

# Distinción importante

## Screenshot normal
Esto sigue siendo otra cosa.

Comandos como:
- `take screenshot`
- `capture screenshot`

siguen apuntando a screenshot de display / pantalla del sistema.

## Browser screenshot
Esto es distinto.

Comandos como:
- `browser screenshot`
- `take browser screenshot`
- `website screenshot`

apuntan al bloque webautomation y sacan screenshot de la página/browser, no del monitor entero.

**Resumen simple:**
- display screenshot = pantalla real
- browser screenshot = página web dentro de Playwright

---

# Qué bloques existen

## 1. Web tools
Base real del navegador.

Ruta principal:
```text
app/web_tools/


Acá vive:

Playwright
navegación
screenshots del browser
extractores
providers de búsqueda
runtime web
Subpartes importantes
app/web_tools/browser/
app/web_tools/providers/
app/web_tools/runtime/
Archivos clave
app/web_tools/browser/playwright_manager.py
app/web_tools/browser/navigation.py
app/web_tools/browser/screenshots.py
app/web_tools/browser/extractors.py
2. MCP webautomation

Es la puerta MCP que expone el browser como tools.

Ruta principal:

app/mcp/webautomation/
Capas
adapters/
services/
tools/
Archivos importantes
app/mcp/webautomation/adapters/webautomation_adapter.py
app/mcp/webautomation/services/webautomation_mcp_service.py
app/mcp/webautomation/tools/webautomation_tools.py
Qué hace

Expone tools como:

abrir URL
extraer texto
guardar HTML/TXT
sacar screenshot
sesiones persistentes browser
escribir / clickear / apretar teclas
3. MCP gateway

Es la puerta interna del app hacia MCP.

Ruta:

app/services/mcp_gateway_service.py
app/services/mcp_gateway_runtime.py
Qué hace

El resto del sistema no debería llamar app.mcp.server directo.
Debería entrar por este gateway.

Acá sumamos métodos para webautomation como:

web_session_start
web_session_list
web_session_info
web_session_open_url
web_session_type
web_session_press_key
web_session_capture_page
web_session_stop
web_session_stop_all
4. Administrative listener

Es el listener tranquilo del sistema. Ya existía como listener de presente/contexto, y ahora además detecta comandos administrativos/browser y puede ejecutarlos.

Ruta:

app/live_listeners/administrative_listener/
Archivos nuevos/importantes de esta etapa
administrative_command_cleaner.py
administrative_command_matcher.py
administrative_command_bridge.py
administrative_command_router.py
administrative_command_runners.py
administrative_command_execution_guard.py
administrative_listener_service.py
administrative_listener_execution_readme.md
Dónde viven los comandos

No quedaron metidos dentro de primary_listener.
Tampoco “pertenecen” a administrative_listener.

El dueño conceptual ahora es:

app/system_support/commands/

Y los catálogos quedaron en:

app/system_support/commands/catalogs/
Archivos de catálogo
administrative_core_commands.json
administrative_web_commands.json
README.md
Loader
app/system_support/commands/command_catalog_loader.py

Esto permite que los listeners consuman los catálogos sin ser dueños de ellos.

Qué comandos web tenemos hoy

Hoy, en la parte browser/administrative, tenemos estos comandos base:

open_browser
open_url
look_for
browser_screenshot

Estos viven en:

app/system_support/commands/catalogs/administrative_web_commands.json
Cómo se detectan hoy

El matcher del administrative listener hoy es simple a propósito:

normaliza texto
compara aliases
acepta match si el alias:
es igual
aparece al inicio
o está contenido en la frase

Eso se hizo así para que frases como:

please open browser now
can you look for playwright python on the web
please take a browser screenshot now

igual matcheen.

No hay NLP complejo ni limpieza sofisticada.
Es un matcher práctico y tolerante.




Cómo se ejecutan hoy
Flujo real
el assembled transcript entra al administrative_listener
arma párrafo
detecta si hay comando administrativo
si lo hay, genera metadata
si la ejecución está habilitada, lo manda al router
el router llama al runner correcto
el runner usa MCP gateway
MCP gateway llama webautomation
webautomation usa Playwright
En cadena
assembled transcript
-> administrative_listener
-> administrative_command_bridge
-> administrative_command_router
-> administrative_command_runners
-> MCPGatewayService
-> MCP webautomation
-> Playwright
Qué ejecuta hoy cada comando
open_browser
si ya hay sesión browser activa en el proceso, la reutiliza
si no hay, crea una nueva
normalmente arranca en about:blank si no se le pasa URL
open_url
usa la sesión browser activa
requiere payload como URL
abre esa URL en la sesión
look_for
usa la sesión browser activa
si no hay, crea una en DuckDuckGo
escribe en input[name=q]
presiona Enter
espera un poco
queda la búsqueda abierta
browser_screenshot
usa el runner browser screenshot ya conectado al bloque webautomation
saca screenshot de la sesión browser actual
si no hay sesión, crea una y captura esa sesión
Qué metadata deja el administrative listener

Cuando detecta un comando, el live_moment guarda metadata como:

administrative_command
has_administrative_command
administrative_action_name
administrative_is_browser_command
administrative_routing_hint
listener_execution_policy
administrative_execution_fingerprint
administrative_execution_guard_allowed
administrative_execution_reason
administrative_execution_result
administrative_execution_ok

O sea:
no solo detecta, también deja trazabilidad de qué entendió y qué intentó ejecutar.

Qué ya probamos y salió bien

Se probó directamente desde administrative_listener_service.process_record(...) que:

open_browser detecta y ejecuta OK
look_for detecta y ejecuta OK
browser_screenshot detecta y ejecuta OK

Y esos resultados quedaron dentro del live_moment con metadata completa.

También antes se validó que el bloque webautomation ya funcionaba por sí solo con:

sesiones persistentes por proceso
screenshot browser
búsqueda DuckDuckGo
tools MCP
tests y smoke tests OK.
Dónde mirar outputs
Screenshots browser
runtime/web/screenshots/
Páginas guardadas
runtime/web/pages/
Live moments del administrative listener

El listener escribe live_moment_history.jsonl como parte de su flujo normal. Eso ya era parte de su función original.

Status del administrative listener

Mira los archivos/runtime que ya use ese listener:

status json
cursor json
sacred/live moment outputs
Cómo usarlo hoy
Opción 1: prueba directa de router

Ejemplos:

from app.live_listeners.administrative_listener.administrative_command_router import route_administrative_command

print(route_administrative_command({
    "action_name": "open_browser",
    "payload_text": "",
    "is_browser_command": True,
}))
print(route_administrative_command({
    "action_name": "look_for",
    "payload_text": "playwright python",
    "is_browser_command": True,
}))
Opción 2: prueba real por administrative listener

Ejemplo:

from app.live_listeners.administrative_listener.administrative_listener_service import AdministrativeListenerService

svc = AdministrativeListenerService()
result = svc.process_record({
    "event_id": "asmb_test_020",
    "ts": 1234567890.0,
    "session_id": "session_test",
    "text": "please open browser now",
})
print(result)

Esto ya ejecuta si la config lo permite.

Config importante

En:

app/live_listeners/administrative_listener/administrative_listener_config.py

se sumaron flags para decidir si ejecuta o no:

ADMINISTRATIVE_EXECUTE_COMMANDS
ADMINISTRATIVE_EXECUTE_BROWSER_COMMANDS

Con eso podés dejar al listener en modo:

solo detectar
o detectar + ejecutar

La base original del administrative listener seguía siendo leer transcript, formar párrafo y escribir live moments. Eso no se perdió; se extendió.

Limitación importante
Persistencia browser

La sesión browser actual es por proceso.

Eso significa:

si probás con python -c separados, cada prueba arranca otro proceso
entonces no comparte la misma sesión
por eso a veces open_browser, look_for y browser_screenshot terminan usando sesiones distintas si los corrés separados

Esto no es un bug del bloque.
Es la forma actual de persistencia.

Para continuidad real:

tiene que vivir dentro del proceso real del sistema corriendo.
Qué no hace todavía

Todavía no está pulido en estas cosas:

payloads con relleno (now, please, of this page now)
validación fuerte de URLs
confirmación para acciones más delicadas
comandos no-browser administrativos completos
persistencia browser entre procesos
limpieza inteligente del lenguaje
prioridad/frecuencia fina para evitar acciones de más
Qué ganamos con esta parte nueva

Ganamos una línea completa nueva del sistema:

catálogos administrativos ordenados
web commands separados
matcher simple y útil
administrative listener entendiendo comandos browser
ejecución real vía MCP + webautomation + Playwright
metadata de trazabilidad
separación clara entre screenshot display y browser screenshot

Resumen corto
Qué es esto

La nueva parte que permite que el sistema use navegador de forma ordenada desde el flujo administrativo.

Dónde vive
comandos: app/system_support/commands/catalogs/
webautomation: app/mcp/webautomation/ y app/web_tools/
ejecución administrativa: app/live_listeners/administrative_listener/
Qué puede hacer hoy
abrir browser
buscar en la web
sacar browser screenshot
dejar todo registrado en metadata del live moment
Qué mirar si algo falla
administrative_listener_service.py
administrative_command_matcher.py
administrative_command_router.py
administrative_command_runners.py
mcp_gateway_service.py
app/mcp/webautomation/*
runtime/web/screenshots/


