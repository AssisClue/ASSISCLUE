from __future__ import annotations

from pathlib import Path

from app.bootstrap import bootstrap_app


def build_settings_summary(project_root: str | Path) -> dict:
    boot = bootstrap_app(project_root)

    return {
        "app_name": boot.config.app.app_name,
        "app_version": boot.config.app.app_version,
        "system_mode": boot.config.app.system_mode,
        "active_persona": boot.config.persona.active_persona,
        "offline_mode": boot.config.app.offline_mode,
        "private_mode": boot.config.app.private_mode,
        "ui_host": boot.config.ui.host,
        "ui_port": boot.config.ui.port,
        "ui_reload": boot.config.ui.reload,
        "wake_word": boot.config.audio.wake_word,
        "tts_backend": boot.config.tts.backend,
        "tts_voice": boot.config.tts.kokoro_voice,
        "tts_lang_code": boot.config.tts.kokoro_lang_code,
        "tts_sample_rate": boot.config.tts.sample_rate,
        "tts_playback_enabled": boot.config.audio.tts_playback_enabled,
        "tts_output_device_name": boot.config.audio.tts_output_device_name,
        "tts_playback_blocking": boot.config.audio.tts_playback_blocking,
        "tts_output_gain": boot.config.audio.tts_output_gain,
        "llm_enabled": boot.config.models.enable_llm,
        "llm_model_name": boot.config.models.llm_model_name,
        "memory_enabled": boot.config.memory.enabled,
        "memory_backend": boot.config.memory.backend,
        "screenshots_enabled": boot.config.screenshots.enabled,
        "screenshot_recent_seconds": boot.config.screenshots.recent_seconds,
    }