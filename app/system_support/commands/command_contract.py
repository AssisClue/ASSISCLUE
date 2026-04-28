from __future__ import annotations

from typing import Final


ACTION_ADD: Final[str] = "add"
ACTION_CHANGE: Final[str] = "change"
ACTION_REMOVE: Final[str] = "remove"
ACTION_READ: Final[str] = "read"
ACTION_LIST: Final[str] = "list"
ACTION_MOVE: Final[str] = "move"
ACTION_RENAME: Final[str] = "rename"
ACTION_ACTIVATE: Final[str] = "activate"

VALID_ACTIONS: Final[set[str]] = {
    ACTION_ADD,
    ACTION_CHANGE,
    ACTION_REMOVE,
    ACTION_READ,
    ACTION_LIST,
    ACTION_MOVE,
    ACTION_RENAME,
    ACTION_ACTIVATE,
}

TARGET_NOTES: Final[str] = "notes"
TARGET_RULES: Final[str] = "rules"
TARGET_PROMPTS: Final[str] = "prompts"
TARGET_PROJECTS: Final[str] = "projects"
TARGET_HELP: Final[str] = "help"
TARGET_PERSONA: Final[str] = "persona"
TARGET_STATE: Final[str] = "state"
TARGET_MEMORY: Final[str] = "memory"
TARGET_SOURCE_EVIDENCE: Final[str] = "source_evidence"

VALID_TARGETS: Final[set[str]] = {
    TARGET_NOTES,
    TARGET_RULES,
    TARGET_PROMPTS,
    TARGET_PROJECTS,
    TARGET_HELP,
    TARGET_PERSONA,
    TARGET_STATE,
    TARGET_MEMORY,
    TARGET_SOURCE_EVIDENCE,
}

# Alias simples para normalizar lenguaje natural.
ACTION_ALIASES: Final[dict[str, str]] = {
    "add": ACTION_ADD,
    "create": ACTION_ADD,
    "new": ACTION_ADD,
    "change": ACTION_CHANGE,
    "update": ACTION_CHANGE,
    "edit": ACTION_CHANGE,
    "modify": ACTION_CHANGE,
    "remove": ACTION_REMOVE,
    "delete": ACTION_REMOVE,
    "erase": ACTION_REMOVE,
    "read": ACTION_READ,
    "show": ACTION_READ,
    "tell": ACTION_READ,
    "get": ACTION_READ,
    "list": ACTION_LIST,
    "move": ACTION_MOVE,
    "rename": ACTION_RENAME,
    "activate": ACTION_ACTIVATE,
    "use": ACTION_ACTIVATE,
    "switch": ACTION_ACTIVATE,
}

TARGET_ALIASES: Final[dict[str, str]] = {
    "note": TARGET_NOTES,
    "notes": TARGET_NOTES,
    "rule": TARGET_RULES,
    "rules": TARGET_RULES,
    "prompt": TARGET_PROMPTS,
    "prompts": TARGET_PROMPTS,
    "project": TARGET_PROJECTS,
    "projects": TARGET_PROJECTS,
    "help": TARGET_HELP,
    "persona": TARGET_PERSONA,
    "state": TARGET_STATE,
    "memory": TARGET_MEMORY,
    "evidence": TARGET_SOURCE_EVIDENCE,
    "source": TARGET_SOURCE_EVIDENCE,
    "sources": TARGET_SOURCE_EVIDENCE,
}

DEFAULT_TARGET_BY_ACTION: Final[dict[str, str]] = {
    ACTION_ADD: TARGET_NOTES,
    ACTION_CHANGE: TARGET_NOTES,
    ACTION_REMOVE: TARGET_NOTES,
    ACTION_READ: TARGET_HELP,
    ACTION_LIST: TARGET_HELP,
    ACTION_ACTIVATE: TARGET_PERSONA,
}
