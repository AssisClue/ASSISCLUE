from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from app.personas.services.persona_service import PersonaService


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _runtime_root() -> Path:
    return _project_root() / "runtime"


def _safe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    return raw if isinstance(raw, dict) else {}


def _to_plain_data(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, tuple):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, dict):
        return {str(key): _to_plain_data(val) for key, val in value.items()}

    if hasattr(value, "__dataclass_fields__"):
        result: dict[str, Any] = {}
        for field_name in value.__dataclass_fields__.keys():
            result[field_name] = _to_plain_data(getattr(value, field_name))
        return result

    if hasattr(value, "__dict__"):
        raw = vars(value)
        return {str(key): _to_plain_data(val) for key, val in raw.items()}

    return str(value)


def _sanitize_persona_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Keep this read-only and safe.
    Do not expose raw prompt-heavy internals by default.
    """
    allowed_keys = {
        "persona_id",
        "display_name",
        "name",
        "description",
        "attitude",
        "rules",
        "assistant_directed_default",
        "language",
        "voice_id",
        "metadata",
    }
    return {key: value for key, value in payload.items() if key in allowed_keys}


@dataclass(slots=True)
class PersonasAdapter:
    """
    MCP-facing adapter for personas.

    Read-only.
    Exposes safe persona summaries and active persona id.
    """

    def _persona_service(self) -> PersonaService:
        personas_dir = _project_root() / "app" / "personas" / "profiles"
        return PersonaService(personas_dir)

    def list_personas(self) -> dict[str, Any]:
        service = self._persona_service()
        persona_ids = service.list_profiles()

        items: list[dict[str, Any]] = []
        for persona_id in persona_ids:
            profile = service.get_profile(persona_id)
            if profile is None:
                continue
            payload = _to_plain_data(profile)
            if isinstance(payload, dict):
                items.append(_sanitize_persona_payload(payload))

        return {
            "count": len(items),
            "items": items,
        }

    def get_persona(self, *, persona_id: str) -> dict[str, Any]:
        clean_persona_id = str(persona_id or "").strip()
        service = self._persona_service()
        profile = service.get_profile(clean_persona_id)

        if profile is None:
            return {
                "persona_id": clean_persona_id,
                "found": False,
                "item": None,
            }

        payload = _to_plain_data(profile)
        if isinstance(payload, dict):
            payload = _sanitize_persona_payload(payload)

        return {
            "persona_id": clean_persona_id,
            "found": True,
            "item": payload,
        }

    def get_active_persona_id(self) -> dict[str, Any]:
        system_runtime = _safe_load_json(_runtime_root() / "state" / "system_runtime.json")
        active_persona = str(system_runtime.get("active_persona") or "").strip()

        return {
            "active_persona_id": active_persona,
            "found": bool(active_persona),
        }