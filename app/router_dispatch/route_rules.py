from __future__ import annotations

from typing import Any

from app.capabilities import find_capability_by_action_name

from .schemas.queue_target_schema import (
    QUEUE_TARGET_IGNORE,
    QUEUE_TARGET_RESPONSE,
)


def _get_action_name(event: dict[str, Any]) -> str:
    command = event.get("command", {})
    if not isinstance(command, dict):
        return ""
    return str(command.get("action_name", "")).strip()


def resolve_route(event: dict[str, Any]) -> dict[str, str]:
    event_type = str(event.get("event_type", "")).strip()
    action_name = _get_action_name(event)

    if event_type == "primary_command":
        command = event.get("command", {}) if isinstance(event.get("command", {}), dict) else {}
        if isinstance(command.get("command_core"), dict):
            return {
                "target_queue": QUEUE_TARGET_RESPONSE,
                "target_runner": "spoken_queries",
                "routing_reason": "primary_command:command_core_response",
            }

        capability = find_capability_by_action_name(action_name)
        if capability is not None and capability.enabled:
            return {
                "target_queue": capability.target_queue,
                "target_runner": capability.target_runner,
                "routing_reason": f"primary_command:{capability.capability_id}",
            }

        return {
            "target_queue": QUEUE_TARGET_IGNORE,
            "target_runner": "",
            "routing_reason": "primary_command:unknown_action",
        }

    if event_type == "primary_quick_question":
        return {
            "target_queue": QUEUE_TARGET_RESPONSE,
            "target_runner": "spoken_queries",
            "routing_reason": "primary_quick_question",
        }

    if event_type == "primary_wakeword_only":
        return {
            "target_queue": QUEUE_TARGET_IGNORE,
            "target_runner": "",
            "routing_reason": "primary_wakeword_only",
        }

    return {
        "target_queue": QUEUE_TARGET_IGNORE,
        "target_runner": "",
        "routing_reason": "unknown_event_type",
    }
