from __future__ import annotations

from typing import Any

from app.system_support.commands.command_catalog_loader import (
    load_administrative_command_catalog,
)


def _normalize_text(text: str) -> str:
    return " ".join(str(text or "").strip().lower().split())


def match_administrative_command(text: str) -> dict[str, Any] | None:
    normalized_text = _normalize_text(text)
    if not normalized_text:
        return None

    catalog = load_administrative_command_catalog()

    best_match: dict[str, Any] | None = None
    best_alias_length = -1

    for section in catalog:
        section_name = str(section.get("section") or "").strip()
        commands = section.get("commands", [])
        if not isinstance(commands, list):
            continue

        for command in commands:
            if not isinstance(command, dict):
                continue

            aliases = command.get("aliases", [])
            if not isinstance(aliases, list):
                continue

            for alias in aliases:
                normalized_alias = _normalize_text(alias)
                if not normalized_alias:
                    continue

                if normalized_text == normalized_alias or normalized_text.startswith(f"{normalized_alias} "):
                    if len(normalized_alias) > best_alias_length:
                        payload_text = normalized_text[len(normalized_alias):].strip()
                        best_alias_length = len(normalized_alias)
                        best_match = {
                            "section": section_name,
                            "command_id": str(command.get("command_id") or "").strip(),
                            "action_name": str(command.get("action_name") or "").strip(),
                            "capability_id": str(command.get("capability_id") or "").strip(),
                            "requires_wakeword": bool(command.get("requires_wakeword", False)),
                            "allow_without_wakeword": bool(command.get("allow_without_wakeword", False)),
                            "matched_alias": normalized_alias,
                            "raw_text": str(text or "").strip(),
                            "normalized_text": normalized_text,
                            "payload_text": payload_text,
                            "is_browser_command": section_name == "BROWSER_CONTROL",
                        }

    return best_match