# ASSISCLUE APP - FOLDER EXPLANATION

This file gives a quick map of the main `APP` folders. It is for a new user who wants to know where the important parts live before reading all the READMEs.

Main requirements are in the root folder:
- `/ASSISCLUE/requirements.txt`
- `/ASSISCLUE/requirements-linux.txt`
- Moonshine STT is in `/ASSISCLUE/APP/inputfeed_to_text/providers/moonshine/`
- Kokoro TTS is used from `/ASSISCLUE/APP/speech_out/` and configured in `/ASSISCLUE/APP/settings/`

Outside `APP`, also remember:
- `/ASSISCLUE/runtime/sacred/` has the sacred live transcript and live moment files.
- `/ASSISCLUE/runtime/memory/user_spaces/help/helpfolders.md` is important help for user memory spaces.
- `/ASSISCLUE/scripts/start_main_stack.py` and `/ASSISCLUE/scripts/stop_main_stack.py` are important runners for starting and stopping the app stack.

---

## /ASSISCLUE/APP

This is the main app code. It is split into small blocks so voice input, listeners, routing, memory, LLM, tools, UI, and voice output do not all mix together.

Important files:
- `bootstrap.py`
- `config.py`
- `main.py`
- Root requirements are outside this folder.

Important note: `main.py` looks like a demo/entry test path in this project. The real running stack is mostly controlled by the scripts in `/ASSISCLUE/scripts/`.

---

## /ASSISCLUE/APP/capabilities

This is the app's list of allowed "powers", like screenshot actions or status actions. It helps the system know if a spoken command matches a real action.

Important files:
- `default_capabilities.py`
- `capability_registry.py`
- `capability_spec.py`

Important note: use this when adding a fixed action the assistant can run. Normal chat questions do not belong here.

---

## /ASSISCLUE/APP/context_memory

This is the real memory and context engine. It reads activity, builds useful context, stores memory, searches memory, and prepares context for tasks.

Important files:
- `README.md`
- `services/context_memory_service.py`
- `orchestration/context_pipeline.py`
- `retrieval/memory_search_service.py`

Important note: this is different from moment memory. `context_memory` is the bigger long-term memory engine; `moment_memory` is a fast live snapshot helper.

---

## /ASSISCLUE/APP/context_memory/user_spaces

This stores manual editable memory like notes, rules, prompts, and help items. It reads JSON files from runtime user spaces, not random folders.

Important files:
- `README.md`
- `user_spaces_service.py`
- `json_user_space_store.py`
- `storage_paths.py`

Important note: this is for user-written memory. The external help file `/ASSISCLUE/runtime/memory/user_spaces/help/helpfolders.md` is very important.

---

## /ASSISCLUE/APP/display_actions

This runs screen actions after the router sends them here. It handles screenshots and screen analysis results.

Important files:
- `README.md`
- `runners/display_action_router.py`
- `runners/screenshot_capture_runner.py`
- `runners/screenshot_analyze_runner.py`

Important note: this folder does not decide if an action should happen. The router decides first, then this folder runs the display action.

---

## /ASSISCLUE/APP/inputfeed_to_text

This turns live audio into text. It writes the sacred transcript files that the listeners read later.

Important files:
- `inputfeed_to_text_service.py`
- `transcript_runtime.py`
- `inputfeed_settings.py`
- `providers/moonshine/moonshine_stt_provider.py`

Important note: Moonshine lives inside `providers/moonshine/`. This folder writes the transcript; it does not answer questions or run commands.

---

## /ASSISCLUE/APP/knowledge_library

This handles the user's document library. It can scan folders, read files, summarize, chunk, index, and optionally promote useful info into context memory.

Important files:
- `README.md`
- `services/knowledge_library_facade.py`
- `orchestration/library_scan_pipeline.py`
- `orchestration/read_file_pipeline.py`

Important note: this is not the main memory engine. It is more like a library reader and organizer that can feed `context_memory` when needed.

---

## /ASSISCLUE/APP/live_listeners

This contains the listeners that read the sacred transcript. `inputfeed_to_text` writes the transcript, and these listeners read it without deleting it.

Important files:
- `README.md`
- `shared/transcript_reader.py`
- `shared/cursor_store.py`
- `shared/listener_paths.py`

Important note: every listener needs its own cursor. They all read the same transcript but at their own speed.

---

## /ASSISCLUE/APP/live_listeners/primary_listener

This is the fast listener. It detects wakewords, clear commands, and quick questions from the transcript.

Important files:
- `primary_listener_service.py`
- `primary_listener_config.py`
- `command_matcher.py`
- `command_catalog.json`

Important note: primary listener does not answer or run actions. It only detects clear events fast and sends them forward.

---

## /ASSISCLUE/APP/live_listeners/administrative_listener

This is the calmer listener. It groups recent transcript records into a paragraph and decides if it is a response candidate, context only, or ignore.

Important files:
- `administrative_listener_service.py`
- `moment_window_builder.py`
- `paragraph_builder.py`
- `live_moment_writer.py`

Important note: admin listener is different from primary listener because it is slower and looks at the present moment more carefully. It writes live moments.

---

## /ASSISCLUE/APP/live_listeners/moment_memory

This reads live moments and creates quick snapshots like current context, memory snapshot, and world state. It is a fast live helper, not the full memory brain.

Important files:
- `context_runner_service.py`
- `context_window_builder.py`
- `summary_builder.py`
- `memory_snapshot_writer.py`

Important note: moment memory is different from context memory. Moment memory is for "what is happening now"; context memory is for deeper storage, search, and long-term use.

---

## /ASSISCLUE/APP/llm

This is the central place for talking to the LLM, especially Ollama text and vision. Runners should call this folder instead of talking to Ollama directly.

Important files:
- `llm_client.py`
- `llm_service.py`
- `vision_service.py`
- `llm_prompts.py`

Important note: LLM settings are in `/ASSISCLUE/APP/settings/llm_settings.py`. This folder is for model calls, prompts, formatting, and vision.

---

## /ASSISCLUE/APP/mcp

This exposes app functions as standard tools. It is a clean doorway for memory, router, browser, display, and other blocks to be used by tool systems.

Important files:
- `server.py`
- `registry.py`
- `tools/memory_tools.py`
- `services/memory_mcp_service.py`

Important note: MCP does not replace memory, LLM, or UI. It only gives a clean way to access existing app abilities.

---

## /ASSISCLUE/APP/output

This is a small output helper folder for text, image, notification, and UI output shapes. It is not the main voice speaker.

Important files:
- `text_output.py`
- `image_output.py`
- `notification_output.py`
- `ui_output.py`

Important note: for actual spoken audio, use `/ASSISCLUE/APP/speech_out/`.

---

## /ASSISCLUE/APP/personas

This stores assistant personality/profile definitions. Other blocks can ask for the active persona instead of hardcoding strings.

Important files:
- `profiles/*.json`
- `models/assistant_profile.py`
- `registry/profile_registry.py`
- `services/persona_service.py`

Important note: personas do not route commands, store memory, or run actions. They only define the active assistant style/profile.

---

## /ASSISCLUE/APP/router_dispatch

This receives events from listeners and sends them to the correct lane. It chooses action queue, response queue, or ignore.

Important files:
- `router_service.py`
- `route_rules.py`
- `route_event_builder.py`
- `schemas/incoming_listener_event_schema.py`

Important note: router does not answer, think deeply, or execute actions. It only sends the event to the right next place.

---

## /ASSISCLUE/APP/runtime

This folder holds app runtime storage used by some services, like local Qdrant test/runtime data. Most active runtime files are outside `APP` in `/ASSISCLUE/runtime/`.

Important files:
- `qdrant/`

Important note: do not confuse this with `/ASSISCLUE/runtime/`, which has the main live files, sacred transcripts, status files, queues, and memory.

---

## /ASSISCLUE/APP/services

This has general technical services used by the app, like audio playback, mode status, settings summary, and activity status.

Important files:
- `audio_playback.py`
- `activity_status_service.py`
- `mode_service.py`
- `settings_summary_service.py`

Important note: `speech_service.py` here is only a helper. The real process that speaks is `/ASSISCLUE/APP/speech_out/speaker_service.py`.

---

## /ASSISCLUE/APP/settings

This is where the app's knobs and defaults live. It controls audio, LLM, TTS, app mode, and play settings.

Important files:
- `app_settings.py`
- `audio_settings.py`
- `llm_settings.py`
- `tts_settings.py`

Important note: use this folder for defaults and ENV-based settings. Main package requirements are in `/ASSISCLUE/requirements.txt` and `/ASSISCLUE/requirements-linux.txt`.

---

## /ASSISCLUE/APP/speech_out

This turns final text into spoken audio. It queues speech, makes TTS audio with Kokoro, and plays it.

Important files:
- `speech_queue_writer.py`
- `speaker_service.py`
- `tts_bridge.py`
- `schemas/speech_queue_schema.py`

Important note: Kokoro belongs to this output side. This folder does not decide what to say; it only speaks the final text.

---

## /ASSISCLUE/APP/spoken_queries

This processes simple spoken questions after the router sends them here. It can choose a simple answer, memory-needed path, or simple refusal.

Important files:
- `runners/spoken_query_router.py`
- `runners/simple_question_runner.py`
- `runners/memory_question_runner.py`
- `runners/llm_direct_runner.py`

Important note: this does not read the transcript directly and does not run PC actions. It receives clean routed question events.

---

## /ASSISCLUE/APP/system_support

This is shared system glue for runtime files, JSONL logs, system state, text cleaning, and LLM runtime state. Many blocks depend on this.

Important files:
- `system_runtime_state.py`
- `runtime_files.py`
- `runtime_jsonl.py`
- `llm_runtime_state.py`

Important note: this folder is very important. Core and web command support also connect through the commands subfolder.

---

## /ASSISCLUE/APP/system_support/commands

This is the command brain. It turns natural phrases like "add note buy milk" into structured commands with action, target, payload, and safety info.

Important files:
- `command_service.py`
- `command_parser.py`
- `command_handlers.py`
- `catalogs/administrative_core_commands.json`

Important note: core command catalogs and web command catalogs are very important. This is for command meaning, not for normal chat answers.

---

## /ASSISCLUE/APP/tools

This is a small toolbox folder with simple helpers like file reading, note writing, summaries, tasks, and web search wrappers.

Important files:
- `tool_registry.py`
- `file_reader.py`
- `note_writer.py`
- `summary_tools.py`

Important note: this looks like simple local helper tools. Bigger tool access is organized more through `/ASSISCLUE/APP/mcp/`.

---

## /ASSISCLUE/APP/ui_local

This is the local web UI for the app. It contains panels for chat, memory status, mode, persona, screenshots, settings, and tasks.

Important files:
- `app.py`
- `memory_status_panel.py`
- `screenshots_panel.py`
- `library_ui/README.md`

Important note: the UI should show and control the system, but it should not become the place where all business logic lives.

---

## /ASSISCLUE/APP/ui_local/library_ui

This is the visual UI for the knowledge library. It helps users view library roots, files, previews, summaries, indexing, and promotion actions.

Important files:
- `README.md`

Important note: `knowledge_library` is the backend logic. `library_ui` is the screen for humans to use it.

---

## /ASSISCLUE/APP/web_tools

This is the browser automation block using Playwright. It can open pages, read visible text, click, type, screenshot, and do simple DuckDuckGo searches.

Important files:
- `README.md`
- `browser/playwright_manager.py`
- `browser/navigation.py`
- `providers/duckduckgo_provider.py`

Important note: this is web browser automation, not Windows desktop automation and not OCR. Playwright and Chromium are the main requirement here.

---

## QUICK FLOW MAP

Audio comes in here:
`inputfeed_to_text` -> writes `/runtime/sacred/live_transcript_history.jsonl`

Listeners read it:
`primary_listener` -> fast commands/questions
`administrative_listener` -> calmer present-moment paragraphs
`moment_memory` -> quick live context snapshots

Routing happens here:
`router_dispatch` -> sends to action queue or response queue

Then work runs here:
`display_actions` for screenshots/screen actions
`spoken_queries` for spoken answers
`speech_out` for final voice output

Memory lives here:
`context_memory` for the main memory engine
`context_memory/user_spaces` for manual editable memory
`knowledge_library` for reading/indexing user documents
