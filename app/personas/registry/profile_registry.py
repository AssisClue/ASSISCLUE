from __future__ import annotations

import json
from pathlib import Path

from app.personas.models.assistant_profile import AssistantProfile


class ProfileRegistry:
    def __init__(self, profiles_dir: Path) -> None:
        self._profiles_dir = Path(profiles_dir)

    def list_persona_ids(self) -> list[str]:
        persona_ids: list[str] = []
        for path in sorted(self._profiles_dir.glob("*.json")):
            persona_id = path.stem.strip()
            if persona_id:
                persona_ids.append(persona_id)
        return persona_ids

    def load_profile(self, persona_id: str) -> AssistantProfile | None:
        cleaned_id = str(persona_id or "").strip().lower()
        if not cleaned_id:
            return None

        path = self._profiles_dir / f"{cleaned_id}.json"
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            return None

        return AssistantProfile(
            persona_id=str(payload.get("persona_id") or cleaned_id).strip(),
            display_name=str(payload.get("display_name") or cleaned_id.title()).strip(),
            system_prompt=str(payload.get("system_prompt") or "").strip(),
            style_prompt=str(payload.get("style_prompt") or "").strip(),
            attitude=str(payload.get("attitude") or "").strip(),
            rules=[str(rule).strip() for rule in list(payload.get("rules") or []) if str(rule).strip()],
            metadata=dict(payload.get("metadata") or {}),
        )
