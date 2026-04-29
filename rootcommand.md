
--------------------------
POWER SHELL COMMANDS :
--------------------------
--------------------------
Start and Stop:
--------------------------
python .\scripts\start_main_stack.py

python .\scripts\stop_main_stack.py

--------------------------
WEB UI : 
--------------------------
THE STARTER RUNs THIS WEB INTERFACE 
LEGACY / DEBUG ONLY - not official startup:
uvicorn app.ui_local.app:app --host 127.0.0.1 --port 8000 --reload  
http://127.0.0.1:8000

--------------------------
WEB UI LIBRARY : 
--------------------------
THE STARTER RUNs THIS WEB INTERFACE
LEGACY / DEBUG ONLY - not official startup:
uvicorn app.ui_local.library_ui.appdocs:app --host 127.0.0.1 --port 8002 --reload  
http://127.0.0.1:8002

--------------------------


--------------------------
Ejecutar light runtime clean :
--------------------------
powershell -ExecutionPolicy Bypass -File .\scripts\clean_all_lightrun.ps1

--------------------------

