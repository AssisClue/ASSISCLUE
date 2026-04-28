# MCP Tools Map

## Current phase
Phase 1+ is working internally.

Total tools:
- 30

---

## Memory tools

### `search_memory`
Searches memory through the current context-memory service facade.

Input:
- `query: str`
- `limit: int = 5`
- `preferred_sources: list[str] = []`

Type:
- read-only

### `get_recent_context`
Returns recent context snapshot.

Type:
- read-only

### `get_live_context`
Returns live context snapshot.

Type:
- read-only

### `get_user_profile_context`
Returns user profile context snapshot.

Type:
- read-only

### `get_task_context`
Builds task context packet.

Input:
- `task_type: str`
- `query: str = ""`
- `project_name: str = ""`
- `preferred_sources: list[str] = []`
- `tags: list[str] = []`

Type:
- read-only

### `list_user_spaces`
Lists user spaces.

Type:
- read-only

### `get_user_space`
Searches one user space.

Input:
- `space_id: str`
- `query: str = ""`
- `limit: int = 20`

Type:
- read-only

---

## Runtime tools

### `read_system_runtime_state`
Reads current system runtime state.

Type:
- read-only

### `read_llm_runtime_state`
Reads LLM runtime state with safe fallback.

Type:
- read-only

### `read_recent_chat_history`
Reads recent items from `runtime/output/chat_history.jsonl`.

Type:
- read-only

### `read_latest_response`
Reads `runtime/output/latest_response.json`.

Type:
- read-only

### `read_latest_tts`
Reads `runtime/output/latest_tts.json`.

Type:
- read-only

### `read_latest_decision`
Reads `runtime/state/latest_decision.json`.

Type:
- read-only

---

## Display tools

### `capture_screenshot`
Captures standard screenshot.

Type:
- write / side effect

### `capture_full_screenshot`
Captures full screenshot.

Type:
- write / side effect

### `analyze_latest_screenshot`
Analyzes latest screenshot.

Type:
- read-only over existing screenshot state

### `analyze_current_screen`
Captures or reuses screenshot, then analyzes.

Type:
- write + read

---

## Workspace tools

### `read_text_file`
Reads UTF-8 text file.

Type:
- read-only

### `read_text_file_safe`
Reads UTF-8 text file safely.

Type:
- read-only

### `read_python_file`
Reads Python source file as text with language metadata.

Type:
- read-only

### `read_json_file`
Reads and parses JSON file with safe fallback.

Type:
- read-only

### `append_note`
Appends text to file.

Type:
- write / side effect

### `overwrite_note`
Overwrites file text.

Type:
- write / side effect

---

## Moment memory tools

### `read_context_snapshot`
Reads `runtime/sacred/context_snapshot.json`.

Type:
- read-only

### `read_memory_snapshot`
Reads `runtime/sacred/memory_snapshot.json`.

Type:
- read-only

### `read_world_state`
Reads `runtime/sacred/world_state.json`.

Type:
- read-only

### `read_context_runner_status`
Reads `runtime/status/context_runner_status.json`.

Type:
- read-only

### `read_context_runner_cursor`
Reads `runtime/state/live_listeners/context_runner_cursor.json`.

Type:
- read-only

---

## Capabilities tools

### `list_capabilities`
Lists capabilities exposed by `app/capabilities/`.

Type:
- read-only

### `get_capability_by_action_name`
Looks up one capability by `action_name`.

Input:
- `action_name: str`

Type:
- read-only

---

## Architecture rule

Preferred flow:

```text
tool -> mcp service -> mcp adapter -> existing app service/runner

## Personas tools

### `list_personas`
Lists safe persona summaries from `app/personas/`.

Type:
- read-only

### `get_persona`
Looks up one persona by `persona_id`.

Input:
- `persona_id: str`

Type:
- read-only

### `get_active_persona_id`
Reads the active persona id from `runtime/state/system_runtime.json`.

Type:
- read-only
