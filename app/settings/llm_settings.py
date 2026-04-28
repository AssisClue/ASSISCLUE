from __future__ import annotations

from dataclasses import dataclass
import os


def _normalize_base_url(value: str) -> str:
    raw = str(value or "").strip().rstrip("/")
    if not raw:
        return "http://127.0.0.1:11434"
    if "://" not in raw:
        raw = f"http://{raw}"
    return raw.rstrip("/")


def _resolve_ollama_base_url() -> str:
    # Source of truth precedence:
    # 1) OLLAMA_BASE_URL (explicit URL)
    # 2) OLLAMA_HOST (common Ollama host env, may be host:port)
    # 3) default localhost URL
    explicit = os.getenv("OLLAMA_BASE_URL", "")
    if str(explicit).strip():
        return _normalize_base_url(explicit)

    host = os.getenv("OLLAMA_HOST", "")
    if str(host).strip():
        return _normalize_base_url(host)

    return "http://127.0.0.1:11434"


@dataclass(slots=True)
class LLMSettings:
    provider: str = os.getenv("LLM_PROVIDER", "ollama").strip()
    base_url: str = _resolve_ollama_base_url()

    # Default to a lighter text model for CPU-only setups. Vision stays separate.
    text_model: str = os.getenv("LLM_TEXT_MODEL", "qwen2.5:3b").strip()
    vision_model: str = os.getenv("LLM_VISION_MODEL", "gemma3n:e4b").strip()

    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.51"))
    max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "50"))
    timeout_seconds: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "90"))
    vision_timeout_seconds: float = float(os.getenv("LLM_VISION_TIMEOUT_SECONDS", "180"))

    short_response_max_chars: int = int(os.getenv("LLM_SHORT_RESPONSE_MAX_CHARS", "20"))
    tts_response_max_chars: int = int(os.getenv("LLM_TTS_RESPONSE_MAX_CHARS", "50"))

    enable_text_llm: bool = os.getenv("LLM_ENABLE_TEXT", "1").strip() not in {"0", "false", "False"}
    enable_vision_llm: bool = os.getenv("LLM_ENABLE_VISION", "1").strip() not in {"0", "false", "False"}

    def __post_init__(self) -> None:
        self.base_url = _normalize_base_url(self.base_url)
        # Keep vision calls on a real multimodal default even if environment
        # accidentally points vision to the text-only model.
        if self.vision_model.strip().lower() == self.text_model.strip().lower():
            self.vision_model = "gemma3n:e4b"
