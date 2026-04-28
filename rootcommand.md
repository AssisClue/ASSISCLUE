
--------------------------
POWER SHELL COMMANDS :
--------------------------
--------------------------
Start and Stop:
--------------------------
powershell -ExecutionPolicy Bypass -File .\scripts\start_main_stack.py

powershell -ExecutionPolicy Bypass -File .\scripts\stop_main_stack.py


--------------------------
WEB UI : 
--------------------------
uvicorn app.ui_local.app:app --host 127.0.0.1 --port 8000 --reload  
http://127.0.0.1:8000

--------------------------
WEB UI LIBRARY : 
--------------------------

uvicorn app.ui_local.library_ui.appdocs:app --host 127.0.0.1 --port 8001 --reload  
http://127.0.0.1:8001

--------------------------


--------------------------
Ejecutar light runtime clean :
--------------------------
powershell -ExecutionPolicy Bypass -File .\scripts\clean_all_lightrun.ps1

--------------------------

