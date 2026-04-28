from __future__ import annotations

import json
from pathlib import Path

from app.personas.models.assistant_profile import AssistantProfile
from app.personas.registry.profile_registry import ProfileRegistry
from app.system_support.system_runtime_state import read_system_runtime_state, write_system_runtime_state


class PersonaService:
    def __init__(self, profiles_dir: Path | None = None) -> None:
        base_dir = Path(__file__).resolve().parents[1]
        self._profiles_dir = Path(profiles_dir) if profiles_dir is not None else base_dir / "profiles"
        self._registry = ProfileRegistry(self._profiles_dir)

    def list_profiles(self) -> list[str]:
        return self._registry.list_persona_ids()

    def get_profile(self, persona_id: str) -> AssistantProfile | None:
        return self._registry.load_profile(persona_id)

    def get_active_profile(self, persona_id: str, *, default_persona_id: str = "rick") -> AssistantProfile:
        requested = self.get_profile(persona_id)
        if requested is not None:
            return requested

        fallback = self.get_profile(default_persona_id)
        if fallback is not None:
            return fallback

        available = ", ".join(self.list_profiles()) or "none"
        raise ValueError(f"No assistant profile available for '{persona_id}'. Available: {available}")

    def is_assistant_directed_by_default(self, persona_id: str, *, default_persona_id: str = "rick") -> bool:
        profile_payload = self._load_profile_payload(persona_id)
        if profile_payload is None and default_persona_id:
            profile_payload = self._load_profile_payload(default_persona_id)
        if not isinstance(profile_payload, dict):
            return False
        return bool(profile_payload.get("assistant_directed_default", False))

    def get_active_persona_id(self, project_root: Path, *, default_persona_id: str = "rick") -> str:
        payload = read_system_runtime_state(project_root) or {}
        persona_id = str(payload.get("active_persona") or default_persona_id).strip().lower()
        return persona_id or default_persona_id

    def is_active_persona_assistant_directed(
        self,
        project_root: Path,
        *,
        default_persona_id: str = "rick",
    ) -> bool:
        persona_id = self.get_active_persona_id(project_root, default_persona_id=default_persona_id)
        return self.is_assistant_directed_by_default(
            persona_id,
            default_persona_id=default_persona_id,
        )

    def activate_persona(
        self,
        *,
        project_root: Path,
        persona_id: str,
        default_persona_id: str = "rick",
    ) -> dict:
        requested = str(persona_id or "").strip().lower()
        if requested in {"default", "persona_default"}:
            requested = default_persona_id

        if not requested:
            return {
                "ok": False,
                "error_code": "empty_persona_id",
                "message": "Persona id is empty.",
            }

        profile = self.get_profile(requested)
        if profile is None:
            return {
                "ok": False,
                "error_code": "unknown_persona",
                "message": f"Persona '{requested}' was not found.",
            }

        write_system_runtime_state(project_root, {"active_persona": profile.persona_id})
        return {
            "ok": True,
            "active_persona": profile.persona_id,
        }

    def _load_profile_payload(self, persona_id: str) -> dict | None:
        cleaned_id = str(persona_id or "").strip().lower()
        if not cleaned_id:
            return None

        path = self._profiles_dir / f"{cleaned_id}.json"
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
        return None
