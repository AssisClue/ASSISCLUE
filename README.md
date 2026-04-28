## Hi there 👋
<img width="640" height="1028" alt="CLUE SUPER EXPLAINED" src="https://github.com/user-attachments/assets/0dfa540a-5014-4e36-b2ce-413f174aea67" />


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
# 🗂️ INSTAINT Root Folders — Quick Explanation
---

---# 🗂️ INSTAINT APP — MAIN APP FOLDER 

## 🧠 `/INSTAINT/APP`

Main app code.  
Keeps the system modular: input, listeners, routing, memory, tools, UI, LLM, and voice output stay separated.  
Important: the real app stack is mostly started from `/INSTAINT/scripts/`.

---

## 🧩 `/APP/capabilities`

List of allowed app powers/actions.  
Used when the assistant needs to know if a command maps to a real supported action.  
Not for normal chat.

---

## 🧠 `/APP/context_memory`

Main long-term context and memory engine.  
Handles memory storage, retrieval, search, and context building before responses.  
Different from `moment_memory`, which is only a fast live snapshot helper.

---

## 📝 `/APP/context_memory/user_spaces`

Manual editable memory area.  
Used for notes, rules, prompts, and help files controlled by the user.  
Important for custom user memory spaces.

---

## 🖥️ `/APP/display_actions`

Runs display/screen actions after routing.  
Used for screenshots and screen analysis.  
It does not decide actions; it only executes them.

---

## 🎙️ `/APP/inputfeed_to_text`

Turns live audio into text.  
Writes the sacred transcript that listeners read.  
Moonshine STT lives inside `providers/moonshine/`.

---

## 📚 `/APP/knowledge_library`

Handles local files and documents.  
Can scan, read, summarize, chunk, index, and prepare useful knowledge.  
This is a library system, not the main memory brain.

---

## 👂 `/APP/live_listeners`

Reads the sacred transcript without deleting it.  
Each listener has its own cursor and job.  
Main idea: one transcript, many readers.

---

## ⚡ `/APP/live_listeners/primary_listener`

Fast listener.  
Detects wakewords, clear commands, and short questions.  
It does not answer or execute; it only emits clean events.

---

## 🧭 `/APP/live_listeners/administrative_listener`

Calmer listener.  
Groups transcript records into present-moment paragraphs.  
Can create live moments and detect admin/browser commands.

---

## 🧩 `/APP/live_listeners/moment_memory`

Fast live context snapshot helper.  
Reads live moments and writes quick context/world-state snapshots.  
Not the full memory engine.

---

## 🤖 `/APP/llm`

Central place for LLM calls.  
Handles Ollama text/vision, prompts, formatting, and model access.  
Other blocks should call this instead of talking to Ollama directly.

---

## 🧰 `/APP/mcp`

Tool doorway for the app.  
Exposes memory, router, browser, display, and other app abilities as clean tools.  
It does not replace the original systems.

---

## 📤 `/APP/output`

Small output-shape helpers.  
Used for text, image, notification, and UI output formats.  
Actual voice output lives in `speech_out`.

---

## 🎭 `/APP/personas`

Assistant profile/personality definitions.  
Controls style, tone, and active assistant identity.  
It does not route commands or run tools.

---

## 🚦 `/APP/router_dispatch`

Traffic controller.  
Receives listener events and sends them to the correct lane: response, action, or ignore.  
It routes; it does not answer or execute.

---

## 🗃️ `/APP/runtime`

Small app-side runtime storage.  
Do not confuse it with `/INSTAINT/runtime/`, which contains the main live files, transcript, queues, status, and memory.

---

## ⚙️ `/APP/services`

Shared technical services.  
Handles things like app status, modes, settings summaries, audio helpers, and coordination bridges.  
Many blocks depend on this folder.

---

## 🎛️ `/APP/settings`

App knobs and defaults.  
Controls audio, LLM, TTS, modes, and environment-based settings.  
Good place for config, not feature logic.

---

## 🔊 `/APP/speech_out`

Final voice output block.  
Takes final text, sends it to TTS, queues speech, and plays audio.  
Kokoro belongs here.

---

## 🗣️ `/APP/spoken_queries`

Handles routed spoken questions.  
Can choose simple answer, memory answer, direct LLM answer, or refusal.  
It does not read the transcript directly.

---

## 🧱 `/APP/system_support`

Shared system glue.  
Handles runtime files, JSONL logs, state, text cleaning, and common helpers.  
Very important foundation folder.

---

## 🧠 `/APP/system_support/commands`

Command brain.  
Turns phrases like “add note buy milk” into structured commands with action, target, payload, and safety info.  
Command catalogs live here.

---

## 🧰 `/APP/tools`

Small local helper tools.  
Includes file reading, note writing, summaries, tasks, and simple web wrappers.  
Bigger tool access is mostly through `mcp`.

---

## 🖼️ `/APP/ui_local`

Local web UI.  
Shows chat, memory status, modes, persona, screenshots, settings, and tasks.  
UI should display/control the app, not hold all business logic.

---

## 📚 `/APP/ui_local/library_ui`

Human-facing UI for the knowledge library.  
Lets users view files, previews, summaries, indexing, and promotion actions.  
Backend logic stays in `knowledge_library`.

---

## 🌐 `/APP/web_tools`

Browser automation block.  
Uses Playwright to open pages, search, click, type, read text, and take browser screenshots.  
This is browser automation, not desktop OCR.

---

# ⚡ Quick Flow

🎙️ inputfeed_to_text
→ writes /runtime/sacred/live_transcript_history.jsonl

👂 live_listeners
→ primary_listener = fast commands/questions
→ administrative_listener = live moments/admin commands
→ moment_memory = quick context snapshots

🚦 router_dispatch
→ sends events to response or action lanes

🧠 context_memory / knowledge_library
→ memory, retrieval, documents, saved knowledge

🤖 llm
→ creates the final answer

🔊 speech_out
→ speaks the final response

##
## 🕓 `/INSTAINT/runtime`

Live working state of the app.

This is where the system writes transcripts, queues, memory files, screenshots, saved browser text, TTS files, status JSONs, and debug traces.
---
## 🚀 `/INSTAINT/scripts`

Start, stop, test, and utility scripts.
---
## ℹ️ `/INSTAINT/info`
Project explanation and human-readable notes.

This folder is for documentation, maps, plans, architecture notes, setup explanations, and helper files that explain how the system works.
##
##
EXTENDED EXPLANATION>
INSTAINT\info\FOLDER_EXPLANATION.md
##
##
Requirements
Install the main dependencies:

pip install -r requirements.txt
##
##Optionals:##
##
<img width="640" height="420" alt="opt Requirments detail" src="https://github.com/user-attachments/assets/324821ce-81ae-41fd-9c4b-5e371ed221c8" />
