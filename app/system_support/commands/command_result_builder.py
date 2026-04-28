from __future__ import annotations

from typing import Any

from app.system_support.commands.command_models import CommandResult, ParsedCommand


def build_ok_result(
    command: ParsedCommand,
    message: str,
    data: dict[str, Any] | None = None,
) -> CommandResult:
    return CommandResult(
        ok=True,
        message=message,
        action=command.action,
        target=command.target,
        status="ok",
        data=data or {},
        errors=[],
        requires_confirmation=command.requires_confirmation,
    )


def build_error_result(
    command: ParsedCommand,
    message: str,
    errors: list[str] | None = None,
) -> CommandResult:
    return CommandResult(
        ok=False,
        message=message,
        action=command.action,
        target=command.target,
        status="error",
        errors=errors or [],
        requires_confirmation=command.requires_confirmation,
    )


def build_confirmation_result(command: ParsedCommand, message: str) -> CommandResult:
    return CommandResult(
        ok=True,
        message=message,
        action=command.action,
        target=command.target,
        status="confirmation_required",
        errors=[],
        requires_confirmation=True,
    )
