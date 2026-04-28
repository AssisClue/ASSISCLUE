from __future__ import annotations

import time
from uuid import uuid4
from typing import Any

from app.capabilities import find_capability_by_action_name


def build_routed_event(
    event: dict[str, Any],
    *,
    target_queue: str,
    target_runner: str,
    routing_reason: str,
) -> dict[str, Any]:
    command = event.get("command", {}) if isinstance(event.get("command", {}), dict) else {}
    action_name = str(command.get("action_name", "")).strip()
    resolved_capability = find_capability_by_action_name(action_name)
    capability_payload = command.get("capability", {}) if isinstance(command.get("capability", {}), dict) else {}
    if not capability_payload and resolved_capability is not None:
        capability_payload = {
            "capability_id": resolved_capability.capability_id,
            "block_id": resolved_capability.block_id,
            "handler_key": resolved_capability.handler_key,
        }

    return {
        "routed_event_id": f"revt_{uuid4().hex}",
        "ts": time.time(),
        "source_event_id": str(event.get("event_id", "")).strip(),
        "source": "router_dispatch",
        "event_type": str(event.get("event_type", "")).strip(),
        "target_queue": target_queue,
        "target_runner": target_runner,
        "text": str(event.get("text", "")).strip(),
        "original_text": str(event.get("original_text", "")).strip(),
        "transcript_text": str(event.get("transcript_text", "")).strip(),
        "cleaned_text": str(event.get("cleaned_text", "")).strip(),
        "matched_wakeword": str(event.get("matched_wakeword", "")).strip(),
        "flags": event.get("flags", {}) if isinstance(event.get("flags", {}), dict) else {},
        "command": command,
        "capability": capability_payload,
        "routing_reason": routing_reason,
    }
