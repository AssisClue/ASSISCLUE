from __future__ import annotations

from typing import Any

from app.system_support.commands.administrative_command_matcher import (
    match_administrative_command,
)


def detect_administrative_command(text: str) -> dict[str, Any] | None:
    match = match_administrative_command(text)
    if not match:
        return None

    action_name = str(match.get("action_name") or "").strip()
    payload_text = str(match.get("payload_text") or "").strip()

    return {
        "ok": True,
        "kind": "administrative_command",
        "action_name": action_name,
        "section": str(match.get("section") or "").strip(),
        "command_id": str(match.get("command_id") or "").strip(),
        "capability_id": str(match.get("capability_id") or "").strip(),
        "matched_alias": str(match.get("matched_alias") or "").strip(),
        "raw_text": str(match.get("raw_text") or "").strip(),
        "payload_text": payload_text,
        "is_browser_command": bool(match.get("is_browser_command", False)),
        "routing_hint": _build_routing_hint(action_name, payload_text),
    }


def _build_routing_hint(action_name: str, payload_text: str) -> dict[str, Any]:
    clean_action = str(action_name or "").strip()
    clean_payload = str(payload_text or "").strip()

    if clean_action == "browser_screenshot":
        return {
            "route_family": "display_actions",
            "target_runner": "display_actions",
            "handler_key": "browser_screenshot",
            "payload_text": clean_payload,
        }

    if clean_action in {"open_browser", "open_url", "look_for"}:
        return {
            "route_family": "webautomation",
            "target_runner": "display_actions",
            "handler_key": clean_action,
            "payload_text": clean_payload,
        }

    return {
        "route_family": "administrative",
        "target_runner": "",
        "handler_key": clean_action,
        "payload_text": clean_payload,
    }