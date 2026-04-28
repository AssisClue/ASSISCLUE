from __future__ import annotations

import os
import argparse
import signal
import json
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import bootstrap_app
from app.system_support.runtime_service_registry import (
    BACKEND_SERVICE_SPECS,
    backend_service_specs,
    stack_process_needles,
    starter_chain_text,
)
from app.system_support.system_runtime_state import (
    build_system_runtime_payload,
    read_system_runtime_state,
    write_system_runtime_state,
)


STARTER_NAME = "stop_main_stack.py"

STATUS_RUNTIME_DIR = PROJECT_ROOT / "runtime" / "status"
ROUTER_STATUS_JSON = PROJECT_ROOT / "runtime" / "status" / "router_dispatch" / "router_status.json"
DISPLAY_STATUS_JSON = (
    PROJECT_ROOT / "runtime" / "display_actions" / "status" / "display_action_runner_status.json"
)
SPOKEN_STATUS_JSON = (
    PROJECT_ROOT / "runtime" / "status" / "spoken_queries" / "spoken_query_status.json"
)
SPEECH_QUEUE_WRITER_STATUS_JSON = (
    PROJECT_ROOT / "runtime" / "status" / "speech_out" / "speech_queue_writer_status.json"
)
SPEAKER_STATUS_JSON = PROJECT_ROOT / "runtime" / "status" / "speech_out" / "speaker_status.json"
ASSEMBLER_STATUS_JSON = PROJECT_ROOT / "runtime" / "status" / "assembled_transcript_builder_status.json"
CONTEXT_MEMORY_RUNTIME_STATUS_JSON = (
    PROJECT_ROOT / "runtime" / "status" / "memory" / "context_memory_runtime_status.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Stop only backend services and keep the web UI running.",
    )
    return parser.parse_args()


def _wmic_list_processes() -> list[tuple[int, str, str]]:
    try:
        raw = subprocess.check_output(
            [
                "wmic",
                "process",
                "get",
                "ProcessId,Name,CommandLine",
                "/FORMAT:CSV",
            ],
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        raw = ""

    rows: list[tuple[int, str, str]] = []
    if raw:
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("node,"):
                continue

            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 4:
                continue

            name = parts[-2]
            pid_str = parts[-1]
            cmd = ",".join(parts[2:-2]) if len(parts) > 4 else parts[1]

            try:
                pid = int(pid_str)
            except Exception:
                continue

            rows.append((pid, name or "", cmd or ""))
        return rows

    ps_cmd = (
        "Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress"
    )
    try:
        ps_raw = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return []
    if not ps_raw:
        return []
    try:
        payload = json.loads(ps_raw)
    except Exception:
        return []
    items = payload if isinstance(payload, list) else [payload]
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            pid = int(item.get("ProcessId", 0) or 0)
        except Exception:
            continue
        rows.append((pid, str(item.get("Name") or ""), str(item.get("CommandLine") or "")))

    return rows


def _find_stack_pids(*, include_ui: bool = True) -> list[int]:
    needles = stack_process_needles(include_ui=include_ui)

    pids: list[int] = []
    for pid, name, cmd in _wmic_list_processes():
        hay = f"{name} {cmd}".lower()
        if not hay.strip():
            continue
        if any(n.lower() in hay for n in needles):
            pids.append(pid)

    return [pid for pid in sorted(set(pids)) if pid != os.getpid()]


def _kill_pid(pid: int | None) -> None:
    if not pid:
        return

    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(int(pid)), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            return
        return

    try:
        os.kill(int(pid), signal.SIGTERM)
    except Exception:
        return


def _kill_many(pids: list[int | None]) -> None:
    for pid in pids:
        _kill_pid(pid)


def _kill_stack_tree_with_proof(*, include_ui: bool = True) -> list[int]:
    killed: list[int] = []
    for _ in range(4):
        live_stack = _find_stack_pids(include_ui=include_ui)
        if not live_stack:
            break
        for pid in live_stack:
            _kill_pid(pid)
            if pid not in killed:
                killed.append(pid)
    return sorted(set(killed))


def _live_pid_set() -> set[int]:
    return {pid for pid, _, _ in _wmic_list_processes()}


def _print_windows_process_snapshot() -> None:
    print("\nWINDOWS PROCESS SNAPSHOT")
    print("-" * 80)

    interesting = []
    for pid, name, cmd in _wmic_list_processes():
        hay = f"{name} {cmd}".lower()
        if any(token in hay for token in ["python", "py.exe", "uvicorn", "ollama"]):
            interesting.append((pid, name, cmd))

    if not interesting:
        print("No matching python/uvicorn/ollama processes found.")
        return

    for pid, name, cmd in interesting:
        short_cmd = (cmd or "").strip()
        if len(short_cmd) > 180:
            short_cmd = short_cmd[:177] + "..."
        print(f"PID={pid} | NAME={name} | CMD={short_cmd}")


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}
    return {}


def _write_service_status(path: Path, service_name: str, state: str, **extra: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    current = _load_json(path)
    payload: dict[str, object] = {
        "ok": state != "error",
        "state": state,
        "service": service_name,
        "updated_at": time.time(),
    }
    for key, value in current.items():
        if key.startswith("last_processed_line_number") or key.endswith("_last_processed_line_number"):
            payload[key] = value
    payload.update(extra)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_stopped_status_files(*, backend_only: bool) -> None:
    _write_service_status(
        STATUS_RUNTIME_DIR / "inputfeed_to_text_status.json",
        "inputfeed_to_text",
        "off",
        last_event="stopped",
    )
    _write_service_status(
        ASSEMBLER_STATUS_JSON,
        "assembled_transcript_builder",
        "off",
        last_event="stopped",
    )
    _write_service_status(
        STATUS_RUNTIME_DIR / "primary_listener_status.json",
        "primary_listener",
        "off",
        last_event="stopped",
    )
    _write_service_status(
        STATUS_RUNTIME_DIR / "administrative_listener_status.json",
        "administrative_listener",
        "off",
        last_event="stopped",
    )
    _write_service_status(
        PROJECT_ROOT / "runtime" / "browser" / "status.json",
        "browser_service",
        "off",
        last_event="stopped",
    )
    _write_service_status(
        ROUTER_STATUS_JSON,
        "router_dispatch",
        "off",
        last_route="stopped",
        last_routing_reason="stopped",
    )
    _write_service_status(
        DISPLAY_STATUS_JSON,
        "display_action_runner",
        "off",
        last_action_name="stopped",
        last_result_ok=False,
    )
    _write_service_status(
        SPOKEN_STATUS_JSON,
        "spoken_query_router",
        "off",
        last_runner_name="stopped",
        last_result_ok=False,
    )
    _write_service_status(
        CONTEXT_MEMORY_RUNTIME_STATUS_JSON,
        "context_memory_runtime",
        "off",
        last_result_id="",
        memory_item_count=0,
    )
    _write_service_status(
        SPEECH_QUEUE_WRITER_STATUS_JSON,
        "speech_queue_writer",
        "off",
        last_result_id="",
        last_enqueued_speech_id="",
    )
    _write_service_status(
        SPEAKER_STATUS_JSON,
        "speaker_service",
        "off",
        last_status="stopped",
        last_speech_id="",
    )


def main() -> None:
    args = _parse_args()
    boot = bootstrap_app(PROJECT_ROOT)
    state = read_system_runtime_state(PROJECT_ROOT)
    starter_chain = starter_chain_text(include_ui=not args.backend_only)

    known_runtime_pids = [state.get("ui_pid")]
    known_runtime_pids.extend(state.get(spec.pid_key) for spec in backend_service_specs())
    known_runtime_pids.extend(
        [
            state.get("assistant_loop_pid"),
            state.get("stt_loop_pid"),
            state.get("screenshot_loop_pid"),
        ]
    )

    if args.backend_only:
        known_runtime_pids = [pid for pid in known_runtime_pids if pid and pid != state.get("ui_pid")]
    killed_pids: list[int] = [int(pid) for pid in known_runtime_pids if pid]
    _kill_many(known_runtime_pids)
    killed_pids.extend(_kill_stack_tree_with_proof(include_ui=not args.backend_only))

    still_alive = _find_stack_pids(include_ui=not args.backend_only)
    if still_alive:
        raise RuntimeError(f"stop failed; stack still alive: {still_alive}")

    ui_pid: int | None = None
    ui_running = False
    if args.backend_only:
        try:
            candidate_ui_pid = int(state.get("ui_pid") or 0)
        except Exception:
            candidate_ui_pid = 0
        if candidate_ui_pid > 0 and candidate_ui_pid in _live_pid_set():
            ui_pid = candidate_ui_pid
            ui_running = True

    payload = build_system_runtime_payload(
        status="running" if args.backend_only else "stopped",
        active_mode=boot.config.app.system_mode,
        active_persona=boot.config.persona.active_persona,
        ui_running=ui_running if args.backend_only else False,
        assistant_loop_running=False,
        stt_loop_running=False,
        screenshot_loop_running=False,
    )

    payload["starter_name"] = STARTER_NAME
    payload["starter_chain"] = starter_chain
    payload["starter_model"] = "kill_and_report"

    payload["inputfeed_to_text_pid"] = None
    payload["inputfeed_to_text_running"] = False
    payload["assembled_transcript_builder_pid"] = None
    payload["assembled_transcript_builder_running"] = False
    payload["primary_listener_pid"] = None
    payload["primary_listener_running"] = False
    payload["administrative_listener_pid"] = None
    payload["administrative_listener_running"] = False
    payload["browser_service_pid"] = None
    payload["browser_service_running"] = False
    payload["router_dispatch_pid"] = None
    payload["router_dispatch_running"] = False
    payload["display_action_router_pid"] = None
    payload["display_action_router_running"] = False
    payload["spoken_query_router_pid"] = None
    payload["spoken_query_router_running"] = False
    payload["context_memory_runtime_pid"] = None
    payload["context_memory_runtime_running"] = False
    payload["speech_queue_writer_pid"] = None
    payload["speech_queue_writer_running"] = False
    payload["speaker_service_pid"] = None
    payload["speaker_service_running"] = False
    payload["raw_interrupt_listener_pid"] = None
    payload["raw_interrupt_listener_running"] = False
    if args.backend_only:
        payload["ui_pid"] = ui_pid
        payload["ui_running"] = ui_running
    payload["root_process_count"] = 1 if (args.backend_only and ui_running) else 0
    payload["ollama_managed_by_starter"] = False

    write_system_runtime_state(PROJECT_ROOT, payload)
    _write_stopped_status_files(backend_only=args.backend_only)

    print("STOPPED")
    print(f"starter_name = {STARTER_NAME}")
    print(f"starter_chain = {starter_chain}")
    print(f"root_process_count = {payload['root_process_count']}")
    print("ollama_managed_by_starter = False")
    print(f"backend_only = {args.backend_only}")
    print(f"killed_pids = {sorted(set(killed_pids))}")
    if args.backend_only:
        print("UI: uvicorn app.ui_local.app:app")
    for spec in BACKEND_SERVICE_SPECS:
        print(f"SERVICE: {spec.process_needles[0]}")

    _print_windows_process_snapshot()


if __name__ == "__main__":
    main()
