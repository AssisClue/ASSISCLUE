from __future__ import annotations

from dataclasses import dataclass


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
    headless: bool = False
    slow_mo_ms: int = 0
    navigation_timeout_ms: int = 30000
    action_timeout_ms: int = 15000
    screenshot_image_type: str = "png"