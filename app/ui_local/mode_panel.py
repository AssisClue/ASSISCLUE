from __future__ import annotations


def build_mode_panel() -> dict[str, str]:
    return {
        "title": "Mode",
        "status": "passive",
        "description": "Passive, listening, background, or fully active mode.",
    }