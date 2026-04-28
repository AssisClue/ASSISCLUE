from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CATALOGS_DIR = Path(__file__).resolve().parent / "catalogs"
ADMINISTRATIVE_CORE_COMMANDS_JSON = CATALOGS_DIR / "administrative_core_commands.json"
ADMINISTRATIVE_WEB_COMMANDS_JSON = CATALOGS_DIR / "administrative_web_commands.json"


def _read_catalog(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return []

    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"Command catalog must be a list: {path}")

    normalized: list[dict[str, Any]] = []
    for section in data:
        if not isinstance(section, dict):
            continue

        section_name = str(section.get("section") or "").strip()
        commands = section.get("commands", [])

        if not isinstance(commands, list):
            commands = []

        normalized_commands: list[dict[str, Any]] = []
        for item in commands:
            if not isinstance(item, dict):
                continue

            normalized_commands.append(
                {
                    "command_id": str(item.get("command_id") or "").strip(),
                    "action_name": str(item.get("action_name") or "").strip(),
                    "capability_id": str(item.get("capability_id") or "").strip(),
                    "requires_wakeword": bool(item.get("requires_wakeword", False)),
                    "allow_without_wakeword": bool(item.get("allow_without_wakeword", False)),
                    "aliases": [
                        str(alias).strip()
                        for alias in item.get("aliases", [])
                        if str(alias).strip()
                    ],
                }
            )

        normalized.append(
            {
                "section": section_name,
                "commands": normalized_commands,
            }
        )

    return normalized


def load_administrative_core_command_catalog() -> list[dict[str, Any]]:
    return _read_catalog(ADMINISTRATIVE_CORE_COMMANDS_JSON)


def load_administrative_web_command_catalog() -> list[dict[str, Any]]:
    return _read_catalog(ADMINISTRATIVE_WEB_COMMANDS_JSON)


def load_administrative_command_catalog() -> list[dict[str, Any]]:
    return (
        load_administrative_core_command_catalog()
        + load_administrative_web_command_catalog()
    )

