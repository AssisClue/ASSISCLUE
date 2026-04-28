from __future__ import annotations

import base64
import time
from pathlib import Path

import httpx

from app.settings.llm_settings import LLMSettings
from .llm_types import LLMResult, LLMTextRequest, LLMVisionRequest


def _build_client(timeout_seconds: float) -> httpx.Client:
    return httpx.Client(timeout=timeout_seconds)


def _coerce_finish_reason(data: dict) -> str:
    if data.get("done") is True:
        return str(data.get("done_reason") or "stop").strip() or "stop"
    return "incomplete"


def _result_from_success(
    *,
    provider: str,
    model_name: str,
    text: str,
    data: dict,
    metadata: dict,
) -> LLMResult:
    return LLMResult(
        ok=True,
        text=str(text or "").strip(),
        provider=provider,
        model_name=model_name,
        error="",
        finish_reason=_coerce_finish_reason(data),
        prompt_tokens=int(data.get("prompt_eval_count", 0) or 0),
        completion_tokens=int(data.get("eval_count", 0) or 0),
        metadata=metadata,
    )


def run_ollama_text(request: LLMTextRequest, settings: LLMSettings) -> LLMResult:
    model_name = request.model_name or settings.text_model
    payload = {
        "model": model_name,
        "system": request.system_prompt,
        "prompt": request.prompt,
        "stream": False,
        "options": {
            "temperature": request.temperature,
            "num_predict": request.max_tokens,
        },
    }

    started = time.monotonic()
    try:
        with _build_client(settings.timeout_seconds) as client:
            response = client.post(
                f"{settings.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        text = str(data.get("response") or "").strip()
        metadata = {
            **request.metadata,
            "provider": "ollama",
            "done": data.get("done", False),
            "done_reason": data.get("done_reason", ""),
            "total_duration": data.get("total_duration", 0),
            "load_duration": data.get("load_duration", 0),
            "prompt_eval_duration": data.get("prompt_eval_duration", 0),
            "eval_duration": data.get("eval_duration", 0),
        }
        return _result_from_success(
            provider="ollama",
            model_name=model_name,
            text=text,
            data=data,
            metadata=metadata,
        )

    except Exception as exc:
        elapsed = time.monotonic() - started
        err = f"{type(exc).__name__}: {exc} (elapsed={elapsed:.1f}s timeout={float(settings.timeout_seconds):.1f}s)"
        return LLMResult(
            ok=False,
            text="",
            provider="ollama",
            model_name=model_name,
            error=err,
            finish_reason="error",
            metadata={
                **request.metadata,
                "provider": "ollama",
                "error": err,
                "timeout_seconds": float(settings.timeout_seconds),
                "elapsed_seconds": float(elapsed),
            },
        )


def _encode_image_base64(image_path: str | Path) -> str:
    return base64.b64encode(Path(image_path).read_bytes()).decode("utf-8")


def run_ollama_vision(request: LLMVisionRequest, settings: LLMSettings) -> LLMResult:
    model_name = request.model_name or settings.vision_model
    payload = {
        "model": model_name,
        "keep_alive": "10m",
        "system": request.system_prompt,
        "prompt": request.prompt,
        "images": [_encode_image_base64(request.image_path)],
        "stream": False,
        "options": {
            "temperature": request.temperature,
            "num_predict": request.max_tokens,
        },
    }

    started = time.monotonic()
    try:
        with _build_client(settings.timeout_seconds) as client:
            response = client.post(
                f"{settings.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        text = str(data.get("response") or "").strip()
        metadata = {
            **request.metadata,
            "provider": "ollama",
            "done": data.get("done", False),
            "done_reason": data.get("done_reason", ""),
            "total_duration": data.get("total_duration", 0),
            "load_duration": data.get("load_duration", 0),
            "prompt_eval_duration": data.get("prompt_eval_duration", 0),
            "eval_duration": data.get("eval_duration", 0),
            "image_path": str(request.image_path),
        }
        return _result_from_success(
            provider="ollama",
            model_name=model_name,
            text=text,
            data=data,
            metadata=metadata,
        )

    except Exception as exc:
        elapsed = time.monotonic() - started
        err = f"{type(exc).__name__}: {exc} (elapsed={elapsed:.1f}s timeout={float(settings.timeout_seconds):.1f}s)"
        return LLMResult(
            ok=False,
            text="",
            provider="ollama",
            model_name=model_name,
            error=err,
            finish_reason="error",
            metadata={
                **request.metadata,
                "provider": "ollama",
                "error": err,
                "timeout_seconds": float(settings.timeout_seconds),
                "elapsed_seconds": float(elapsed),
            },
        )
