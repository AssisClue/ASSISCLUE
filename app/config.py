from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.settings.app_settings import AppSettings
from app.settings.audio_settings import AudioSettings
from app.settings.play_settings import PlaySettings
from app.settings.tts_settings import TTSSettings


@dataclass(slots=True)
class PathsConfig:
    project_root: Path
    runtime_dir: Path
    data_dir: Path
    models_dir: Path
    assets_dir: Path
    docs_dir: Path
    personas_dir: Path

    @classmethod
    def from_root(cls, project_root: Path) -> "PathsConfig":
        root = Path(project_root).resolve()
        return cls(
            project_root=root,
            runtime_dir=root / "runtime",
            data_dir=root / "data",
            models_dir=root / "models",
            assets_dir=root / "assets",
            docs_dir=root / "docs",
            personas_dir=root / "app" / "personas" / "profiles",
        )


@dataclass(slots=True)
class PersonaConfig:
    active_persona: str = "rick"


@dataclass(slots=True)
class ModelConfig:
    enable_llm: bool = True
    llm_model_name: str = "ollama"


@dataclass(slots=True)
class MemoryConfig:
    enabled: bool = False
    backend: str = "json"
    autostart: bool = False


@dataclass(slots=True)
class UIConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    reload: bool = False


@dataclass(slots=True)
class ScreenshotConfig:
    enabled: bool = True
    recent_seconds: int = 120


@dataclass(slots=True)
class AppConfig:
    paths: PathsConfig
    app: AppSettings = field(default_factory=AppSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    play: PlaySettings = field(default_factory=PlaySettings)
    tts: TTSSettings = field(default_factory=TTSSettings)
    persona: PersonaConfig = field(default_factory=PersonaConfig)
    models: ModelConfig = field(default_factory=ModelConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    screenshots: ScreenshotConfig = field(default_factory=ScreenshotConfig)

    @classmethod
    def build(cls, project_root: Path) -> "AppConfig":
        config = cls(paths=PathsConfig.from_root(project_root))

        # Mirror starter/UI defaults into a single global config.
        config.app.system_mode = config.play.default_system_mode
        config.persona.active_persona = config.play.default_persona
        config.ui.host = config.play.ui_host
        config.ui.port = config.play.ui_port
        config.ui.reload = config.play.ui_reload

        return config
