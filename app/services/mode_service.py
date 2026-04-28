from __future__ import annotations


_MODE_DESCRIPTIONS = {
    "passive": "Passive mode. The system stays quiet and does not actively engage.",
    "listening_light": "Listening light mode. The system watches for direct commands and short questions.",
    "smart_background": "Smart background mode. The system listens more broadly but stays conservative.",
    "fully_active": "Fully active mode. The system is running the full live routing stack.",
}


def get_runtime_mode_flags(system_mode: str) -> dict[str, bool]:
    mode = (system_mode or "").strip().lower()

    return {
        "capture_enabled": mode in {"listening_light", "smart_background", "fully_active"},
        "routing_enabled": mode in {"listening_light", "smart_background", "fully_active"},
        "speech_enabled": mode in {"smart_background", "fully_active"},
        "background_enabled": mode in {"smart_background", "fully_active"},
    }


def get_runtime_mode_description(system_mode: str) -> str:
    mode = (system_mode or "").strip().lower()
    return _MODE_DESCRIPTIONS.get(mode, "Unknown system mode.")


def get_available_modes() -> list[str]:
    return sorted(_MODE_DESCRIPTIONS.keys())