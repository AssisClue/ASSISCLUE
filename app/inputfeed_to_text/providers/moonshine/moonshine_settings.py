from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class MoonshineSettings:
    enabled: bool = os.getenv("INPUTFEED_STT_BACKEND", "moonshine").strip().lower() == "moonshine"
    language: str = os.getenv("MOONSHINE_LANGUAGE", "en").strip() or "en"