## Hi there 👋
<img width="640" height="1028" alt="CLUE SUPER EXPLAINED" src="info/CLUE SUPER EXPLAINED.png" />


# ASSISTANT CLUE
# ASSISTANT IS NOT FINISHED , FILES MIGHT BE MIXED UP , FALLBACKS AND PLACEHOLDERS STILL COULD BE HIT , IDEAS ARE WELCOME ! #

## IM CREATIG A HELP THAT WILL BE A QUICK RESPONSE FOR EACH SECTION AND BLOCK AND ANYTHING THAT IS INSIDE THE ASSISNT 
Using "explain" as command and follow with any Assistant reference will trigger a info about that 
---
Example: explain prompts? explain notes ? explain web browser ? explain memory ? .... 

##
CLUE is a local AI assistant project built to connect voice, browser control, memory, document reading, and local AI models into one modular system.

The goal is simple: an assistant that can listen, understand context, use tools, remember useful information, search through stored knowledge, and respond in a natural way.

This project is still in active development. Many core blocks already exist and work, but not every advanced option is fully integrated yet. Some features are active now, while others are prepared as optional modules for future expansion.

---

## What This App Can Do

CLUE is designed as a local assistant with separate blocks for:

- Voice input and speech-to-text
- Local LLM responses
- Browser automation
- Knowledge library and document reading
- Memory and retrieval with Qdrant
- Text-to-speech output
- Screen capture and system interaction
- Optional advanced memory, OCR, and document parsing tools

The app is built in a modular way, so each block can be improved, replaced, disabled, or expanded without rebuilding the whole system.

##
##
## Install simple

### 
1. Crear la carpeta principal

Abrí PowerShell y creá el root del proyecto:


powershell

mkdir C:\AI\ASSISCLUE
cd C:\AI\ASSISCLUE
##
2. Crear el entorno virtual

Dentro de ASSISCLUE, creá el venv:

python -m venv .venv
##
3. Activar el entorno virtual
.\.venv\Scripts\Activate.ps1

Si aparece un error de permisos en PowerShell, ejecutá una vez:

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Después activalo otra vez:

.\.venv\Scripts\Activate.ps1
##
4. Instalar dependencias

Con el venv activado:

pip install --upgrade pip
##
pip install -r requirements.txt
