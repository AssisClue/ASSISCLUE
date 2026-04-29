from __future__ import annotations

import asyncio
import os
import subprocess
import sys
from pathlib import Path
import json
import time
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.bootstrap import bootstrap_app
from app.services.activity_status_service import (
    get_activity_status,
    get_assistant_flow_status,
)
from app.services.capture_loop_service import run_screenshot_capture_once
from app.services.mode_service import get_runtime_mode_description
from app.services.settings_summary_service import build_settings_summary
from app.system_support.runtime_service_registry import (
    UI_SERVICE_SPEC,
    backend_service_specs,
    expected_root_process_count,
)
from app.system_support.system_runtime_state import (
    read_system_runtime_state,
    write_system_runtime_state,
)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PROJECT_ROOT = BASE_DIR.parent.parent

from app.display_actions.helpers.screenshot_paths import SCREENSHOTS_DIR

SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ASSISTANT_CORE_INPUTFEED_DASHBOARD")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

CONTROL_LOCK = asyncio.Lock()
CONTROL_STATE: dict[str, Any] = {
    "busy": False,
    "action": "",
    "status": "idle",
    "message": "ready",
    "last_code": None,
    "last_stdout": "",
    "last_stderr": "",
}

# Live UI session start: anything older than this is ignored by live endpoints.
UI_LIVE_STARTED_AT = time.time()


def _stack_script_path(name: str) -> Path:
    return PROJECT_ROOT / "scripts" / name


def _pid_alive(pid: Any) -> bool:
    try:
        pid_int = int(pid)
    except Exception:
        return False
    if os.name != "nt":
        try:
            os.kill(pid_int, 0)
            return True
        except Exception:
            return False
    try:
        raw = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid_int}", "/FO", "CSV", "/NH"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        return False
    return str(pid_int) in raw and "No tasks are running" not in raw


def _list_process_rows() -> list[tuple[int, str, str]]:
    if os.name != "nt":
        rows: list[tuple[int, str, str]] = []
        proc_root = Path("/proc")
        for item in proc_root.iterdir() if proc_root.exists() else []:
            if not item.name.isdigit():
                continue
            try:
                pid = int(item.name)
                name = (item / "comm").read_text(encoding="utf-8", errors="ignore").strip()
                raw_cmd = (item / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", errors="ignore").strip()
            except Exception:
                continue
            rows.append((pid, name, raw_cmd))
        return rows

    ps_cmd = (
        "Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
    )
    try:
        raw = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return []
    if not raw:
        return []
    try:
        payload = json.loads(raw)
    except Exception:
        return []
    items = payload if isinstance(payload, list) else [payload]
    rows: list[tuple[int, str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            pid = int(item.get("ProcessId", 0) or 0)
        except Exception:
            continue
        rows.append((pid, str(item.get("Name") or ""), str(item.get("CommandLine") or "")))
    return rows


def _find_service_pid(needle: str) -> int | None:
    lowered = needle.lower()
    for pid, name, cmd in _list_process_rows():
        hay = f"{name} {cmd}".lower()
        if lowered in hay:
            return pid
    return None


def _process_matches_needles(pid: Any, needles: tuple[str, ...]) -> bool:
    try:
        pid_int = int(pid)
    except Exception:
        return False
    lowered_needles = tuple(needle.lower() for needle in needles)
    for row_pid, name, cmd in _list_process_rows():
        if row_pid != pid_int:
            continue
        hay = f"{name} {cmd}".lower()
        return all(needle in hay for needle in lowered_needles)
    return False


def _process_parent_pid(pid: int) -> int | None:
    if os.name != "nt":
        try:
            return os.getppid() if pid == os.getpid() else None
        except Exception:
            return None
    ps_cmd = f"(Get-CimInstance Win32_Process -Filter \"ProcessId = {int(pid)}\").ParentProcessId"
    try:
        raw = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return int(raw) if raw else None
    except Exception:
        return None


def _same_ui_process_family(owner_pid: int, current_pid: int) -> bool:
    return _process_parent_pid(current_pid) == owner_pid or _process_parent_pid(owner_pid) == current_pid


def _ensure_single_ui_owner() -> None:
    state = read_system_runtime_state(PROJECT_ROOT)
    current_pid = os.getpid()
    try:
        owner_pid = int(state.get(UI_SERVICE_SPEC.pid_key) or 0)
    except Exception:
        owner_pid = 0
    if (
        owner_pid
        and owner_pid != current_pid
        and not _same_ui_process_family(owner_pid, current_pid)
        and _pid_alive(owner_pid)
        and _process_matches_needles(owner_pid, UI_SERVICE_SPEC.process_needles)
    ):
        raise RuntimeError(f"official UI already running at PID {owner_pid}")


def _update_ui_runtime_state() -> None:
    _ensure_single_ui_owner()
    state = read_system_runtime_state(PROJECT_ROOT)
    state["ui_pid"] = os.getpid()
    state["ui_running"] = True
    write_system_runtime_state(PROJECT_ROOT, state)


@app.on_event("startup")
async def _on_startup() -> None:
    global UI_LIVE_STARTED_AT
    UI_LIVE_STARTED_AT = time.time()
    _update_ui_runtime_state()


def _control_snapshot() -> dict[str, Any]:
    state = _normalize_runtime_state(read_system_runtime_state(PROJECT_ROOT))
    backend_running = state.get("status") == "running"
    control_status = str(CONTROL_STATE["status"] or "idle")
    final_status = control_status if CONTROL_STATE["busy"] or control_status == "error" else ("running" if backend_running else "stopped")
    return {
        "busy": bool(CONTROL_STATE["busy"]),
        "action": CONTROL_STATE["action"],
        "status": final_status,
        "message": CONTROL_STATE["message"],
        "last_code": CONTROL_STATE["last_code"],
        "last_stdout": CONTROL_STATE["last_stdout"],
        "last_stderr": CONTROL_STATE["last_stderr"],
        "ui_pid": os.getpid(),
        "ui_running": True,
        "backend_running": backend_running,
        "system_status": state.get("status") or "unknown",
        "system_runtime": state,
    }


def _normalize_runtime_state(state: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(state)
    any_backend_running = False
    for spec in backend_service_specs():
        pid = normalized.get(spec.pid_key)
        alive = _pid_alive(pid)
        if not alive:
            discovered_pid = _find_service_pid(spec.process_needles[0])
            if discovered_pid:
                pid = discovered_pid
                alive = True
        normalized[spec.pid_key] = pid if alive else None
        normalized[spec.running_key] = alive
        any_backend_running = any_backend_running or alive
    normalized[UI_SERVICE_SPEC.running_key] = _pid_alive(normalized.get(UI_SERVICE_SPEC.pid_key)) or os.getpid() == normalized.get(UI_SERVICE_SPEC.pid_key)
    if not normalized["ui_running"]:
        normalized[UI_SERVICE_SPEC.pid_key] = None
    normalized["assistant_loop_running"] = bool(normalized.get("router_dispatch_running"))
    normalized["stt_loop_running"] = bool(normalized.get("inputfeed_to_text_running"))
    normalized["screenshot_loop_running"] = bool(normalized.get("display_action_router_running"))
    ui_count = 1 if normalized.get(UI_SERVICE_SPEC.running_key) else 0
    backend_count = sum(1 for spec in backend_service_specs() if normalized.get(spec.running_key))
    normalized["root_process_count"] = ui_count + backend_count
    normalized["expected_root_process_count"] = expected_root_process_count(include_ui=True)
    normalized["status"] = "running" if any_backend_running else "stopped"
    return normalized


def _write_normalized_runtime_state() -> dict[str, Any]:
    normalized = _normalize_runtime_state(read_system_runtime_state(PROJECT_ROOT))
    write_system_runtime_state(PROJECT_ROOT, normalized)
    return normalized


def _service_status_from_runtime(
    state: dict[str, Any],
    running_key: str,
    status_payload: dict[str, Any],
) -> tuple[str, str]:
    if state.get(running_key):
        return (
            str(status_payload.get("state") or "running").strip().lower(),
            str(
                status_payload.get("last_event")
                or status_payload.get("last_routing_reason")
                or status_payload.get("last_action_name")
                or status_payload.get("last_runner_name")
                or status_payload.get("last_status")
                or "active"
            ).strip(),
        )
    return "off", "stopped"


def _read_runtime_service_statuses(runtime_dir: Path) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for spec in backend_service_specs():
        if spec.status_relpath is None:
            continue
        statuses[spec.service_id] = _read_json(runtime_dir.joinpath(*spec.status_relpath))
    return statuses


async def _run_control_action(action: str) -> dict[str, Any]:
    if action not in {"start", "stop"}:
        raise ValueError(f"unknown control action: {action}")
    script_name = "start_main_stack.py" if action == "start" else "stop_main_stack.py"
    args = [sys.executable, str(_stack_script_path(script_name)), "--backend-only"]

    proc = await asyncio.to_thread(
        subprocess.run,
        args,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    return {
        "ok": proc.returncode == 0,
        "action": action,
        "code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "message": "ok" if proc.returncode == 0 else "failed",
    }


def _launch_shutdown_action() -> None:
    args = [sys.executable, str(_stack_script_path("stop_main_stack.py"))]
    popen_kwargs: dict[str, Any] = {
        "cwd": str(PROJECT_ROOT),
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(args, **popen_kwargs)


def _project_root() -> Path:
    return PROJECT_ROOT


def _runtime_dir() -> Path:
    return PROJECT_ROOT / "runtime"


def _clear_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _reset_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")


def _remove_files(directory: Path, suffixes: tuple[str, ...]) -> None:
    if not directory.exists():
        return
    for path in directory.iterdir():
        if path.is_file() and path.suffix.lower() in suffixes:
            try:
                path.unlink()
            except Exception:
                pass


def _clean_all_lightrun_python(runtime_root: Path) -> None:
    for rel in (
        "sacred/live_transcript_raw.jsonl",
        "sacred/live_transcript_history.jsonl",
        "queues/router_dispatch/router_input_queue.jsonl",
        "queues/router_dispatch/action_queue.jsonl",
        "queues/router_dispatch/response_queue.jsonl",
        "display_actions/results/display_action_results.jsonl",
        "queues/spoken_queries/spoken_query_results.jsonl",
        "queues/speech_out/speech_queue.jsonl",
        "queues/speech_out/spoken_history.jsonl",
    ):
        _clear_file(runtime_root / rel)
    for rel in (
        "sacred/live_transcript_raw_latest.json",
        "sacred/live_transcript_latest.json",
        "status/assembled_transcript_builder_status.json",
        "status/inputfeed_to_text_status.json",
        "status/primary_listener_status.json",
        "status/raw_interrupt_listener_status.json",
        "state/live_listeners/primary_listener_cursor.json",
        "state/live_listeners/raw_interrupt_listener_cursor.json",
        "state/live_listeners/administrative_listener_cursor.json",
        "state/live_listeners/context_runner_cursor.json",
        "status/router_dispatch/router_status.json",
        "display_actions/status/display_action_runner_status.json",
        "status/spoken_queries/spoken_query_status.json",
        "queues/speech_out/latest_tts.json",
        "state/speech_out/playback_state.json",
        "status/speech_out/speech_queue_writer_status.json",
        "status/speech_out/speaker_status.json",
        "output/latest_response.json",
        "state/session_snapshot.json",
    ):
        _reset_json(runtime_root / rel)
    _remove_files(runtime_root / "queues/speech_out/audio", (".wav", ".mp3", ".ogg"))
    _remove_files(runtime_root / "input/audio_chunks", (".wav", ".json", ".txt"))


def _live_transcript_history_path(runtime_dir: Path) -> Path:
    raw_path = runtime_dir / "sacred" / "live_transcript_raw.jsonl"
    if raw_path.exists():
        return raw_path
    return runtime_dir / "sacred" / "live_transcript_history.jsonl"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}

    return {}


def _read_jsonl(
    path: Path,
    *,
    limit: int | None = None,
    newest_first: bool = False,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except Exception:
        return []

    cleaned = [line for line in lines if line.strip()]
    if limit is not None and limit > 0:
        cleaned = cleaned[-limit:]

    items: list[dict[str, Any]] = []
    for line in cleaned:
        try:
            payload = json.loads(line.lstrip("\ufeff"))
            if isinstance(payload, dict):
                items.append(payload)
        except Exception:
            continue

    if newest_first:
        items.reverse()

    return items


def _filter_since_ts(items: list[dict[str, Any]], since_ts: float | None) -> list[dict[str, Any]]:
    if since_ts is None:
        return items

    since = float(since_ts)
    return [
        item
        for item in items
        if isinstance(item.get("ts"), (int, float)) and float(item.get("ts")) >= since
    ]


def _live_since_ts(explicit_since_ts: float | None = None) -> float:
    if explicit_since_ts is not None:
        try:
            return float(explicit_since_ts)
        except Exception:
            pass
    return float(UI_LIVE_STARTED_AT)


def _ts_short(ts: Any) -> str:
    try:
        import datetime as _dt

        value = float(ts)
        return _dt.datetime.fromtimestamp(value).strftime("%H:%M:%S")
    except Exception:
        return ""


def _normalize_chat_history(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for raw in items:
        role = str(raw.get("role") or "").strip().lower()
        is_user = role == "user"
        normalized.append(
            {
                **raw,
                "ui_role": "YOU" if is_user else "ASSISTANT",
                "role_class": "user" if is_user else "assistant",
                "text": str(raw.get("text") or "").strip(),
                "ts_short": _ts_short(raw.get("ts")),
            }
        )

    return normalized


def _normalize_spoken_history(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for raw in items:
        normalized.append(
            {
                **raw,
                "ui_role": "TTS",
                "role_class": "assistant",
                "text": str(raw.get("spoken_text") or raw.get("text") or "").strip(),
                "ts_short": _ts_short(raw.get("ts")),
            }
        )

    return normalized


def _normalize_transcript_history(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []

    for raw in items:
        normalized.append(
            {
                **raw,
                "text": str(raw.get("text") or "").strip(),
                "source": str(raw.get("source") or "audio_input").strip(),
                "session_id": str(raw.get("session_id") or "").strip(),
                "language": str(raw.get("language") or "").strip(),
                "ts_short": _ts_short(raw.get("ts")),
            }
        )

    return normalized


def _debug_stage_class(stage: str) -> str:
    lowered = str(stage or "").strip().lower()
    if lowered in {"listener", "router", "spoken", "speech"}:
        return lowered
    return "transcript"


def _debug_status_class(ok: bool, *, reason: str = "", route: str = "", runner: str = "") -> str:
    if ok:
        return "ok"
    normalized_reason = str(reason or "").strip().lower()
    normalized_route = str(route or "").strip().lower()
    normalized_runner = str(runner or "").strip().lower()
    if (
        "anti_echo" in normalized_reason
        or "invalid_jsonl" in normalized_reason
        or "unavailable" in normalized_reason
        or normalized_route == "invalid_jsonl_line"
    ):
        return "error"
    if (
        "wakeword_only" in normalized_reason
        or normalized_reason in {"no_wakeword", "router_ignored", "no_spoken_result"}
        or normalized_runner == "simple_refusal_runner"
        or normalized_route == "ignore"
    ):
        return "warn"
    return "idle"


def _bool_text(value: Any) -> str:
    return "yes" if bool(value) else "no"


def _short_text(value: Any, fallback: str = "n/a") -> str:
    text = str(value or "").strip()
    return text or fallback


def _build_debug_events(runtime_dir: Path) -> list[dict[str, Any]]:
    transcripts = _read_jsonl(
        runtime_dir / "sacred" / "live_transcript_assembled.jsonl",
        limit=5,
        newest_first=True,
    )
    listener_events = _read_jsonl(runtime_dir / "queues" / "router_dispatch" / "router_input_queue.jsonl", limit=80)
    action_events = _read_jsonl(runtime_dir / "queues" / "router_dispatch" / "action_queue.jsonl", limit=80)
    response_events = _read_jsonl(runtime_dir / "queues" / "router_dispatch" / "response_queue.jsonl", limit=80)
    spoken_results = _read_jsonl(
        runtime_dir / "queues" / "spoken_queries" / "spoken_query_results.jsonl",
        limit=80,
    )
    speech_queue = _read_jsonl(runtime_dir / "queues" / "speech_out" / "speech_queue.jsonl", limit=80)
    spoken_history = _read_jsonl(runtime_dir / "queues" / "speech_out" / "spoken_history.jsonl", limit=80)
    listener_status = _read_json(runtime_dir / "status" / "primary_listener_status.json")
    router_status = _read_json(runtime_dir / "status" / "router_dispatch" / "router_status.json")
    spoken_status = _read_json(runtime_dir / "status" / "spoken_queries" / "spoken_query_status.json")
    queue_writer_status = _read_json(runtime_dir / "status" / "speech_out" / "speech_queue_writer_status.json")
    playback_state = _read_json(runtime_dir / "state" / "speech_out" / "playback_state.json")

    listener_by_source = {
        str(item.get("source_event_id", "")).strip(): item
        for item in listener_events
        if str(item.get("source_event_id", "")).strip()
    }
    route_by_source = {
        str(item.get("source_event_id", "")).strip(): item
        for item in [*action_events, *response_events]
        if str(item.get("source_event_id", "")).strip()
    }
    spoken_by_source = {
        str(item.get("source_event_id", "")).strip(): item
        for item in spoken_results
        if str(item.get("source_event_id", "")).strip()
    }
    speech_queue_by_source = {
        str(item.get("source_event_id", "")).strip(): item
        for item in speech_queue
        if str(item.get("source_event_id", "")).strip()
    }
    speech_history_by_source = {
        str(item.get("source_event_id", "")).strip(): item
        for item in spoken_history
        if str(item.get("source_event_id", "")).strip()
    }

    debug_events: list[dict[str, Any]] = []
    for transcript in transcripts:
        transcript_id = str(transcript.get("event_id", "")).strip()
        listener_event = listener_by_source.get(transcript_id)
        primary_event_id = str((listener_event or {}).get("event_id", "")).strip()
        route_event = route_by_source.get(primary_event_id)
        spoken_result = spoken_by_source.get(primary_event_id)
        speech_queue_item = speech_queue_by_source.get(primary_event_id)
        speech_history_item = speech_history_by_source.get(primary_event_id)

        stage = "transcript"
        reason = ""
        route = ""
        runner = ""
        route_runner = ""
        event_type = ""
        matched_wakeword = ""
        use_memory = False
        decision = ""
        ok = False

        if listener_event:
            stage = "listener"
            event_type = str(listener_event.get("event_type", "")).strip()
            matched_wakeword = str(listener_event.get("matched_wakeword", "")).strip()
            flags = listener_event.get("flags", {}) if isinstance(listener_event.get("flags", {}), dict) else {}
            use_memory = bool(flags.get("use_memory", False))
            decision = "emitted"
            reason = event_type or "listener_event"
            if event_type == "primary_wakeword_only":
                stage = "router"
                route = "ignore"
                reason = "router_ignored"
            if route_event:
                stage = "router"
                route = str(route_event.get("target_queue", "")).strip()
                route_runner = str(route_event.get("target_runner", "")).strip()
                reason = str(route_event.get("routing_reason", "")).strip() or reason
            if spoken_result:
                stage = "spoken"
                runner = str(spoken_result.get("runner_name", "")).strip()
                route = route or "response_queue"
                meta = spoken_result.get("meta", {}) if isinstance(spoken_result.get("meta", {}), dict) else {}
                reason = (
                    str(spoken_result.get("error_code", "")).strip()
                    or str(meta.get("fallback_reason", "")).strip()
                    or runner
                    or reason
                )
                ok = bool(spoken_result.get("ok", False))
            elif route_event and str(route_event.get("target_runner", "")).strip() == "spoken_queries":
                stage = "spoken"
                runner = str(spoken_status.get("last_runner_name", "")).strip()
                if str(spoken_status.get("last_event_id", "")).strip() == primary_event_id:
                    reason = str(spoken_status.get("last_debug_reason", "")).strip() or "no_spoken_result"
                else:
                    reason = "no_spoken_result"
            if speech_queue_item or speech_history_item:
                stage = "speech"
                ok = True
                reason = "spoken_history_written" if speech_history_item else "speech_queued"
        else:
            stage = "listener"
            route = str(router_status.get("last_route", "")).strip()
            if str(listener_status.get("last_source_event_id", "")).strip() == transcript_id:
                event_type = str(listener_status.get("last_detected_event_type", "")).strip()
                matched_wakeword = str(listener_status.get("last_matched_wakeword", "")).strip()
                use_memory = bool(listener_status.get("last_use_memory", False))
                decision = str(listener_status.get("last_decision", "")).strip()
                reason = str(listener_status.get("last_debug_reason", "")).strip() or "listener_ignored"
            else:
                reason = "listener_no_event"

        if stage != "speech" and str(playback_state.get("status", "")).strip().lower() in {"playing", "synthesizing"}:
            playback_label = str(playback_state.get("status", "")).strip().lower()
        else:
            playback_label = "idle"

        detail_parts = [
            f"type={_short_text(event_type, '-')}",
            f"wake={_short_text(matched_wakeword, 'none')}",
            f"use_memory={_bool_text(use_memory)}",
            f"route={_short_text(route, '-')}",
            f"runner={_short_text(runner or route_runner, '-')}",
            f"playback={playback_label}",
        ]
        if decision:
            detail_parts.insert(0, f"decision={decision}")

        debug_events.append(
            {
                "ts": transcript.get("ts"),
                "ts_short": _ts_short(transcript.get("ts")),
                "stage": stage.upper(),
                "stage_class": _debug_stage_class(stage),
                "status_class": _debug_status_class(ok, reason=reason, route=route, runner=runner),
                "reason": _short_text(reason),
                "text": _short_text(transcript.get("text")),
                "detail": " | ".join(detail_parts),
            }
        )

    if not debug_events:
        queue_state = str(queue_writer_status.get("state", "")).strip() or "idle"
        debug_events.append(
            {
                "ts": None,
                "ts_short": "",
                "stage": "DEBUG",
                "stage_class": "transcript",
                "status_class": "idle",
                "reason": "no_debug_events",
                "text": "No transcript debug data yet.",
                "detail": f"speech_queue={queue_state}",
            }
        )

    return debug_events


def _build_screenshots_panel(project_root: Path) -> dict[str, Any]:
    candidates = sorted(
        SCREENSHOTS_DIR.glob("*.png"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        return {
            "title": "Screenshot",
            "image_url": "",
            "image_name": "",
            "image_mtime_ns": 0,
            "image_key": "",
        }

    latest = candidates[0]
    try:
        image_mtime_ns = int(latest.stat().st_mtime_ns)
    except Exception:
        image_mtime_ns = 0
    image_key = f"{latest.name}:{image_mtime_ns}" if image_mtime_ns else latest.name
    return {
        "title": "Screenshot",
        "image_url": f"/screenshots/{latest.name}",
        "image_name": latest.name,
        "image_mtime_ns": image_mtime_ns,
        "image_key": image_key,
    }


def _build_running_services(
    *,
    system_runtime: dict[str, Any],
    llm_state: dict[str, Any],
    service_statuses: dict[str, dict[str, Any]],
    latest_tts: dict[str, Any],
    assistant_mode: str,
    llm_model_fallback: str,
) -> list[dict[str, str]]:
    def service_item(name: str, status: str, detail: str) -> dict[str, str]:
        normalized = (status or "off").strip().lower()
        return {
            "name": name,
            "status": normalized,
            "detail": detail or "n/a",
        }

    llm_status = str(llm_state.get("status") or "off").strip().lower()
    llm_detail = str(llm_state.get("model_name") or llm_model_fallback or "n/a").strip()

    items = [
        service_item("UI", "running", "fastapi local"),
        service_item(
            "Assistant",
            "running" if system_runtime.get("status") == "running" else "off",
            f"mode = {assistant_mode}",
        ),
        service_item("LLM", llm_status, llm_detail),
    ]

    for spec in backend_service_specs(panel_only=True):
        status_payload = service_statuses.get(spec.service_id, {})
        status, detail = _service_status_from_runtime(system_runtime, spec.running_key, status_payload)
        if spec.service_id == "speaker_service":
            status = "running" if system_runtime.get(spec.running_key) else "off"
            detail = (
                str(
                    latest_tts.get("status")
                    or status_payload.get("last_status")
                    or "active"
                ).strip()
                if system_runtime.get(spec.running_key)
                else "stopped"
            )
        items.append(service_item(spec.display_name, status, detail))

    return items


def build_home_context(project_root: Path, request: Request) -> dict[str, Any]:
    boot = bootstrap_app(project_root)
    runtime_dir = _runtime_dir()
    view = str(request.query_params.get("view") or "live").strip().lower()

    mode_description = get_runtime_mode_description(boot.runtime_state.current_mode)
    settings_summary = build_settings_summary(project_root)

    show_history = view == "history"
    live_since_ts = _live_since_ts()

    transcript_history = (
        _normalize_transcript_history(
            _filter_since_ts(
                _read_jsonl(
                    _live_transcript_history_path(runtime_dir),
                    limit=10,
                    newest_first=True,
                ),
                live_since_ts,
            )
        )
        if show_history
        else []
    )
    chat_history = (
        _normalize_chat_history(
            _filter_since_ts(
                _read_jsonl(
                    runtime_dir / "output" / "chat_history.jsonl",
                    limit=10,
                    newest_first=True,
                ),
                live_since_ts,
            )
        )
        if show_history
        else []
    )
    spoken_history = (
        _normalize_spoken_history(
            _filter_since_ts(
                _read_jsonl(
                    runtime_dir / "queues" / "speech_out" / "spoken_history.jsonl",
                    limit=10,
                    newest_first=True,
                ),
                live_since_ts,
            )
        )
        if show_history
        else []
    )



    latest_response = _read_json(runtime_dir / "output" / "latest_response.json")
    latest_tts = _read_json(runtime_dir / "queues" / "speech_out" / "latest_tts.json")
    system_runtime = _write_normalized_runtime_state()
    session_snapshot = _read_json(runtime_dir / "state" / "session_snapshot.json")
    llm_state = _read_json(runtime_dir / "state" / "llm_runtime_state.json")

    service_statuses = _read_runtime_service_statuses(runtime_dir)

    activity_status = get_activity_status(project_root)
    assistant_flow_status = get_assistant_flow_status(project_root)
    screenshots_panel = _build_screenshots_panel(project_root)
    debug_events = (
        _filter_since_ts(_build_debug_events(runtime_dir), live_since_ts)
        if show_history
        else []
    )
    
    mem0_runtime = {
        "enabled": False,
        "active_backend": "json",
        "mem0_ready": False,
        "process_running": False,
    }

    running_services = _build_running_services(
        system_runtime=system_runtime,
        llm_state=llm_state,
        service_statuses=service_statuses,
        latest_tts=latest_tts,
        assistant_mode=boot.runtime_state.current_mode,
        llm_model_fallback=boot.config.models.llm_model_name,
    )

    return {
        "request": request,
        "app_name": boot.config.app.app_name,
        "app_version": boot.config.app.app_version,
        "status": "running" if boot.ok else "startup_failed",
        "view": view,
        "mode": boot.runtime_state.current_mode,
        "mode_description": mode_description,
        "persona": boot.runtime_state.active_persona,
        "offline_mode": boot.config.app.offline_mode,
        "private_mode": boot.config.app.private_mode,
        "llm_enabled": boot.runtime_state.llm_enabled,
        "background_capture_enabled": boot.runtime_state.background_capture_enabled,
        "background_processing_enabled": boot.runtime_state.background_processing_enabled,
        "pending_tasks": boot.runtime_state.pending_tasks,
        "system_runtime": system_runtime,
        "session_snapshot": session_snapshot,
        "latest_response": latest_response,
        "latest_tts": latest_tts,
        "settings_summary": settings_summary,
        "chat_history": chat_history,
        "spoken_history": spoken_history,
        "transcript_history": transcript_history,
        "running_services": running_services,
        "screenshots_panel": screenshots_panel,
        "mem0_runtime": mem0_runtime,
        "activity_status": activity_status,
        "assistant_flow_status": assistant_flow_status,
        "debug_events": debug_events,
    }


@app.get("/api/transcript")
async def api_transcript(since_ts: float | None = None) -> dict[str, Any]:
    runtime_dir = _runtime_dir()
    raw = _read_jsonl(_live_transcript_history_path(runtime_dir), limit=10, newest_first=True)
    raw = _filter_since_ts(raw, _live_since_ts(since_ts))
    items = _normalize_transcript_history(raw)
    return {"items": items}


@app.get("/api/chat")
async def api_chat(since_ts: float | None = None) -> dict[str, Any]:
    runtime_dir = _runtime_dir()
    raw = _read_jsonl(runtime_dir / "output" / "chat_history.jsonl", limit=10, newest_first=True)
    raw = _filter_since_ts(raw, _live_since_ts(since_ts))
    items = _normalize_chat_history(raw)
    return {"items": items}


@app.get("/api/spoken")
async def api_spoken(since_ts: float | None = None) -> dict[str, Any]:
    runtime_dir = _runtime_dir()
    raw = _read_jsonl(runtime_dir / "queues" / "speech_out" / "spoken_history.jsonl", limit=10, newest_first=True)
    raw = _filter_since_ts(raw, _live_since_ts(since_ts))
    items = _normalize_spoken_history(raw)
    return {"items": items}


@app.get("/api/debug")
async def api_debug(since_ts: float | None = None) -> dict[str, Any]:
    runtime_dir = _runtime_dir()
    items = _build_debug_events(runtime_dir)
    items = _filter_since_ts(items, _live_since_ts(since_ts))
    return {"items": items}


@app.get("/api/services")
async def api_services() -> dict[str, Any]:
    runtime_dir = _runtime_dir()
    system_runtime = _write_normalized_runtime_state()
    llm_state = _read_json(runtime_dir / "state" / "llm_runtime_state.json")
    service_statuses = _read_runtime_service_statuses(runtime_dir)
    latest_tts = _read_json(runtime_dir / "queues" / "speech_out" / "latest_tts.json")
    items = _build_running_services(
        system_runtime=system_runtime,
        llm_state=llm_state,
        service_statuses=service_statuses,
        latest_tts=latest_tts,
        assistant_mode=str(system_runtime.get("active_mode") or "unknown").strip(),
        llm_model_fallback=str(llm_state.get("model_name") or "n/a").strip(),
    )
    return {"items": items}


@app.get("/api/screenshot")
async def api_screenshot() -> dict[str, Any]:
    project_root = _project_root()
    return _build_screenshots_panel(project_root)


@app.get("/api/control/status")
async def api_control_status() -> dict[str, Any]:
    return _control_snapshot()


@app.post("/api/control/start")
async def api_control_start() -> dict[str, Any]:
    if CONTROL_LOCK.locked():
        return {"ok": False, "message": "control already busy"}
    async with CONTROL_LOCK:
        CONTROL_STATE.update({"busy": True, "action": "start", "status": "running", "message": "starting"})
        try:
            result = await _run_control_action("start")
            CONTROL_STATE.update(
                {
                    "action": "start",
                    "status": "running" if result["ok"] else "error",
                    "message": "started" if result["ok"] else "start failed",
                    "last_code": result["code"],
                    "last_stdout": result["stdout"],
                    "last_stderr": result["stderr"],
                }
            )
            return {"ok": result["ok"], **result}
        except Exception as exc:
            CONTROL_STATE.update(
                {
                    "action": "start",
                    "status": "error",
                    "message": "start exception",
                    "last_code": -1,
                    "last_stdout": "",
                    "last_stderr": f"{type(exc).__name__}: {exc}",
                }
            )
            return {"ok": False, "message": "start exception", "error": f"{type(exc).__name__}: {exc}"}
        finally:
            CONTROL_STATE["busy"] = False


@app.post("/api/control/stop")
async def api_control_stop() -> dict[str, Any]:
    if CONTROL_LOCK.locked():
        return {"ok": False, "message": "control already busy"}
    async with CONTROL_LOCK:
        CONTROL_STATE.update({"busy": True, "action": "stop", "status": "stopping", "message": "stopping"})
        try:
            result = await _run_control_action("stop")
            CONTROL_STATE.update(
                {
                    "action": "stop",
                    "status": "stopped" if result["ok"] else "error",
                    "message": "stopped" if result["ok"] else "stop failed",
                    "last_code": result["code"],
                    "last_stdout": result["stdout"],
                    "last_stderr": result["stderr"],
                }
            )
            return {"ok": result["ok"], **result}
        except Exception as exc:
            CONTROL_STATE.update(
                {
                    "action": "stop",
                    "status": "error",
                    "message": "stop exception",
                    "last_code": -1,
                    "last_stdout": "",
                    "last_stderr": f"{type(exc).__name__}: {exc}",
                }
            )
            return {"ok": False, "message": "stop exception", "error": f"{type(exc).__name__}: {exc}"}
        finally:
            CONTROL_STATE["busy"] = False


@app.post("/api/control/shutdown")
async def api_control_shutdown() -> dict[str, Any]:
    if CONTROL_LOCK.locked():
        return {"ok": False, "message": "control already busy"}
    async with CONTROL_LOCK:
        CONTROL_STATE.update(
            {"busy": True, "action": "shutdown", "status": "stopping", "message": "shutting down"}
        )
        try:
            await asyncio.to_thread(_launch_shutdown_action)
            CONTROL_STATE.update(
                {
                    "action": "shutdown",
                    "status": "shutdown",
                    "message": "shutting down",
                    "last_code": 0,
                    "last_stdout": "",
                    "last_stderr": "",
                }
            )
            return {"ok": True, "action": "shutdown", "code": 0, "message": "shutting down"}
        except Exception as exc:
            CONTROL_STATE.update(
                {
                    "action": "shutdown",
                    "status": "error",
                    "message": "shutdown exception",
                    "last_code": -1,
                    "last_stdout": "",
                    "last_stderr": f"{type(exc).__name__}: {exc}",
                }
            )
            return {"ok": False, "message": "shutdown exception", "error": f"{type(exc).__name__}: {exc}"}
        finally:
            CONTROL_STATE["busy"] = False


@app.get("/")
async def home(request: Request):
    project_root = _project_root()
    context = build_home_context(project_root, request)
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/clear-chat")
async def clear_chat():
    project_root = _project_root()

    stop_path = project_root / "runtime" / "state" / "speech_out" / "stop_request.json"
    stop_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stop_path.write_text(
            json.dumps(
                {
                    "ts": time.time(),
                    "reason": "ui_clean_queue",
                    "source_event_id": "ui",
                    "routed_event_id": "ui",
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass

    script_path = project_root / "scripts" / "clean_all_lightrun.ps1"
    if os.name == "nt" and script_path.exists():
        try:
            subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(script_path),
                ],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except Exception:
            pass
    else:
        _clean_all_lightrun_python(project_root / "runtime")

    return RedirectResponse(url="/", status_code=303)


@app.post("/capture-screenshot")
async def debug_capture_screenshot():
    project_root = _project_root()
    run_screenshot_capture_once(project_root, trigger="ui_manual")
    return RedirectResponse(url="/", status_code=303)
