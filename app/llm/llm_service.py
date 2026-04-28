from __future__ import annotations

from app.settings.llm_settings import LLMSettings
from .llm_client import run_ollama_text
from .llm_formatters import trim_for_tts, trim_for_ui
from .llm_prompts import TEXT_ASSISTANT_SYSTEM_PROMPT, build_text_prompt
from .llm_types import LLMResult, LLMTextRequest


def get_llm_settings() -> LLMSettings:
    return LLMSettings()


def generate_text_response(
    *,
    user_text: str,
    context_text: str = "",
    system_prompt: str = "",
    max_tokens: int | None = None,
    temperature: float | None = None,
    metadata: dict | None = None,
) -> LLMResult:
    settings = get_llm_settings()

    if not settings.enable_text_llm:
        return LLMResult(
            ok=False,
            text="",
            provider=settings.provider,
            model_name=settings.text_model,
            error="text_llm_disabled",
            finish_reason="disabled",
            metadata=metadata or {},
        )

    request = LLMTextRequest(
        prompt=build_text_prompt(user_text, context_text=context_text),
        system_prompt=(system_prompt or TEXT_ASSISTANT_SYSTEM_PROMPT).strip(),
        model_name=settings.text_model,
        temperature=settings.temperature if temperature is None else temperature,
        max_tokens=settings.max_tokens if max_tokens is None else max_tokens,
        metadata=metadata or {},
    )
    return run_ollama_text(request, settings)


def generate_short_spoken_response(
    *,
    user_text: str,
    context_text: str = "",
    system_prompt: str = "",
    metadata: dict | None = None,
) -> dict:
    settings = get_llm_settings()
    result = generate_text_response(
        user_text=user_text,
        context_text=context_text,
        system_prompt=system_prompt,
        metadata=metadata,
    )

    if not result.ok:
        return {
            "ok": False,
            "text": "",
            "ui_text": "",
            "tts_text": "",
            "error": result.error,
            "provider": result.provider,
            "model_name": result.model_name,
            "metadata": result.metadata,
        }

    return {
        "ok": True,
        "text": result.text,
        "ui_text": trim_for_ui(result.text, max_chars=settings.short_response_max_chars),
        "tts_text": trim_for_tts(result.text, max_chars=settings.tts_response_max_chars),
        "error": "",
        "provider": result.provider,
        "model_name": result.model_name,
        "metadata": result.metadata,
    }