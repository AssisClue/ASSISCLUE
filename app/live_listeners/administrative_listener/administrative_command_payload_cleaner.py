from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


TEMP_KNOWLEDGE_DIR = Path("runtime/knowledge_library/parsed/temp")


FILLER_WORDS = {
    "please",
    "pls",
    "now",
    "okay",
    "ok",
    "hey",
    "can",
    "you",
    "could",
    "would",
    "just",
    "me",
    "for",
    "about",
    "on",
    "the",
    "this",
    "that",
    "a",
    "an",
    "to",
    "in",
}


COMMAND_PREFIXES = [
    "search web for",
    "search for",
    "look for",
    "find on web",
    "search",
    "save entire text as",
    "save full page text as",
    "save entire page text as",
    "save visible text as",
    "save page text as",
    "save text as",
]


def clean_payload_text(text: str) -> str:
    value = str(text or "").strip()
    value = _strip_command_prefix(value)
    value = _remove_edge_noise(value)
    value = _remove_filler_edges(value)
    value = _collapse_spaces(value)
    return value


def clean_search_payload(text: str) -> str:
    value = clean_payload_text(text)
    value = value.strip(" \"'`.,:;!?|/\\")
    return _collapse_spaces(value)


def clean_filename_payload(text: str, fallback_prefix: str = "browser_saved_text") -> str:
    value = clean_payload_text(text)
    value = value.strip(" \"'`.,:;!?|/\\")
    value = value.lower()
    value = re.sub(r"[^a-z0-9\-_\s]+", "", value)
    value = re.sub(r"\s+", "_", value).strip("_")

    if not value:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        value = f"{fallback_prefix}_{stamp}"

    return value[:80]


def build_temp_text_path(filename_payload: str) -> Path:
    safe_name = clean_filename_payload(filename_payload)
    TEMP_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    return TEMP_KNOWLEDGE_DIR / f"{safe_name}.txt"


def _strip_command_prefix(text: str) -> str:
    value = str(text or "").strip()
    lowered = value.lower()

    for prefix in sorted(COMMAND_PREFIXES, key=len, reverse=True):
        if lowered.startswith(prefix):
            return value[len(prefix):].strip()

    return value


def _remove_edge_noise(text: str) -> str:
    return str(text or "").strip(" \n\r\t\"'`.,:;!?|/\\()[]{}")


def _remove_filler_edges(text: str) -> str:
    parts = str(text or "").split()

    while parts and parts[0].lower().strip(".,:;!?") in FILLER_WORDS:
        parts.pop(0)

    while parts and parts[-1].lower().strip(".,:;!?") in FILLER_WORDS:
        parts.pop()

    return " ".join(parts)


def _collapse_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()