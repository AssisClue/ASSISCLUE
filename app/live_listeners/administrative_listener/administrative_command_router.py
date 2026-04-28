from __future__ import annotations

from typing import Any

from .administrative_command_runners import run_administrative_browser_command


def _feedback_target(command: dict[str, Any], result: dict[str, Any]) -> str:
    for key in ("payload_clean", "payload_text"):
        value = str(result.get(key) or command.get(key) or "").strip()
        if value:
            return value

    data = result.get("data", {}) if isinstance(result.get("data", {}), dict) else {}
    value = str(data.get("target_text") or "").strip()
    return value


def _browser_feedback(command: dict[str, Any], result: dict[str, Any]) -> str:
    action_name = str(result.get("action_name") or command.get("action_name") or "").strip()
    target = _feedback_target(command, result)
    error = str(result.get("error") or "").strip()
    data = result.get("data", {}) if isinstance(result.get("data", {}), dict) else {}
    data_error = str(data.get("error") or "").strip()

    if not bool(result.get("ok", False)):
        if error == "no_active_browser_session":
            return "Open the browser first."
        if action_name in {"browser_click_text", "browser_click"}:
            return f"I could not find {target}." if target else "I could not find that."
        if action_name == "look_for" and error == "missing_search_payload":
            return "Tell me what to search for."
        if data_error == "target_not_found":
            return f"I could not find {target}." if target else "I could not find that."
        return "Browser command failed."

    if action_name == "open_browser":
        return "Browser opened."
    if action_name == "open_url":
        return "Website opened."
    if action_name == "look_for":
        return f"Searching for {target}." if target else "Searching."
    if action_name in {"browser_click_text", "browser_click"}:
        return f"Clicked {target}." if target else "Clicked."
    if action_name in {"browser_save_visible_text", "browser_save_full_page_text"}:
        return "Saved file in temp folder."
    if action_name == "browser_screenshot":
        return "Browser screenshot captured."
    if action_name == "browser_refresh":
        return "Browser refreshed."
    if action_name == "browser_back":
        return "Went back."
    if action_name == "browser_forward":
        return "Went forward."
    if action_name == "browser_type":
        return "Typed."
    if action_name == "browser_press":
        return f"Pressed {target}." if target else "Pressed."
    if action_name == "browser_scroll_down":
        return "Scrolled down."
    if action_name == "browser_scroll_up":
        return "Scrolled up."
    if action_name == "browser_scroll_top":
        return "Scrolled to top."
    return "Browser command done."


def _with_browser_feedback(command: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    feedback = _browser_feedback(command, payload)
    payload["message"] = feedback
    payload["speech_text"] = feedback
    payload["answer_text"] = feedback
    return payload


def route_administrative_command(command: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(command, dict):
        return {
            "ok": False,
            "error": "invalid_command_object",
        }

    if bool(command.get("is_browser_command", False)):
        return _with_browser_feedback(command, run_administrative_browser_command(command))

    return {
        "ok": False,
        "action_name": str(command.get("action_name") or "").strip(),
        "error": "non_browser_administrative_command_not_implemented_yet",
    }
