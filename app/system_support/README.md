Ya revise app/system_support/ (ignoro to_integrate/ como pediste).

Mapa (quien usa que)

scripts/start_main_stack.py + scripts/stop_main_stack.py + app/ui_local/app.py + app/bootstrap.py + app/spoken_queries/runners/simple_question_runner.py -> app/system_support/system_runtime_state.py -> runtime/state/system_runtime.json

app/main.py -> app/system_support/llm_runtime_state.py
app/main.py + app/ui_local/screenshots_panel.py -> app/system_support/runtime_files.py
app/main.py -> app/system_support/runtime_jsonl.py
runtime_files.py + runtime_jsonl.py -> text_cleaning.py / time_utils.py


Que hace cada archivo (quick)

app/system_support/system_runtime_state.py: “dueño” del estado del sistema (modo/persona/pids) en system_runtime.json + play loop state.

app/system_support/runtime_files.py: leer/escribir .json de runtime + armar payload {text, ts} con texto normalizado.

app/system_support/runtime_jsonl.py: escribir/leer .jsonl (listas de eventos) + armar items de chat history con timestamps “bonitos”.

app/system_support/llm_runtime_state.py: guarda/carga estado del LLM (proveedor/modelo/ok/error) para runtime/UI.

app/system_support/text_cleaning.py: limpia texto (espacios, signos) y repara “texto roto” tipo QuÃ©.

app/system_support/time_utils.py: convierte ts a hora/fecha legible.

app/system_support/__init__.py: solo re-exporta helpers (comodidad). No vi que nadie lo importe directo ahora mismo.
Imports que no concuerdan

En esta carpeta ya no existe live_settings_state.py (bien: ahora todo va por system_runtime.json)
