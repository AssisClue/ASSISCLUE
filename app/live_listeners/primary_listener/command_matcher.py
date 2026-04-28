from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.capabilities import find_capability_by_action_name, find_capability_by_id
from app.system_support.commands.command_contract import ACTION_ACTIVATE, ACTION_ADD, ACTION_REMOVE
from app.system_support.commands.command_parser import parse_command

from .primary_listener_config import COMMAND_CATALOG_PATH
from .wakeword_matcher import normalize_text
from .matcher_vocabulary import fuzzy_token_match


_COMMAND_CATALOG_CACHE: list[dict[str, Any]] = []
_COMMAND_CATALOG_CACHE_PATH: Path | None = None
_COMMAND_CATALOG_CACHE_MTIME: float | None = None


def _flatten_commands(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []

    flattened: list[dict[str, Any]] = []

    for section in payload:
        if not isinstance(section, dict):
            continue

        commands = section.get("commands", [])
        if not isinstance(commands, list):
            continue

        for command in commands:
            if isinstance(command, dict):
                flattened.append(command)

    return flattened


def load_command_catalog() -> list[dict[str, Any]]:
    global _COMMAND_CATALOG_CACHE
    global _COMMAND_CATALOG_CACHE_PATH
    global _COMMAND_CATALOG_CACHE_MTIME

    if not COMMAND_CATALOG_PATH.exists():
        _COMMAND_CATALOG_CACHE = []
        _COMMAND_CATALOG_CACHE_PATH = COMMAND_CATALOG_PATH
        _COMMAND_CATALOG_CACHE_MTIME = None
        return []

    try:
        current_mtime = COMMAND_CATALOG_PATH.stat().st_mtime
    except Exception:
        current_mtime = None

    if (
        _COMMAND_CATALOG_CACHE_PATH == COMMAND_CATALOG_PATH
        and _COMMAND_CATALOG_CACHE_MTIME == current_mtime
    ):
        return list(_COMMAND_CATALOG_CACHE)

    try:
        payload = json.loads(COMMAND_CATALOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        _COMMAND_CATALOG_CACHE = []
        _COMMAND_CATALOG_CACHE_PATH = COMMAND_CATALOG_PATH
        _COMMAND_CATALOG_CACHE_MTIME = current_mtime
        return []

    _COMMAND_CATALOG_CACHE = _flatten_commands(payload)
    _COMMAND_CATALOG_CACHE_PATH = COMMAND_CATALOG_PATH
    _COMMAND_CATALOG_CACHE_MTIME = current_mtime
    return list(_COMMAND_CATALOG_CACHE)


def _sorted_aliases(command_item: dict[str, Any]) -> list[str]:
    aliases = command_item.get("aliases", [])
    if not isinstance(aliases, list):
        return []

    normalized_aliases = []
    for alias in aliases:
        alias_normalized = normalize_text(str(alias))
        if alias_normalized:
            normalized_aliases.append(alias_normalized)

    return sorted(normalized_aliases, key=len, reverse=True)


def _matches_alias(cleaned_text: str, alias: str) -> bool:
    if cleaned_text == alias:
        return True

    allowed_suffixes = (
        " now",
        " please",
        " for me",
    )

    for suffix in allowed_suffixes:
        if cleaned_text == f"{alias}{suffix}":
            return True

    text_words = cleaned_text.split()
    alias_words = alias.split()
    if not alias_words or len(alias_words) > len(text_words):
        return False

    for start_index in range(0, len(text_words) - len(alias_words) + 1):
        ok = True
        for idx, alias_word in enumerate(alias_words):
            current = text_words[start_index + idx]
            if current == alias_word:
                continue
            if not fuzzy_token_match(current, alias_word):
                ok = False
                break
        if ok:
            return True

    return False


def _matches_alias_exact_only(cleaned_text: str, alias: str) -> bool:
    cleaned_text = normalize_text(cleaned_text)
    alias = normalize_text(alias)
    if not cleaned_text or not alias:
        return False
    if cleaned_text == alias:
        return True
    for suffix in (" now", " please", " for me"):
        if cleaned_text == f"{alias}{suffix}":
            return True
    return False


def match_command(text: str, *, wakeword_found: bool) -> dict[str, Any] | None:
    cleaned_text = normalize_text(text)
    if not cleaned_text:
        return None

    for item in load_command_catalog():
        requires_wakeword = bool(item.get("requires_wakeword", True))
        allow_without_wakeword = bool(item.get("allow_without_wakeword", False))

        if requires_wakeword and not wakeword_found and not allow_without_wakeword:
            continue

        for alias_normalized in _sorted_aliases(item):
            if not _matches_alias(cleaned_text, alias_normalized):
                continue

            if str(item.get("action_name", "")).strip() == "stop_talking" and not _matches_alias_exact_only(
                cleaned_text, alias_normalized
            ):
                continue

            capability = None
            capability_id = str(item.get("capability_id", "")).strip()
            if capability_id:
                capability = find_capability_by_id(capability_id)
            if capability is None:
                capability = find_capability_by_action_name(str(item.get("action_name", "")).strip())

            matched: dict[str, Any] = {
                "command_id": str(item.get("command_id", "")).strip(),
                "action_name": str(item.get("action_name", "")).strip(),
                "matched_alias": alias_normalized,
                "requires_wakeword": requires_wakeword,
                "allow_without_wakeword": allow_without_wakeword,
            }
            if capability is not None:
                matched["capability"] = {
                    "capability_id": capability.capability_id,
                    "block_id": capability.block_id,
                    "handler_key": capability.handler_key,
                }
            return matched

    # Fallback to command core parser when catalog aliases do not match.
    parsed = parse_command(cleaned_text)
    if (
        parsed.is_valid
        and parsed.confidence >= 0.8
        and parsed.action in {ACTION_ADD, ACTION_ACTIVATE, ACTION_REMOVE}
    ):
        if parsed.action in {ACTION_ACTIVATE, ACTION_REMOVE} and not wakeword_found:
            return None

        return {
            "command_id": "command_core",
            "action_name": "command_core",
            "matched_alias": cleaned_text,
            "requires_wakeword": parsed.action in {ACTION_ACTIVATE, ACTION_REMOVE},
            "allow_without_wakeword": parsed.action not in {ACTION_ACTIVATE, ACTION_REMOVE},
            "command_core": {
                "action": parsed.action,
                "target": parsed.target,
                "payload_text": parsed.payload.text,
                "item_name": parsed.payload.item_name,
                "destination_space": parsed.destination.space,
                "destination_folder": parsed.destination.folder,
                "confidence": parsed.confidence,
            },
        }

    return None
