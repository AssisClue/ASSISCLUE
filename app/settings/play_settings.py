from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PlaySettings:
    # MASTER SWITCHES
    enable_ui: bool = True
    enable_assistant_loop: bool = True
    enable_stt_loop: bool = True
    enable_screenshot_loop: bool = False


    # DEFAULT START MODE
    default_system_mode: str = "listening_light"
    default_persona: str = "rick"

    # UI
    ui_host: str = "127.0.0.1"
    ui_port: int = 8000
    ui_reload: bool = False

    # LOOP BEHAVIOR
    assistant_loop_poll_seconds: float = 0.25
    idle_sleep_seconds: float = 0.35

    # EXECUTION
    auto_execute_latest_bundle: bool = True
    auto_execute_ignore_routes: bool = False
    enable_tts_for_generation: bool = True

    # SAFETY / QUIET MODE
    allow_background_generation: bool = False
    allow_screenshot_auto_execution: bool = False
    allow_system_audio_auto_generation: bool = False    
    allow_mic_auto_generation: bool = True

    # PROCESS LABELS
    ui_process_name: str = "ui_local"
    assistant_process_name: str = "assistant_play_loop"
    stt_process_name: str = "stt_live_loop"
    screenshot_process_name: str = "screenshot_interval_loop"