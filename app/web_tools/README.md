# WEB TOOLS / PLAYWRIGHT / MCP WEB AUTOMATION

## Qué es este bloque

Este bloque agrega automatización web local al asistente usando **Playwright** como base real de navegador.

No es un buscador mágico.
No es OCR.
No es desktop automation de Windows.
No es Google automation como base.

Es un bloque para:

- abrir páginas
- leer título
- extraer texto visible
- guardar HTML
- guardar TXT
- sacar screenshots
- escribir en inputs
- clickear selectores
- presionar teclas
- correr búsquedas simples en DuckDuckGo
- mantener sesiones persistentes por proceso
- exponer todo eso por MCP

---

# Objetivo del bloque

La idea es tener una base web seria, separada y reutilizable.

Este bloque sirve para:

- tools internas del sistema
- tools MCP
- workflows automáticos de páginas web
- debug
- pruebas
- futuras integraciones con agentes
- futura conexión más fuerte con MCP externo

La decisión de diseño fue:

- **Playwright como base**
- **DuckDuckGo como search provider simple**
- **Google NO como base automática**
- **sesiones persistentes por proceso**
- **MCP como capa de acceso**
- **runtime propio para páginas y screenshots**

---

# Qué software / librerías incluye

## Base principal
- `playwright`
- browser instalado: `chromium`

## Complementos usados en este bloque
- `beautifulsoup4`
- `lxml`

## Para qué se usan
- **Playwright**: abrir y controlar navegador
- **BeautifulSoup + lxml**: limpiar HTML y extraer texto visible

---

# Qué NO incluye este bloque

Este bloque no hace todavía:

- OCR
- visión
- Google search automático como base
- browser-use
- Selenium
- desktop automation Windows
- persistencia de sesiones entre procesos
- login/profile persistente real
- navegación multi-tab compleja
- provider API externo de búsqueda

---

# Estructura principal

## Implementación real
```text
app/web_tools/
  __init__.py
  README.md
  config.py
  models.py

  browser/
    __init__.py
    playwright_manager.py
    navigation.py
    screenshots.py
    extractors.py

  providers/
    __init__.py
    search_provider_base.py
    duckduckgo_provider.py
    google_manual_provider.py

  runtime/
    __init__.py
    web_runtime_paths.py


    app/mcp/webautomation/
  __init__.py

  adapters/
    __init__.py
    webautomation_adapter.py

  services/
    __init__.py
    webautomation_mcp_service.py

  tools/
    __init__.py
    webautomation_tools.py


    1. app/web_tools/browser/*

Acá vive Playwright de verdad.

playwright_manager.py

Maneja:

creación de browser
creación de context
creación de page
sesiones persistentes por session_id
navigation.py

Acciones base:

abrir URL
click
type
press key
esperar
screenshots.py

Captura:

screenshot de página
metadata de screenshot
tamaño de viewport
tamaño de archivo
extractors.py

Extrae:

título
html
texto visible
guarda html
guarda txt
2. app/web_tools/providers/*

Define rutas de búsqueda.

duckduckgo_provider.py

Provider simple de búsqueda web sin pelear contra captcha de Google.

google_manual_provider.py

Ruta manual / semi-manual.
No se usa como base automática del bloque.

Regla de diseño

provider de búsqueda != motor de browser

O sea:

Playwright controla navegador
provider decide dónde buscar
3. app/mcp/webautomation/*

Es el puente MCP.

adapters/webautomation_adapter.py

Traduce tools MCP a llamadas reales del bloque web_tools.

services/webautomation_mcp_service.py

Normaliza:

inputs
errores
MCPToolResult
mensajes
tool_name
tools/webautomation_tools.py

Registra todas las tools en el registry MCP.

Runtime que usa este bloque
Carpetas
runtime/web/pages/
runtime/web/screenshots/
Qué guarda
runtime/web/pages/
archivos .html
archivos .txt
runtime/web/screenshots/
archivos .png
Nombres de archivo

Usan prefijo + timestamp, por ejemplo:

example_domain_2026-04-18__20-27-36.html
web_capture_2026-04-18__20-27-37.png
web_session_capture_2026-04-18__20-56-21.png
Qué tools MCP existen hoy
Tools one-shot

Estas abren/usan/cerran dentro de una sola llamada.

web_open_url

Abre una URL.

input

{
  "url": "https://example.com"
}
web_get_title

Abre una URL y devuelve título.

input

{
  "url": "https://example.com"
}
web_extract_text

Abre una URL y devuelve texto visible.

input

{
  "url": "https://example.com"
}
web_capture_page

Abre una URL y guarda screenshot.

input

{
  "url": "https://example.com",
  "full_page": true
}
web_save_page_html

Abre una URL y guarda HTML.

input

{
  "url": "https://example.com",
  "name_prefix": "example_domain"
}
web_save_page_text

Abre una URL y guarda texto visible.

input

{
  "url": "https://example.com",
  "name_prefix": "example_domain"
}
web_search_duckduckgo

Hace búsqueda simple usando DuckDuckGo.

input

{
  "query": "playwright python"
}
web_click

Abre URL y clickea selector.

input

{
  "url": "https://duckduckgo.com/",
  "selector": "input[name=q]",
  "wait_after_ms": 0
}
web_type

Abre URL y escribe en selector.

input

{
  "url": "https://duckduckgo.com/",
  "selector": "input[name=q]",
  "text": "playwright python",
  "clear_first": true
}
web_press_key

Abre URL y presiona tecla.

input

{
  "url": "https://duckduckgo.com/",
  "key": "Enter",
  "wait_after_ms": 1000
}
web_open_and_capture

Abre URL, espera opcional, guarda screenshot.

input

{
  "url": "https://example.com",
  "full_page": true,
  "wait_after_ms": 500
}
web_type_and_press

Abre URL, escribe, presiona tecla, espera.

input

{
  "url": "https://duckduckgo.com/",
  "selector": "input[name=q]",
  "text": "playwright python",
  "key": "Enter",
  "clear_first": true,
  "wait_after_ms": 1200
}
web_search_and_capture

Busca en DuckDuckGo y guarda screenshot de resultados.

input

{
  "query": "playwright python",
  "full_page": true,
  "wait_after_ms": 1200
}
web_search_and_extract

Busca en DuckDuckGo y devuelve texto visible de resultados.

input

{
  "query": "playwright python",
  "wait_after_ms": 1200
}
Tools de sesión persistente

Estas mantienen una página/browser vivos en memoria dentro del mismo proceso Python.

Muy importante

Estas sesiones NO sobreviven entre procesos distintos.

Si abrís una sesión en:

un python -c
y después corrés otro python -c

esa sesión ya no existe.

La persistencia actual es:

sí dentro del mismo proceso
no entre procesos
Tools de sesión disponibles
web_session_start

Crea sesión persistente y opcionalmente abre URL.

input

{
  "url": "https://duckduckgo.com/"
}

salida típica

{
  "ok": true,
  "session_id": "web_abc123...",
  "url": "https://duckduckgo.com/",
  "title": "DuckDuckGo - Protection. Privacy. Peace of mind."
}
web_session_stop

Cierra una sesión.

input

{
  "session_id": "web_abc123..."
}
web_session_info

Lee URL y título actuales de una sesión.

input

{
  "session_id": "web_abc123..."
}
web_session_open_url

Abre URL dentro de la sesión.

input

{
  "session_id": "web_abc123...",
  "url": "https://example.com"
}
web_session_type

Escribe dentro de la sesión.

input

{
  "session_id": "web_abc123...",
  "selector": "input[name=q]",
  "text": "persistent session test",
  "clear_first": true
}
web_session_click

Click dentro de la sesión.

input

{
  "session_id": "web_abc123...",
  "selector": "button",
  "wait_after_ms": 1000
}
web_session_press_key

Presiona tecla dentro de la sesión.

input

{
  "session_id": "web_abc123...",
  "key": "Enter",
  "wait_after_ms": 1200
}
web_session_extract_text

Extrae texto visible de la página actual de la sesión.

input

{
  "session_id": "web_abc123..."
}
web_session_capture_page

Guarda screenshot de la página actual de la sesión.

input

{
  "session_id": "web_abc123...",
  "full_page": true
}
web_session_list

Lista sesiones activas del proceso actual.

input

{}
web_session_stop_all

Cierra todas las sesiones activas del proceso actual.

input

{}
Formato general de salida

La capa MCP devuelve MCPToolResult.

Forma general
{
  "ok": true,
  "tool_name": "web_get_title",
  "message": "Page title loaded.",
  "data": {},
  "error_code": "",
  "meta": {}
}
Campos importantes
ok: si salió bien o no
tool_name: nombre de la tool MCP
message: mensaje corto
data: payload real
error_code: error corto si hubo problema
meta: info adicional de excepción, etc.
Qué formatos acepta este bloque
URLs

Acepta strings tipo:

https://example.com
https://duckduckgo.com/
Selectores

Hoy usa selectores Playwright/CSS simples.
Ejemplos buenos:

input[name=q]
textarea[name=q]
button[type=submit]
Keys

Ejemplos:

Enter
Tab
Escape
Texto

Cualquier string.

Flags booleanos

Ejemplos:

full_page: true
clear_first: true
Tiempos

En milisegundos:

wait_after_ms: 1200
Cómo se usa hoy
Uso rápido desde script
from app.mcp.server import create_mcp_server

server = create_mcp_server()
result = server.call_tool("web_get_title", url="https://example.com")
print(result)
Uso con sesión persistente
server = create_mcp_server()

start = server.call_tool("web_session_start", url="https://duckduckgo.com/")
sid = start.data["session_id"]

server.call_tool("web_session_type", session_id=sid, selector="input[name=q]", text="playwright python")
server.call_tool("web_session_press_key", session_id=sid, key="Enter", wait_after_ms=1200)
server.call_tool("web_session_capture_page", session_id=sid, full_page=True)
server.call_tool("web_session_stop", session_id=sid)
Tests y validación
Smoke test
python scripts\webautomation_smoke_test.py
Pytest
pytest app\mcp\tests\test_webautomation_tools.py -q
Estado actual validado

Este bloque ya fue validado con:

smoke test real
screenshots generadas
búsqueda DuckDuckGo
sesión persistente por proceso
pytest pasando
Limitaciones actuales
1. No usar Google como base automática

Se probó Google web automatizado y puede disparar captcha.
Por eso la base actual de search simple quedó en DuckDuckGo.

2. Persistencia solo por proceso

Las sesiones no sobreviven entre distintos procesos Python.

3. Extracción de texto todavía simple

Se limpió bastante, pero sigue pudiendo traer:

menús
filtros
basura visual
texto no principal
4. No hay login persistente serio todavía

No hay storage state/profile/session disk estable todavía.

5. No hay multi-tab / flujos complejos todavía

La base actual apunta a:

una page
un context
una sesión simple
Cuándo usar este bloque

Usalo cuando necesites:

leer una página
sacar screenshot
guardar HTML/TXT
probar un flujo simple
hacer una búsqueda simple
automatizar un form/input
mantener una sesión viva dentro del proceso actual
Cuándo NO usar este bloque

No lo uses para:

OCR
analizar imágenes
controlar apps Windows
automatización de escritorio
Google Search automático como motor principal
workflows que necesiten persistir entre procesos sin una capa extra
Siguiente evolución posible

Más adelante este bloque puede crecer hacia:

storage state / auth real
sesiones persistentes en disco
provider extra además de DuckDuckGo
mejor extracción de contenido principal
bridge MCP externo real
integración con visión / OCR
acciones web más complejas
Resumen corto
Qué tenemos

Un bloque web local basado en Playwright, usable desde MCP, con lectura, escritura, búsqueda, screenshot y sesiones persistentes por proceso.

Cómo entra

Por app/mcp/webautomation/*

Cómo ejecuta

Por app/web_tools/*

Qué guarda

En runtime/web/pages/ y runtime/web/screenshots/

Qué proveedor usa hoy

DuckDuckGo

Estado

Base funcional, probada y lista para seguir creciendo.


## Si querés guardarlo rápido
```powershell id="renps8"
notepad app\web_tools\README.md