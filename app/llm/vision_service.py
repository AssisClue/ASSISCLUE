from __future__ import annotations

from pathlib import Path
import httpx

from app.settings.llm_settings import LLMSettings
from .llm_client import run_ollama_vision
from .llm_formatters import trim_for_tts, trim_for_ui
from .llm_prompts import VISION_SCREENSHOT_SYSTEM_PROMPT, build_screenshot_prompt
from .llm_types import LLMResult, LLMVisionRequest


def _looks_like_vision_model(model_name: str) -> bool:
    name = (model_name or "").strip().lower()
    if not name:
        return False
    # Heuristic: Ollama vision-capable models usually include one of these tokens.
    return any(token in name for token in ("llava", "vision", "vl", "minicpm", "qwen2.5vl", "pixtral"))


def _vision_backend_health(settings: LLMSettings) -> tuple[bool, str]:
    tags_url = f"{settings.base_url}/api/tags"
    try:
        response = httpx.get(tags_url, timeout=min(4.0, settings.timeout_seconds))
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return False, f"vision_backend_unreachable: {settings.base_url} ({exc})"

    models = data.get("models", [])
    names: set[str] = set()
    if isinstance(models, list):
        for item in models:
            if not isinstance(item, dict):
                continue
            model_name = str(item.get("name") or "").strip()
            if not model_name:
                continue
            names.add(model_name)
            base_name = model_name.split(":")[0].strip()
            if base_name:
                names.add(base_name)

    wanted = settings.vision_model.strip()
    wanted_base = wanted.split(":")[0].strip()
    if wanted and wanted not in names and wanted_base and wanted_base not in names:
        return False, f"vision_model_not_installed: {settings.vision_model} at {settings.base_url}"
    return True, ""


def analyze_image(
    *,
    image_path: str | Path,
    user_intent_hint: str = "",
    metadata: dict | None = None,
) -> dict:
    settings = LLMSettings()
    # Vision models can need extra warm-up/load time versus text calls.
    settings.timeout_seconds = max(settings.timeout_seconds, settings.vision_timeout_seconds)
    image_text_path = str(Path(image_path))

    if not settings.enable_vision_llm:
        return {
            "ok": False,
            "text": "",
            "ui_text": "",
            "tts_text": "",
            "error": "vision_llm_disabled",
            "provider": settings.provider,
            "model_name": settings.vision_model,
            "metadata": metadata or {},
        }

    if not _looks_like_vision_model(settings.vision_model):
        return {
            "ok": False,
            "text": "",
            "ui_text": "",
            "tts_text": "",
            "error": f"vision_model_not_multimodal: {settings.vision_model}",
            "provider": settings.provider,
            "model_name": settings.vision_model,
            "metadata": metadata or {},
        }

    healthy, health_error = _vision_backend_health(settings)
    if not healthy:
        return {
            "ok": False,
            "text": "",
            "ui_text": "",
            "tts_text": "",
            "error": health_error,
            "provider": settings.provider,
            "model_name": settings.vision_model,
            "metadata": metadata or {},
        }

    request = LLMVisionRequest(
        image_path=image_text_path,
        prompt=build_screenshot_prompt(user_intent_hint=user_intent_hint),
        system_prompt=VISION_SCREENSHOT_SYSTEM_PROMPT,
        model_name=settings.vision_model,
        temperature=0.2,
        max_tokens=settings.max_tokens,
        metadata=metadata or {},
    )

    result: LLMResult = run_ollama_vision(request, settings)

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
