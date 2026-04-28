from __future__ import annotations

from app.system_support.commands.command_contract import (
    ACTION_ACTIVATE,
    ACTION_ADD,
    ACTION_CHANGE,
    ACTION_LIST,
    ACTION_MOVE,
    ACTION_READ,
    ACTION_REMOVE,
    ACTION_RENAME,
    TARGET_HELP,
    TARGET_MEMORY,
    TARGET_NOTES,
    TARGET_PERSONA,
    TARGET_PROJECTS,
    TARGET_PROMPTS,
    TARGET_RULES,
    TARGET_SOURCE_EVIDENCE,
    TARGET_STATE,
)


TARGET_ACTIONS: dict[str, set[str]] = {
    TARGET_NOTES: {
        ACTION_ADD,
        ACTION_CHANGE,
        ACTION_REMOVE,
        ACTION_READ,
        ACTION_LIST,
        ACTION_MOVE,
        ACTION_RENAME,
    },
    TARGET_RULES: {
        ACTION_ADD,
        ACTION_CHANGE,
        ACTION_REMOVE,
        ACTION_READ,
        ACTION_LIST,
        ACTION_MOVE,
        ACTION_RENAME,
    },
    TARGET_PROMPTS: {
        ACTION_ADD,
        ACTION_CHANGE,
        ACTION_REMOVE,
        ACTION_READ,
        ACTION_LIST,
        ACTION_MOVE,
        ACTION_RENAME,
    },
    TARGET_PROJECTS: {
        ACTION_ADD,
        ACTION_CHANGE,
        ACTION_REMOVE,
        ACTION_READ,
        ACTION_LIST,
        ACTION_MOVE,
        ACTION_RENAME,
    },
    TARGET_HELP: {
        ACTION_READ,
        ACTION_LIST,
    },
    TARGET_PERSONA: {
        ACTION_READ,
        ACTION_LIST,
        ACTION_CHANGE,
        ACTION_ACTIVATE,
    },
    TARGET_STATE: {
        ACTION_READ,
        ACTION_LIST,
    },
    TARGET_MEMORY: {
        ACTION_READ,
        ACTION_LIST,
    },
    TARGET_SOURCE_EVIDENCE: {
        ACTION_READ,
        ACTION_LIST,
    },
}


def is_action_allowed_for_target(action: str, target: str) -> bool:
    allowed_actions = TARGET_ACTIONS.get(target, set())
    return action in allowed_actions


def get_allowed_actions_for_target(target: str) -> set[str]:
    return TARGET_ACTIONS.get(target, set())