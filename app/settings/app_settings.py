from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AppSettings:
    app_name: str = "ASSISTANT_CORE"
    app_version: str = "0.1.0"
    offline_mode: bool = True
    private_mode: bool = False

    # passive | listening_light | smart_background | fully_active
    system_mode: str = "passive"

    enable_background_capture: bool = True
    enable_background_processing: bool = False
    enable_tools: bool = True
    enable_web_search: bool = False

    max_pending_tasks: int = 100
    runtime_cleanup_days: int = 7

    show_settings_panel: bool = True
    show_debug_panel: bool = True
    show_llm_panel: bool = True
    show_memory_panel: bool = True
    show_history_panel: bool = True