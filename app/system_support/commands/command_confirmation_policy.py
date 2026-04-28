from __future__ import annotations

from app.system_support.commands.command_contract import (
    ACTION_CHANGE,
    ACTION_MOVE,
    ACTION_REMOVE,
    ACTION_RENAME,
)
from app.system_support.commands.command_models import ParsedCommand


def should_require_confirmation(command: ParsedCommand) -> bool:
    if command.action == ACTION_REMOVE:
        return True

    if command.action in {ACTION_MOVE, ACTION_RENAME}:
        return True

    if command.action == ACTION_CHANGE and bool(command.payload.patch):
        return True

    return False