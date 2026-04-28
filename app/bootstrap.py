from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import time

from app.config import AppConfig
from app.personas.services.persona_service import PersonaService
from app.system_support.system_runtime_state import (
    ensure_help_explain_capture_default,
    read_system_runtime_state,
)


@dataclass(slots=True)
class RuntimeState:
    current_mode: str
    active_persona: str
    llm_enabled: bool
    background_capture_enabled: bool
    background_processing_enabled: bool
    pending_tasks: int = 0


@dataclass(slots=True)
class BootstrapResult:
    config: AppConfig
    runtime_state: RuntimeState
    ok: bool
    message: str


def _write_json_if_missing(path: Path, payload: dict) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _ensure_runtime_structure(config: AppConfig) -> None:
    runtime_dir = config.paths.runtime_dir

    dirs = [
        runtime_dir,
        runtime_dir / "sacred",
        runtime_dir / "status",
        runtime_dir / "stt_archive",
        runtime_dir / "queues" / "router_dispatch",
        runtime_dir / "display_actions" / "results",
        runtime_dir / "display_actions" / "screenshots",
        runtime_dir / "display_actions" / "status",
        runtime_dir / "queues" / "spoken_queries",
        runtime_dir / "status" / "spoken_queries",
        runtime_dir / "queues" / "speech_out" / "audio",
        runtime_dir / "status" / "speech_out",
        runtime_dir / "state",
        runtime_dir / "output",
        config.paths.data_dir,
        config.paths.models_dir,
        config.paths.assets_dir,
        config.paths.docs_dir,
        config.paths.personas_dir,
    ]

    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

    text_files = [
        runtime_dir / "sacred" / "live_transcript_history.jsonl",
        runtime_dir / "sacred" / "live_transcript_assembled.jsonl",
        runtime_dir / "queues" / "router_dispatch" / "router_input_queue.jsonl",
        runtime_dir / "queues" / "router_dispatch" / "action_queue.jsonl",
        runtime_dir / "queues" / "router_dispatch" / "response_queue.jsonl",
        runtime_dir / "display_actions" / "results" / "display_action_results.jsonl",
        runtime_dir / "queues" / "spoken_queries" / "spoken_query_results.jsonl",
        runtime_dir / "queues" / "speech_out" / "speech_queue.jsonl",
        runtime_dir / "queues" / "speech_out" / "spoken_history.jsonl",
        runtime_dir / "output" / "chat_history.jsonl",
    ]
    for path in text_files:
        if not path.exists():
            path.write_text("", encoding="utf-8")

    _write_json_if_missing(runtime_dir / "sacred" / "live_transcript_latest.json", {})
    _write_json_if_missing(runtime_dir / "status" / "inputfeed_to_text_status.json", {})
    _write_json_if_missing(runtime_dir / "status" / "assembled_transcript_builder_status.json", {})
    _write_json_if_missing(runtime_dir / "status" / "router_dispatch" / "router_status.json", {})
    _write_json_if_missing(
        runtime_dir / "display_actions" / "status" / "display_action_runner_status.json",
        {},
    )
    _write_json_if_missing(
        runtime_dir / "status" / "spoken_queries" / "spoken_query_status.json",
        {},
    )
    _write_json_if_missing(
        runtime_dir / "status" / "speech_out" / "speech_queue_writer_status.json",
        {},
    )
    _write_json_if_missing(
        runtime_dir / "status" / "speech_out" / "speaker_status.json",
        {},
    )
    _write_json_if_missing(runtime_dir / "queues" / "speech_out" / "latest_tts.json", {})
    _write_json_if_missing(runtime_dir / "state" / "speech_out" / "playback_state.json", {})
    _write_json_if_missing(runtime_dir / "state" / "system_runtime.json", {})
    _write_json_if_missing(runtime_dir / "state" / "session_snapshot.json", {})
    _write_json_if_missing(runtime_dir / "output" / "latest_response.json", {})


def _load_current_mode(config: AppConfig) -> str:
    payload = read_system_runtime_state(config.paths.project_root) or {}
    mode = str(payload.get("active_mode") or payload.get("system_mode") or config.app.system_mode).strip()
    return mode or config.app.system_mode


def _load_active_persona(config: AppConfig) -> str:
    payload = read_system_runtime_state(config.paths.project_root) or {}
    persona = str(payload.get("active_persona") or config.persona.active_persona).strip()
    return persona or config.persona.active_persona


def _resolve_active_persona(config: AppConfig) -> str:
    persona_service = PersonaService(config.paths.personas_dir)
    active_profile = persona_service.get_active_profile(config.persona.active_persona)
    return active_profile.persona_id


def _write_llm_runtime_state(config: AppConfig) -> None:
    payload = {
        "ts": time.time(),
        "provider": "ollama" if config.models.enable_llm else "none",
        "model_name": config.models.llm_model_name,
        "status": "running" if config.models.enable_llm else "disabled",
        "error": "",
    }
    path = config.paths.runtime_dir / "state" / "llm_runtime_state.json"
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def bootstrap_app(project_root: str | Path) -> BootstrapResult:
    root = Path(project_root).resolve()
    config = AppConfig.build(root)

    _ensure_runtime_structure(config)

    # For now, every app start begins with HELP explain capture enabled.
    # This keeps EXPLAIN routed to HELP while we build the HELP block.
    ensure_help_explain_capture_default(
        config.paths.project_root,
        enabled=True,
        force=True,
    )

    config.app.system_mode = _load_current_mode(config)
    config.persona.active_persona = _load_active_persona(config)
    config.persona.active_persona = _resolve_active_persona(config)

    runtime_state = RuntimeState(
        current_mode=config.app.system_mode,
        active_persona=config.persona.active_persona,
        llm_enabled=config.models.enable_llm,
        background_capture_enabled=config.app.enable_background_capture,
        background_processing_enabled=config.app.enable_background_processing,
        pending_tasks=0,
    )

    _write_llm_runtime_state(config)

    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | INFO | app.bootstrap | bootstrap complete at {root}")
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | INFO | app.bootstrap | active persona: {runtime_state.active_persona}")
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | INFO | app.bootstrap | system mode: {runtime_state.current_mode}")
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | INFO | app.bootstrap | help explain capture: enabled")
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | INFO | app.bootstrap | diagnostics status: ok")
    print(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} | INFO | app.bootstrap | "
        f"llm status: {'running' if config.models.enable_llm else 'disabled'}"
    )

    return BootstrapResult(
        config=config,
        runtime_state=runtime_state,
        ok=True,
        message="bootstrap complete",
    )
