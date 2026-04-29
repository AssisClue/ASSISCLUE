from __future__ import annotations

import os
import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Prefer the repo venv if present. This avoids "works yesterday" issues when the global
# python is missing audio deps (soundfile, sounddevice, etc.).
_VENV_PY = PROJECT_ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
PYTHON_EXE = str(_VENV_PY) if _VENV_PY.exists() else sys.executable

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.bootstrap import bootstrap_app
from app.settings.play_settings import PlaySettings
from app.system_support.runtime_service_registry import (
    BACKEND_SERVICE_SPECS,
    UI_SERVICE_SPEC,
    backend_service_specs,
    expected_root_process_count,
    stack_process_needles,
    starter_chain_text,
)
from app.system_support.system_runtime_state import (
    build_system_runtime_payload,
    read_system_runtime_state,
    write_system_runtime_state,
)


STARTER_NAME = "start_main_stack.py"

STARTUP_GRACE_SECONDS = 1.25


def _wmic_list_processes() -> list[tuple[int, str, str]]:
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


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Start only backend services and leave the web UI running.",
    )
    return parser.parse_args()


def _live_pid_set() -> set[int]:
    return {pid for pid, _, _ in _wmic_list_processes()}


def _pid_alive(pid: int | None) -> bool:
    return bool(pid) and int(pid) in _live_pid_set()


def _pid_matches_needles(pid: int | None, needles: tuple[str, ...]) -> bool:
    if not pid:
        return False
    lowered_needles = tuple(needle.lower() for needle in needles)
    for row_pid, name, cmd in _wmic_list_processes():
        if row_pid != int(pid):
            continue
        hay = f"{name} {cmd}".lower()
        return all(needle in hay for needle in lowered_needles)
    return False


def _stack_pid_details() -> list[tuple[int, str, str]]:
    needles = stack_process_needles(include_ui=True)
    rows: list[tuple[int, str, str]] = []
    for pid, name, cmd in _wmic_list_processes():
        hay = f"{name} {cmd}".lower()
        if any(n.lower() in hay for n in needles):
            rows.append((pid, name, cmd))
    return [row for row in rows if row[0] != os.getpid()]


def _kill_pid(pid: int | None) -> None:
    if not pid:
        return
    if os.name != "nt":
        try:
            os.kill(int(pid), signal.SIGTERM)
        except Exception:
            pass
        return
    try:
        subprocess.run(
            ["taskkill", "/PID", str(int(pid)), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except Exception:
        return


def _kill_stack_tree_with_proof_for(*, include_ui: bool) -> list[int]:
    killed: list[int] = []
    live_before = _live_pid_set()
    for pid in sorted(set([pid for pid in _find_stack_pids(include_ui=include_ui) if pid in live_before])):
        _kill_pid(pid)
        killed.append(pid)

    # Repeat until the stack is actually gone or we stop making progress.
    for _ in range(3):
        remaining = [pid for pid, _, _ in _stack_pid_details() if pid in _live_pid_set()]
        if not include_ui:
            remaining = [
                pid
                for pid, name, cmd in _stack_pid_details()
                if pid in _live_pid_set()
                and "app.ui_local.app:app" not in f"{name} {cmd}".lower()
            ]
        if not remaining:
            break
        for pid in remaining:
            _kill_pid(pid)
            if pid not in killed:
                killed.append(pid)

    return sorted(set(killed))


def _preclean_previous_stack(*, backend_only: bool) -> list[int]:
    state = read_system_runtime_state(PROJECT_ROOT)
    known_runtime_pids: list[tuple[int | None, tuple[str, ...]]] = [
        (state.get(spec.pid_key), spec.process_needles) for spec in backend_service_specs()
    ]
    known_runtime_pids.extend(
        [
            (state.get("assistant_loop_pid"), ("app.router_dispatch.router_service",)),
            (state.get("stt_loop_pid"), ("app.inputfeed_to_text.inputfeed_to_text_service",)),
            (state.get("screenshot_loop_pid"), ("app.display_actions.runners.display_action_router",)),
        ]
    )
    if not backend_only:
        known_runtime_pids.insert(0, (state.get("ui_pid"), UI_SERVICE_SPEC.process_needles))
    killed: list[int] = []
    for pid, needles in known_runtime_pids:
        if pid and pid in _live_pid_set() and _pid_matches_needles(int(pid), needles):
            _kill_pid(pid)
            killed.append(int(pid))
    killed.extend(_kill_stack_tree_with_proof_for(include_ui=not backend_only))

    remaining = [pid for pid, _, _ in _stack_pid_details() if pid in _live_pid_set()]
    if backend_only:
        remaining = [
            pid
            for pid, name, cmd in _stack_pid_details()
            if pid in _live_pid_set() and "app.ui_local.app:app" not in f"{name} {cmd}".lower()
        ]
    if remaining:
        raise RuntimeError(f"preclean failed; stack still alive: {remaining}")
    return sorted(set(killed))


def _popen(cmd: list[str]) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        cwd=str(PROJECT_ROOT),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )


def _proc_info(proc: subprocess.Popen | None) -> dict[str, Any]:
    return {
        "pid": proc.pid if proc else None,
        "running": proc is not None and proc.poll() is None,
        "returncode": None if proc is None else proc.poll(),
    }


def _assert_process_alive(name: str, proc: subprocess.Popen | None) -> None:
    if proc is None:
        raise RuntimeError(f"{name} failed to start: process not created.")

    returncode = proc.poll()
    if returncode is not None:
        raise RuntimeError(f"{name} exited immediately with code {returncode}.")


def _file_size(path: Path) -> int:
    try:
        return int(path.stat().st_size) if path.exists() else 0
    except Exception:
        return 0


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _prime_runtime_cursors_to_eof() -> None:
    runtime_dir = PROJECT_ROOT / "runtime"

    raw_transcript = runtime_dir / "sacred" / "live_transcript_raw.jsonl"
    assembled_transcript = runtime_dir / "sacred" / "live_transcript_assembled.jsonl"

    _write_json(
        runtime_dir / "state" / "live_listeners" / "raw_interrupt_listener_cursor.json",
        {"byte_offset": _file_size(raw_transcript), "last_event_id": "", "updated_at": time.time()},
    )
    _write_json(
        runtime_dir / "state" / "live_listeners" / "primary_listener_cursor.json",
        {"byte_offset": _file_size(assembled_transcript), "last_event_id": "", "updated_at": time.time()},
    )
    _write_json(
        runtime_dir / "state" / "live_listeners" / "administrative_listener_cursor.json",
        {"byte_offset": _file_size(assembled_transcript), "last_event_id": "", "updated_at": time.time()},
    )

    _write_json(
        runtime_dir / "status" / "router_dispatch" / "router_status.json",
        {
            "ok": True,
            "state": "primed",
            "service": "router_dispatch",
            "updated_at": time.time(),
            "last_processed_line_number": 0,
            "last_processed_byte_offset": _file_size(runtime_dir / "queues" / "router_dispatch" / "router_input_queue.jsonl"),
        },
    )
    _write_json(
        runtime_dir / "status" / "spoken_queries" / "spoken_query_status.json",
        {
            "ok": True,
            "state": "primed",
            "service": "spoken_query_router",
            "updated_at": time.time(),
            "last_processed_line_number": 0,
            "last_processed_byte_offset": _file_size(runtime_dir / "queues" / "router_dispatch" / "response_queue.jsonl"),
        },
    )
    _write_json(
        runtime_dir / "display_actions" / "status" / "display_action_runner_status.json",
        {
            "ok": True,
            "state": "primed",
            "service": "display_action_runner",
            "updated_at": time.time(),
            "last_processed_line_number": 0,
            "last_processed_byte_offset": _file_size(runtime_dir / "queues" / "router_dispatch" / "action_queue.jsonl"),
        },
    )
    _write_json(
        runtime_dir / "status" / "speech_out" / "speech_queue_writer_status.json",
        {
            "ok": True,
            "state": "primed",
            "service": "speech_queue_writer",
            "updated_at": time.time(),
            "last_processed_line_number": 0,
            "display_last_processed_byte_offset": _file_size(
                runtime_dir / "display_actions" / "results" / "display_action_results.jsonl"
            ),
            "spoken_last_processed_byte_offset": _file_size(
                runtime_dir / "queues" / "spoken_queries" / "spoken_query_results.jsonl"
            ),
            "display_last_processed_line_number": 0,
            "spoken_last_processed_line_number": 0,
        },
    )
    _write_json(
        runtime_dir / "status" / "speech_out" / "speaker_status.json",
        {
            "ok": True,
            "state": "primed",
            "service": "speaker_service",
            "updated_at": time.time(),
            "last_processed_line_number": 0,
            "last_status": "primed",
            "last_speech_id": "",
            "last_processed_byte_offset": _file_size(runtime_dir / "queues" / "speech_out" / "speech_queue.jsonl"),
        },
    )


def main() -> None:
    args = _parse_args()
    boot = bootstrap_app(PROJECT_ROOT)
    settings = PlaySettings()
    starter_chain = starter_chain_text(include_ui=not args.backend_only)
    previous_state = read_system_runtime_state(PROJECT_ROOT)
    preserved_ui_pid = previous_state.get("ui_pid") if _pid_alive(previous_state.get("ui_pid")) else None
    preserved_ui_running = bool(preserved_ui_pid)
    killed_pids = _preclean_previous_stack(backend_only=args.backend_only)
    _prime_runtime_cursors_to_eof()

    processes: dict[str, subprocess.Popen | None] = {
        "ui": None,
        "library_ui": None,
        "inputfeed_to_text": None,
        "assembled_transcript_builder": None,
        "primary_listener": None,
        "administrative_listener": None,
        "browser_service": None,
        "router_dispatch": None,
        "display_action_router": None,
        "spoken_query_router": None,
        "context_memory_runtime": None,
        "speech_queue_writer": None,
        "speaker_service": None,
        "raw_interrupt_listener": None,
    }

    try:
        live_before_spawn = _live_pid_set()

        if settings.enable_ui and not args.backend_only:
            ui_cmd = [
                PYTHON_EXE,
                "-m",
                "uvicorn",
                "app.ui_local.app:app",
                "--host",
                settings.ui_host,
                "--port",
                str(settings.ui_port),
            ]
            if settings.ui_reload:
                ui_cmd.append("--reload")
            processes["ui"] = _popen(ui_cmd)

        processes["library_ui"] = _popen(
            [
                PYTHON_EXE,
                "-m",
                "uvicorn",
                "app.ui_local.library_ui.appdocs:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8002",
            ]
        )
        processes["inputfeed_to_text"] = _popen(
            [PYTHON_EXE, "-m", "app.inputfeed_to_text.inputfeed_to_text_service"]
        )
        processes["assembled_transcript_builder"] = _popen(
            [PYTHON_EXE, "-m", "app.inputfeed_to_text.assembled_transcript_builder"]
        )
        processes["primary_listener"] = _popen(
            [PYTHON_EXE, "-m", "app.live_listeners.primary_listener.primary_listener_service"]
        )
        processes["administrative_listener"] = _popen(
            [PYTHON_EXE, "-m", "app.live_listeners.administrative_listener.administrative_listener_service"]
        )
        processes["browser_service"] = _popen(
            [PYTHON_EXE, "-m", "app.web_tools.browser.browser_service"]
        )
        processes["router_dispatch"] = _popen(
            [PYTHON_EXE, "-m", "app.router_dispatch.router_service"]
        )
        processes["display_action_router"] = _popen(
            [PYTHON_EXE, "-m", "app.display_actions.runners.display_action_router"]
        )


        processes["raw_interrupt_listener"] = _popen(
            [PYTHON_EXE, "-m", "app.live_listeners.primary_listener.raw_interrupt_listener"]
        )


        processes["spoken_query_router"] = _popen(
            [PYTHON_EXE, "-m", "app.spoken_queries.runners.spoken_query_router"]
        )
        processes["context_memory_runtime"] = _popen(
            [PYTHON_EXE, "-m", "app.context_memory.runtime.context_memory_runtime_service"]
        )
        processes["speech_queue_writer"] = _popen(
            [PYTHON_EXE, "-m", "app.speech_out.speech_queue_writer"]
        )
        processes["speaker_service"] = _popen(
            [PYTHON_EXE, "-m", "app.speech_out.speaker_service"]
        )

        time.sleep(STARTUP_GRACE_SECONDS)

        live_after_spawn = _live_pid_set()
        duplicate_stack_pids = []
        for pid, name, cmd in _stack_pid_details():
            if pid not in live_after_spawn:
                continue
            if pid not in live_before_spawn:
                continue
            if args.backend_only and "app.ui_local.app:app" in f"{name} {cmd}".lower():
                continue
            if pid not in {p.pid for p in processes.values() if p}:
                duplicate_stack_pids.append(pid)
        if duplicate_stack_pids:
            raise RuntimeError(f"refusing to start on top of live stack processes: {duplicate_stack_pids}")

        if settings.enable_ui and not args.backend_only:
            _assert_process_alive("uvicorn_ui", processes["ui"])
        _assert_process_alive("library_ui", processes["library_ui"])
        _assert_process_alive("inputfeed_to_text_service", processes["inputfeed_to_text"])
        _assert_process_alive("assembled_transcript_builder", processes["assembled_transcript_builder"])
        _assert_process_alive("primary_listener_service", processes["primary_listener"])
        _assert_process_alive("administrative_listener_service", processes["administrative_listener"])
        _assert_process_alive("browser_service", processes["browser_service"])
        _assert_process_alive("router_dispatch_service", processes["router_dispatch"])
        _assert_process_alive("display_action_router", processes["display_action_router"])
        _assert_process_alive("spoken_query_router", processes["spoken_query_router"])
        _assert_process_alive("context_memory_runtime_service", processes["context_memory_runtime"])
        _assert_process_alive("speech_queue_writer", processes["speech_queue_writer"])
        _assert_process_alive("speaker_service", processes["speaker_service"])

        _assert_process_alive("raw_interrupt_listener", processes["raw_interrupt_listener"])



        payload = build_system_runtime_payload(
            status="running",
            active_mode=boot.config.app.system_mode,
            active_persona=boot.config.persona.active_persona,
            ui_running=_proc_info(processes["ui"])["running"] if settings.enable_ui and not args.backend_only else preserved_ui_running,
            assistant_loop_running=_proc_info(processes["router_dispatch"])["running"],
            stt_loop_running=_proc_info(processes["inputfeed_to_text"])["running"],
            screenshot_loop_running=_proc_info(processes["display_action_router"])["running"],
            ui_pid=_proc_info(processes["ui"])["pid"] if settings.enable_ui and not args.backend_only else preserved_ui_pid,
            assistant_loop_pid=_proc_info(processes["router_dispatch"])["pid"],
            stt_loop_pid=_proc_info(processes["inputfeed_to_text"])["pid"],
            screenshot_loop_pid=_proc_info(processes["display_action_router"])["pid"],
        )

        payload["starter_name"] = STARTER_NAME
        payload["starter_chain"] = starter_chain
        payload["starter_model"] = "launch_and_exit"

        def live_only(proc: subprocess.Popen | None) -> dict[str, Any]:
            info = _proc_info(proc)
            if info["pid"] not in live_after_spawn:
                info["pid"] = None
                info["running"] = False
            return info

        ui_info = (
            live_only(processes["ui"])
            if settings.enable_ui and not args.backend_only
            else {"pid": preserved_ui_pid, "running": preserved_ui_running}
        )
        library_ui_info = live_only(processes["library_ui"])
        input_info = live_only(processes["inputfeed_to_text"])
        assembled_info = live_only(processes["assembled_transcript_builder"])
        primary_info = live_only(processes["primary_listener"])
        administrative_info = live_only(processes["administrative_listener"])
        browser_info = live_only(processes["browser_service"])
        
        raw_interrupt_info = live_only(processes["raw_interrupt_listener"])
        
        router_info = live_only(processes["router_dispatch"])
        display_info = live_only(processes["display_action_router"])
        spoken_info = live_only(processes["spoken_query_router"])
        context_memory_info = live_only(processes["context_memory_runtime"])
        writer_info = live_only(processes["speech_queue_writer"])
        speaker_info = live_only(processes["speaker_service"])

        payload["inputfeed_to_text_pid"] = input_info["pid"]
        payload["inputfeed_to_text_running"] = input_info["running"]

        payload["library_ui_pid"] = library_ui_info["pid"]
        payload["library_ui_running"] = library_ui_info["running"]

        payload["assembled_transcript_builder_pid"] = assembled_info["pid"]
        payload["assembled_transcript_builder_running"] = assembled_info["running"]

        payload["primary_listener_pid"] = primary_info["pid"]
        payload["primary_listener_running"] = primary_info["running"]

        payload["administrative_listener_pid"] = administrative_info["pid"]
        payload["administrative_listener_running"] = administrative_info["running"]

        payload["browser_service_pid"] = browser_info["pid"]
        payload["browser_service_running"] = browser_info["running"]

        payload["router_dispatch_pid"] = router_info["pid"]
        payload["router_dispatch_running"] = router_info["running"]

        payload["display_action_router_pid"] = display_info["pid"]
        payload["display_action_router_running"] = display_info["running"]

        payload["spoken_query_router_pid"] = spoken_info["pid"]
        payload["spoken_query_router_running"] = spoken_info["running"]

        payload["context_memory_runtime_pid"] = context_memory_info["pid"]
        payload["context_memory_runtime_running"] = context_memory_info["running"]

        payload["speech_queue_writer_pid"] = writer_info["pid"]
        payload["speech_queue_writer_running"] = writer_info["running"]

        payload["speaker_service_pid"] = speaker_info["pid"]
        payload["speaker_service_running"] = speaker_info["running"]


        payload["raw_interrupt_listener_pid"] = raw_interrupt_info["pid"]
        payload["raw_interrupt_listener_running"] = raw_interrupt_info["running"]


        payload["ui_pid"] = ui_info["pid"]
        payload["ui_running"] = ui_info["running"]
        payload["assistant_loop_pid"] = router_info["pid"]
        payload["assistant_loop_running"] = router_info["running"]
        payload["stt_loop_pid"] = input_info["pid"]
        payload["stt_loop_running"] = input_info["running"]
        payload["screenshot_loop_pid"] = display_info["pid"]
        payload["screenshot_loop_running"] = display_info["running"]
        live_root_infos = [
            ui_info,
            library_ui_info,
            input_info,
            assembled_info,
            primary_info,
            administrative_info,
            browser_info,
            raw_interrupt_info,
            router_info,
            display_info,
            spoken_info,
            context_memory_info,
            writer_info,
            speaker_info,
        ]
        payload["root_process_count"] = sum(1 for info in live_root_infos if info["running"])
        payload["ollama_managed_by_starter"] = False

        write_system_runtime_state(PROJECT_ROOT, payload)

        print("STARTED")
        print(f"starter_name = {STARTER_NAME}")
        print(f"starter_chain = {starter_chain}")
        print(f"root_process_count = {payload['root_process_count']}")
        print("ollama_managed_by_starter = False")
        print(f"backend_only = {args.backend_only}")
        print(f"killed_pids = {killed_pids}")
        print(
            "started_pids = "
            f"{[info['pid'] for info in [ui_info, library_ui_info, input_info, assembled_info, primary_info, administrative_info, browser_info, raw_interrupt_info, router_info, display_info, spoken_info, context_memory_info, writer_info, speaker_info] if info['pid']]}"
        )
        if not args.backend_only:
            print("UI: uvicorn app.ui_local.app:app")
        print("LIBRARY_UI: uvicorn app.ui_local.library_ui.appdocs:app")
        for spec in BACKEND_SERVICE_SPECS:
            print(f"SERVICE: {spec.process_needles[0]}")


    except Exception as exc:
        payload = build_system_runtime_payload(
            status="error",
            active_mode=boot.config.app.system_mode,
            active_persona=boot.config.persona.active_persona,
            ui_running=False,
            assistant_loop_running=False,
            stt_loop_running=False,
            screenshot_loop_running=False,
            last_error=str(exc),
        )
        payload["starter_name"] = STARTER_NAME
        payload["starter_chain"] = starter_chain
        payload["starter_model"] = "launch_and_exit"

        payload["inputfeed_to_text_pid"] = None
        payload["inputfeed_to_text_running"] = False
        payload["library_ui_pid"] = None
        payload["library_ui_running"] = False
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
        payload["root_process_count"] = 0
        payload["ollama_managed_by_starter"] = False

        write_system_runtime_state(PROJECT_ROOT, payload)
        raise


if __name__ == "__main__":
    main()
