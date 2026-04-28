from __future__ import annotations

from typing import Any

from .administrative_command_matcher import match_administrative_command


BROWSER_ACTIONS = {
    "open_browser",
    "open_url",
    "look_for",
    "browser_click_text",
    "browser_click",
    "browser_type",
    "browser_press",
    "browser_refresh",
    "browser_back",
    "browser_forward",
    "browser_scroll_top",
    "browser_scroll_down",
    "browser_scroll_up",
    "browser_new_tab",
    "browser_close_tab",
    "browser_switch_tab_next",
    "browser_screenshot",
    "browser_save_visible_text",
    "browser_save_full_page_text",
}


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

    if clean_action in BROWSER_ACTIONS:
        return {
            "route_family": "browser_runtime",
            "target_runner": "administrative_listener",
            "handler_key": clean_action,
            "payload_text": clean_payload,
        }

    return {
        "route_family": "administrative",
        "target_runner": "",
        "handler_key": clean_action,
        "payload_text": clean_payload,
    }