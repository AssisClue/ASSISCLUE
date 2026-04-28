from __future__ import annotations

from typing import Any


class AdministrativeCommandExecutionGuard:
    """
    Small in-memory dedupe guard for the running listener process.

    It avoids re-executing the exact same administrative command fingerprint
    when the same assembled paragraph/window is seen again.
    """

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def build_fingerprint(
        self,
        *,
        command: dict[str, Any],
        source_session_id: str,
        source_event_ids: list[str],
        paragraph: str,
    ) -> str:
        action_name = str(command.get("action_name") or "").strip()
        payload_text = str(command.get("payload_text") or "").strip()
        event_ids_key = "|".join(sorted(str(x).strip() for x in source_event_ids if str(x).strip()))
        session_key = str(source_session_id or "").strip()
        paragraph_key = str(paragraph or "").strip()

        return "||".join(
            [
                action_name,
                payload_text,
                session_key,
                event_ids_key,
                paragraph_key,
            ]
        )

    def should_execute(
        self,
        *,
        command: dict[str, Any],
        source_session_id: str,
        source_event_ids: list[str],
        paragraph: str,
    ) -> tuple[bool, str]:
        fingerprint = self.build_fingerprint(
            command=command,
            source_session_id=source_session_id,
            source_event_ids=source_event_ids,
            paragraph=paragraph,
        )

        if fingerprint in self._seen:
            return False, fingerprint

        self._seen.add(fingerprint)
        return True, fingerprint