from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return {}
    return {}


def _project_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve()


def get_activity_status(project_root: str | Path) -> dict[str, Any]:
    root = _project_root(project_root)

    router_status = _read_json(root / "runtime" / "status" / "router_dispatch" / "router_status.json")
    display_status = _read_json(
        root / "runtime" / "display_actions" / "status" / "display_action_runner_status.json"
    )
    spoken_status = _read_json(
        root / "runtime" / "status" / "spoken_queries" / "spoken_query_status.json"
    )
    speaker_status = _read_json(
        root / "runtime" / "status" / "speech_out" / "speaker_status.json"
    )

    service = "idle"
    topic = "general standby"
    action = "waiting"
    details = "assistant is quiet and listening"
    last_event = "none"
    updated_at = None

    if speaker_status:
        service = "speech_out"
        topic = "voice output"
        action = str(speaker_status.get("state") or "idle").strip()
        details = str(speaker_status.get("last_status") or "speaker ready").strip()
        last_event = str(speaker_status.get("last_speech_id") or "none").strip()
        updated_at = speaker_status.get("updated_at")
    elif spoken_status:
        service = "spoken_queries"
        topic = "spoken question routing"
        action = str(spoken_status.get("state") or "idle").strip()
        details = str(spoken_status.get("last_runner_name") or "spoken query ready").strip()
        last_event = str(spoken_status.get("last_event_id") or "none").strip()
        updated_at = spoken_status.get("updated_at")
    elif display_status:
        service = "display_actions"
        topic = "display action routing"
        action = str(display_status.get("state") or "idle").strip()
        details = str(display_status.get("last_action_name") or "display action ready").strip()
        last_event = str(display_status.get("last_event_id") or "none").strip()
        updated_at = display_status.get("updated_at")
    elif router_status:
        service = "router_dispatch"
        topic = "event routing"
        action = str(router_status.get("state") or "idle").strip()
        details = str(router_status.get("last_routing_reason") or "router ready").strip()
        last_event = str(router_status.get("last_event_id") or "none").strip()
        updated_at = router_status.get("updated_at")

    return {
        "service": service,
        "topic": topic,
        "action": action,
        "details": details,
        "last_event": last_event,
        "updated_at": updated_at,
    }


def get_assistant_flow_status(project_root: str | Path) -> dict[str, Any]:
    root = _project_root(project_root)

    router_status = _read_json(root / "runtime" / "status" / "router_dispatch" / "router_status.json")
    display_status = _read_json(
        root / "runtime" / "display_actions" / "status" / "display_action_runner_status.json"
    )
    spoken_status = _read_json(
        root / "runtime" / "status" / "spoken_queries" / "spoken_query_status.json"
    )
    queue_writer_status = _read_json(
        root / "runtime" / "status" / "speech_out" / "speech_queue_writer_status.json"
    )
    speaker_status = _read_json(
        root / "runtime" / "status" / "speech_out" / "speaker_status.json"
    )
    latest_tts = _read_json(root / "runtime" / "queues" / "speech_out" / "latest_tts.json")
    playback_state = _read_json(root / "runtime" / "state" / "speech_out" / "playback_state.json")
    latest_transcript = _read_json(root / "runtime" / "sacred" / "live_transcript_latest.json")

    transcript_text = str(latest_transcript.get("text") or "").strip()
    tts_text = str(latest_tts.get("text") or "").strip()

    return {
        "latest_mic_turn": transcript_text,
        "mic_reason": str(latest_transcript.get("source") or "").strip(),
        "live_intent": str(router_status.get("last_routing_reason") or "").strip(),
        "reply_mode": str(spoken_status.get("last_runner_name") or display_status.get("last_action_name") or "").strip(),
        "final_branch": str(router_status.get("last_route") or "").strip(),
        "should_use_llm": False,
        "final_text": tts_text,
        "latest_response_has_text": bool(tts_text),
        "latest_response_text": tts_text,
        "latest_tts_has_text": bool(tts_text),
        "tts_text": tts_text,
        "tts_status": str(playback_state.get("status") or speaker_status.get("state") or "idle").strip(),
        "tts_playback_blocking": bool(playback_state.get("blocking", False)),
        "tts_playback_until_ts": playback_state.get("until_ts"),
        "speech_queue_state": str(queue_writer_status.get("state") or "").strip(),
    }
