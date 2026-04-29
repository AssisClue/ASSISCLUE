## Hi there 👋
<img width="640" height="1028" alt="CLUE SUPER EXPLAINED" src="info/CLUE SUPER EXPLAINED.png" />
##
##

# 🧩 ASSISTANT CLUE

> ⚠️ **Status:** Assistant Clue is **not finished yet**.  
> Some files may still be mixed, fallbacks/placeholders may still be triggered, and some blocks are still being cleaned or connected.  
> Ideas, feedback, and improvements are welcome.

---

## 🧠 What is Assistant Clue?

**CLUE** is a local AI assistant project built to connect:

- 🎙️ Voice input
- 🧠 Local AI models
- 🌐 Browser control
- 📚 Memory and knowledge retrieval
- 📄 Document reading
- 🔊 Text-to-speech output
- 🖥️ Screen/system interaction

The goal is simple:

> Build a local assistant that can listen, understand context, use tools, remember useful information, search stored knowledge, and respond naturally.

---

## 🚧 Development Status

This project is in **active development**.

Many core blocks already exist and work, but not every advanced option is fully integrated yet.

Some features are active today.  
Other features are prepared as optional modules for future expansion.

The system is designed to be modular, so each block can be improved, replaced, disabled, or expanded without rebuilding the whole app.

---
## 🧭 HELP System — Quick Read

HELP is ASSISCLUE’s internal manual.
It lets the assistant explain its own folders, files, settings, commands, runtime paths, and app blocks using saved project info.

How to use it:

- 🔊  EXPLAIN MEMORY
- 🔊  EXPLAIN QDRANT + EXPLAIN MORE
- 🔊  EXPLAIN SETTINGS
- 🔊  EXPLAIN MENU + EXPLAIN MORE

For deeper detail after any explain:
- 🔊 EXPLAIN MORE
to get a second deeper explanation, more technical ! 

- 📚 We have a Help Structure Agent (agent_helpers), that creates and updates these HELP files from READMEs, code files, settings, runtime paths, and keywords.
- 📚 Goal: HELP is not just documentation — it is the assistant’s self-map.
#
📍 Location folders:
- Agenthelper (agents)
- app/system_support/HELP/  (help jsons)
 #
--
## ✅ What This App Can Do

Assistant Clue is designed as a local assistant with separate blocks for:

- 🎙️ **Voice input and speech-to-text**
- 🧠 **Local LLM responses**
- 🌐 **Browser automation**
- 📚 **Knowledge library and document reading**
- 🧩 **Memory and retrieval**
- 🗂️ **Qdrant vector database support**
- 🔊 **Text-to-speech output**
- 🖥️ **Screen capture and system interaction**
- 👁️ **Optional OCR tools**
- 📄 **Optional advanced document parsing**
- 🧠 **Optional advanced memory modules**

---

## 🧱 Why Modular?

Assistant Clue is built in blocks.

That means one part can fail, restart, or be replaced without destroying the whole system.

Example:

- Memory can use advanced retrieval with Qdrant.
- If Qdrant is disabled, the app can still use simpler fallback memory.
- Voice, browser, memory, documents, and LLM logic are separated.
- Heavy blocks can be turned on only when needed.

This makes the assistant easier to debug, easier to upgrade, and better for local machines.

---

## ⚙️ Simple Install — Windows

## 1. Create the main project folder

Open **PowerShell** and create the project root:

```powershell
mkdir C:\AI\ASSISCLUE
cd C:\AI\ASSISCLUE
git clone https://github.com/AssisClue/ASSISCLUE.git
```

---

## 2. Create the virtual environment

Inside `ASSISCLUE`, create the venv:

```powershell
python -m venv .venv
```

---

## 3. Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell shows a permission error, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```
---

## 4. Install dependencies

With the venv activated:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Run the app

Open in your browser:

```text
http://127.0.0.1:8000
```

--

---

## 📁 Expected Project Structure

```text
ASSISCLUE/
│
├── app/
├── info/
├── runtime/
├── scripts/
├── requirements.txt
└── .venv/
```

### Folder meaning
- `app/` — main application code
- `info/` — all information files from the app
- `runtime/` — temporary states, logs, generated files, outputs
- `scripts/` — helper scripts, tests, startup tools
- `requirements.txt` — Python dependencies
- `.venv/` — local Python virtual environment

---

## 🧪 Notes

This project is experimental but functional in parts.

The current goal is to keep improving the assistant block by block until it becomes a clean local AI system that can:

> listen, understand, remember, use tools, read files, control browser actions, and answer with voice or text.



