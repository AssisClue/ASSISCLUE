from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.llm.vision_service import analyze_image
from app.settings.llm_settings import LLMSettings


def _capture_real_if_needed() -> Path | None:
    from app.display_actions.runners.screenshot_capture_runner import (
        run_screenshot_capture_action,
    )

    capture_result = run_screenshot_capture_action(
        {
            "source_event_id": "",
            "routed_event_id": "",
            "command": {"action_name": "take_screenshot"},
            "flags": {},
        }
    )
    screenshot_path = str(capture_result.get("screenshot_path") or "").strip()
    return Path(screenshot_path) if screenshot_path else None


def _build_no_previous_result(request: dict[str, Any], action_name: str, settings: LLMSettings) -> dict[str, Any]:
    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": False,
        "action_name": action_name,
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "screenshot_path": "",
        "screenshot_created": False,
        "used_existing_screenshot": False,
        "error_code": "no_previous_screenshot",
        "analysis_text": "",
        "speech_text": "No previous screenshot available.",
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "analysis_backend": "ollama_vision",
            "vision_model": settings.vision_model,
        },
    }


def _build_capture_failed_result(
    request: dict[str, Any],
    action_name: str,
    settings: LLMSettings,
    *,
    created_now: bool,
    used_existing: bool,
) -> dict[str, Any]:
    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": False,
        "action_name": action_name,
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "screenshot_path": "",
        "screenshot_created": created_now,
        "used_existing_screenshot": used_existing,
        "error_code": "screenshot_capture_failed",
        "analysis_text": "",
        "speech_text": "I couldn't capture a screenshot to analyze.",
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "analysis_backend": "ollama_vision",
            "vision_model": settings.vision_model,
            "recent_reuse": used_existing,
        },
    }


def _build_analysis_result(
    request: dict[str, Any],
    action_name: str,
    settings: LLMSettings,
    *,
    target_path: Path,
    created_now: bool,
    used_existing: bool,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    ok = bool(analysis.get("ok", False))
    text = str(analysis.get("text") or "").strip()
    tts_text = str(analysis.get("tts_text") or text).strip()
    error = str(analysis.get("error") or "").strip()
    model_name = str(analysis.get("model_name") or settings.vision_model).strip()
    failure_speech = "I couldn't analyze the screenshot."
    if not ok and error.startswith("vision_backend_unreachable:"):
        failure_speech = "I couldn't analyze the screenshot because the vision backend is offline."
    elif not ok and error.startswith("vision_model_not_installed:"):
        failure_speech = "I couldn't analyze the screenshot because the vision model is not installed."
    elif not ok and "timed out" in error.lower():
        failure_speech = "I couldn't analyze the screenshot because the vision model timed out."

    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": ok,
        "action_name": action_name,
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "screenshot_path": str(target_path),
        "screenshot_created": created_now,
        "used_existing_screenshot": used_existing,
        "error_code": "" if ok else (error or "vision_analysis_failed"),
        "analysis_text": text if ok else "",
        "speech_text": tts_text if ok else (tts_text or failure_speech),
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "analysis_backend": "ollama_vision",
            "vision_model": model_name,
            "recent_reuse": used_existing,
        },
    }


def run_screenshot_analyze_action(request: dict[str, Any]) -> dict[str, Any]:
    from app.display_actions.helpers.screenshot_paths import (
        get_latest_screenshot_path,
        is_recent_screenshot,
    )

    settings = LLMSettings()
    command = request.get("command", {}) if isinstance(request.get("command", {}), dict) else {}
    action_name = str(command.get("action_name", "")).strip()

    latest_path = get_latest_screenshot_path()

    if action_name == "analyze_last_screenshot":
        if latest_path is None or not latest_path.exists():
            return _build_no_previous_result(request, action_name, settings)

        analysis = analyze_image(
            image_path=latest_path,
            user_intent_hint="The user explicitly asked to analyze the last screenshot.",
            metadata={
                "action_name": action_name,
                "source_event_id": str(request.get("source_event_id", "")).strip(),
            },
        )
        return _build_analysis_result(
            request,
            action_name,
            settings,
            target_path=latest_path,
            created_now=False,
            used_existing=True,
            analysis=analysis,
        )

    if latest_path is not None and is_recent_screenshot(latest_path):
        target_path = latest_path
        created_now = False
        used_existing = True
    else:
        target_path = _capture_real_if_needed()
        created_now = True
        used_existing = False

    if target_path is None or not target_path.exists():
        return _build_capture_failed_result(
            request,
            action_name,
            settings,
            created_now=created_now,
            used_existing=used_existing,
        )

    analysis = analyze_image(
        image_path=target_path,
        user_intent_hint="The user asked to analyze the current screen.",
        metadata={
            "action_name": action_name,
            "source_event_id": str(request.get("source_event_id", "")).strip(),
        },
    )
    return _build_analysis_result(
        request,
        action_name,
        settings,
        target_path=target_path,
        created_now=created_now,
        used_existing=used_existing,
        analysis=analysis,
    )
