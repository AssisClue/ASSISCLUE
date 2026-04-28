from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class LLMTextRequest:
    prompt: str
    system_prompt: str = ""
    model_name: str = ""
    temperature: float = 0.51
    max_tokens: int = 150
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LLMVisionRequest:
    image_path: str
    prompt: str
    system_prompt: str = ""
    model_name: str = ""
    temperature: float = 0.2
    max_tokens: int = 150
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LLMResult:
    ok: bool
    text: str
    provider: str
    model_name: str
    error: str = ""
    finish_reason: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)