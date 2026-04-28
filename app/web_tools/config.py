from __future__ import annotations

import os
from dataclasses import dataclass


def _default_headless() -> bool:
    if os.getenv("WEBTOOLS_HEADLESS", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    if os.getenv("WEBTOOLS_HEADLESS", "").strip().lower() in {"0", "false", "no", "off"}:
        return False
    return os.name != "nt" and not os.getenv("DISPLAY") and not os.getenv("WAYLAND_DISPLAY")


@dataclass(slots=True)
class WebToolsConfig:
    """
    Base config for local browser automation.

    Phase 1:
    - Chromium only
    - visible browser by default
    - no persistent profile yet
    """

    browser_name: str = "chromium"
    headless: bool = _default_headless()
    slow_mo_ms: int = 0
    navigation_timeout_ms: int = 30000
    action_timeout_ms: int = 15000
    screenshot_image_type: str = "png"
