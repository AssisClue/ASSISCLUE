from __future__ import annotations

from typing import Any

from app.system_support.commands.command_catalog_loader import (
    load_administrative_command_catalog,
)

from .administrative_command_cleaner import normalize_administrative_command_text


def _clean_payload_text(payload_text: str) -> str:
    clean = str(payload_text or "").strip()

    while clean.startswith((":", ",", ";", "-", '"', "'")):
        clean = clean[1:].strip()

    while clean.endswith(('"', "'")):
        clean = clean[:-1].strip()

    return clean


def match_administrative_command(text: str) -> dict[str, Any] | None:
    normalized_text = normalize_administrative_command_text(text)
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
                normalized_alias = normalize_administrative_command_text(alias)
                if not normalized_alias:
                    continue

                alias_found = False
                payload_text = ""

                if normalized_text == normalized_alias:
                    alias_found = True
                    payload_text = ""
                elif normalized_text.startswith(f"{normalized_alias} "):
                    alias_found = True
                    payload_text = normalized_text[len(normalized_alias):].strip()
                elif normalized_text.startswith(f"{normalized_alias}:"):
                    alias_found = True
                    payload_text = normalized_text[len(normalized_alias):].strip()
                elif f" {normalized_alias} " in f" {normalized_text} ":
                    alias_found = True
                    payload_text = normalized_text.split(normalized_alias, 1)[1].strip()

                if not alias_found:
                    continue

                payload_text = _clean_payload_text(payload_text)

                if len(normalized_alias) > best_alias_length:
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