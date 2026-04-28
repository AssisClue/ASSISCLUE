from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class TTSSettings:
    backend: str = os.getenv("ASSISCLUE_TTS_BACKEND", "kokoro").strip().lower()
    kokoro_lang_code: str = os.getenv("ASSISCLUE_KOKORO_LANG", "a").strip()
    kokoro_voice: str = os.getenv("ASSISCLUE_KOKORO_VOICE", "af_heart").strip()
    sample_rate: int = int(os.getenv("ASSISCLUE_TTS_SAMPLE_RATE", "24000"))
