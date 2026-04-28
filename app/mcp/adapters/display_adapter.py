from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.display_actions.runners.screenshot_analyze_runner import run_screenshot_analyze_action
from app.display_actions.runners.screenshot_capture_runner import run_screenshot_capture_action


def _build_request(action_name: str) -> dict[str, Any]:
    return {
        "source_event_id": "",
        "routed_event_id": "",
        "command": {"action_name": action_name},
        "flags": {},
    }


@dataclass(slots=True)
class DisplayAdapter:
    """
    MCP-facing adapter for screenshot and display actions.

    Uses existing display runners as the real execution layer.
    """

    def capture_screenshot(self) -> dict[str, Any]:
        return run_screenshot_capture_action(_build_request("take_screenshot"))

    def capture_full_screenshot(self) -> dict[str, Any]:
        return run_screenshot_capture_action(_build_request("take_full_screenshot"))

    def analyze_latest_screenshot(self) -> dict[str, Any]:
        return run_screenshot_analyze_action(_build_request("analyze_last_screenshot"))

    def analyze_current_screen(self) -> dict[str, Any]:
        return run_screenshot_analyze_action(_build_request("analyze_screenshot"))