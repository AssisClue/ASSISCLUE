from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.context_memory.contracts.input_types import EventInput


@dataclass(slots=True)
class SystemRuntimeEventReader:
    state_path: str | Path

    def read_if_updated(self, last_updated_at: float) -> tuple[list[EventInput], float]:
        path = Path(self.state_path)
        if not path.exists():
            return [], float(last_updated_at or 0.0)

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return [], float(last_updated_at or 0.0)

        if not isinstance(payload, dict):
            return [], float(last_updated_at or 0.0)

        updated_at = self._coerce_float(payload.get("updated_at")) or self._coerce_float(payload.get("started_at")) or 0.0
        if updated_at <= float(last_updated_at or 0.0):
            return [], float(last_updated_at or 0.0)

        text = self._build_text(payload)
        if not text:
            return [], updated_at

        item = EventInput(
            event_type="system_runtime_state",
            text=text,
            ts=updated_at,
            event_id=f"system_runtime_{int(updated_at)}",
            source="runtime_state",
            metadata={
                "status": str(payload.get("status") or "").strip(),
                "active_mode": str(payload.get("active_mode") or "").strip(),
                "active_persona": str(payload.get("active_persona") or "").strip(),
                "conversation_state": str(payload.get("conversation_state") or "").strip(),
            },
        )
        return [item], updated_at

    def _build_text(self, payload: dict) -> str:
        status = str(payload.get("status") or "unknown").strip()
        mode = str(payload.get("active_mode") or "unknown").strip()
        persona = str(payload.get("active_persona") or "unknown").strip()
        conversation_state = str(payload.get("conversation_state") or "unknown").strip()
        return (
            f"System runtime status is {status}. "
            f"Current mode is {mode}. "
            f"Active persona is {persona}. "
            f"Conversation state is {conversation_state}."
        ).strip()

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
