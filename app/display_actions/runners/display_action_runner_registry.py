from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.capabilities import find_capability_by_action_name
from app.system_support.system_runtime_state import read_system_runtime_state

from .screenshot_analyze_runner import run_screenshot_analyze_action
from .screenshot_capture_runner import run_screenshot_capture_action


def run_stop_talking_action(request: dict[str, Any]) -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[3]
    stop_path = project_root / "runtime" / "state" / "speech_out" / "stop_request.json"
    stop_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "ts": time.time(),
        "reason": "user_stop_talking",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
    }
    stop_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "action_name": "stop_talking",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "analysis_text": "Stop request sent to speaker.",
        "speech_text": "",
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "capability_id": "speech.stop_talking",
            "stop_request_path": str(stop_path),
        },
    }


def run_show_runtime_status_action(request: dict[str, Any]) -> dict[str, Any]:
    project_root = Path(__file__).resolve().parents[3]
    runtime_state = read_system_runtime_state(project_root)
    active_mode = str(runtime_state.get("active_mode") or "unknown").strip()
    active_persona = str(runtime_state.get("active_persona") or "unknown").strip()
    system_status = str(runtime_state.get("status") or "unknown").strip()

    speech_text = (
        f"System status is {system_status}. "
        f"Mode is {active_mode}. "
        f"Persona is {active_persona}."
    )

    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "action_name": "show_runtime_status",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "analysis_text": speech_text,
        "speech_text": speech_text,
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "active_mode": active_mode,
            "active_persona": active_persona,
            "system_status": system_status,
            "capability_id": "system_controls.show_runtime_status",
        },
    }


def run_browser_screenshot_action(request: dict[str, Any]) -> dict[str, Any]:
    from app.services.mcp_gateway_service import MCPGatewayService

    gateway = MCPGatewayService()

    list_result = gateway.web_session_list()
    active_session_id = ""

    if list_result.ok:
        session_ids = list_result.data.get("session_ids", []) if isinstance(list_result.data, dict) else []
        if session_ids:
            active_session_id = str(session_ids[0]).strip()

    started_new_session = False
    if not active_session_id:
        start_result = gateway.web_session_start()
        if not start_result.ok:
            return {
                "result_id": f"dres_{uuid4().hex}",
                "ts": time.time(),
                "ok": False,
                "action_name": "browser_screenshot",
                "source_event_id": str(request.get("source_event_id", "")).strip(),
                "routed_event_id": str(request.get("routed_event_id", "")).strip(),
                "analysis_text": "Browser screenshot failed because no browser session could be started.",
                "speech_text": "I could not start a browser session.",
                "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
                "meta": {
                    "capability_id": "display.browser_screenshot",
                    "mcp_tool_name": "web_session_start",
                    "mcp_error_code": start_result.error_code,
                    "mcp_message": start_result.message,
                },
            }
        active_session_id = str(start_result.data.get("session_id") or "").strip()
        started_new_session = True

    capture_result = gateway.web_session_capture_page(
        session_id=active_session_id,
        full_page=True,
    )

    if not capture_result.ok:
        return {
            "result_id": f"dres_{uuid4().hex}",
            "ts": time.time(),
            "ok": False,
            "action_name": "browser_screenshot",
            "source_event_id": str(request.get("source_event_id", "")).strip(),
            "routed_event_id": str(request.get("routed_event_id", "")).strip(),
            "analysis_text": "Browser screenshot failed.",
            "speech_text": "I could not capture the browser screenshot.",
            "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
            "meta": {
                "capability_id": "display.browser_screenshot",
                "mcp_tool_name": "web_session_capture_page",
                "session_id": active_session_id,
                "started_new_session": started_new_session,
                "mcp_error_code": capture_result.error_code,
                "mcp_message": capture_result.message,
            },
        }

    capture_data = capture_result.data if isinstance(capture_result.data, dict) else {}
    screenshot_path = str(capture_data.get("path") or "").strip()
    screenshot_title = str(capture_data.get("title") or "").strip()
    screenshot_url = str(capture_data.get("url") or "").strip()

    analysis_text = "Browser screenshot captured."
    if screenshot_title:
        analysis_text = f"Browser screenshot captured from {screenshot_title}."

    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": True,
        "action_name": "browser_screenshot",
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "analysis_text": analysis_text,
        "speech_text": "Browser screenshot captured.",
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "capability_id": "display.browser_screenshot",
            "session_id": active_session_id,
            "started_new_session": started_new_session,
            "browser_screenshot_path": screenshot_path,
            "browser_url": screenshot_url,
            "browser_title": screenshot_title,
        },
    }


_HANDLER_REGISTRY = {
    "screenshot_capture": run_screenshot_capture_action,
    "browser_screenshot": run_browser_screenshot_action,
    "screenshot_analyze": run_screenshot_analyze_action,
    "show_runtime_status": run_show_runtime_status_action,
    "stop_talking": run_stop_talking_action,
}


def get_display_action_runner(action_name: str):
    capability = find_capability_by_action_name(action_name)
    if capability is None or not capability.enabled:
        return None
    return _HANDLER_REGISTRY.get(capability.handler_key)
