from __future__ import annotations

from pathlib import Path

from app.system_support.commands.command_contract import (
    ACTION_ADD,
    ACTION_CHANGE,
    ACTION_MOVE,
    ACTION_REMOVE,
    ACTION_RENAME,
)
from app.system_support.commands.command_handlers import get_handler
from app.system_support.commands.command_parser import parse_command
from app.system_support.commands.command_result_builder import (
    build_confirmation_result,
    build_error_result,
    build_ok_result,
)
from app.system_support.system_runtime_state import is_edit_mode_active, set_edit_mode
from app.system_support.commands.command_target_registry import is_action_allowed_for_target


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MUTATION_ACTIONS = {
    ACTION_ADD,
    ACTION_CHANGE,
    ACTION_REMOVE,
    ACTION_MOVE,
    ACTION_RENAME,
}


def run_command(text: str, *, project_root: str | Path | None = None):
    # 1) Parse
    resolved_project_root = Path(project_root) if project_root is not None else PROJECT_ROOT
    command = parse_command(text)

    if not command.is_valid:
        return build_error_result(
            command=command,
            message="Command parsing failed.",
            errors=command.errors,
        )

    # 2) Action/target validation
    if not is_action_allowed_for_target(command.action, command.target):
        return build_error_result(
            command=command,
            message=f"Action '{command.action}' is not allowed for target '{command.target}'.",
            errors=[f"Unsupported action/target pair: {command.action}/{command.target}"],
        )

    # 3) Edit mode gate (mutations only)
    mutation_requires_edit_mode = command.action in MUTATION_ACTIONS
    if mutation_requires_edit_mode:
        if not is_edit_mode_active(resolved_project_root):
            return build_error_result(
                command=command,
                message="Edit mode required before mutation commands.",
                errors=["edit_mode_required"],
            )

    # 4) Confirmation check
    # Policy:
    # - confirmation-required mutations (e.g. remove) MUST pass edit-mode gate first
    # - but edit mode is NOT consumed here because no mutation has executed yet
    if command.requires_confirmation:
        return build_confirmation_result(
            command=command,
            message=f"Confirmation required for {command.action} on {command.target}.",
        )

    # 5) Handler execution
    handler = get_handler(command.target)
    if handler is None:
        return build_error_result(
            command=command,
            message=f"No handler found for target '{command.target}'.",
            errors=[f"Missing handler for target: {command.target}"],
        )

    try:
        handler_output = handler(command)
    except Exception as exc:
        return build_error_result(
            command=command,
            message=f"Handler execution failed for target '{command.target}'.",
            errors=[f"{type(exc).__name__}: {exc}"],
        )

    if not isinstance(handler_output, dict):
        return build_error_result(
            command=command,
            message="Handler returned unexpected output type.",
            errors=[f"invalid_handler_output:{type(handler_output).__name__}"],
        )

    # 6) Normalized result
    message = str(handler_output.get("message", "Command executed.")).strip() or "Command executed."
    handler_ok = bool(handler_output.get("ok", True))
    if not handler_ok:
        raw_errors = handler_output.get("errors")
        errors: list[str] = []
        if isinstance(raw_errors, list):
            errors = [str(item).strip() for item in raw_errors if str(item).strip()]
        error_code = str(handler_output.get("error_code", "")).strip()
        if error_code and error_code not in errors:
            errors.append(error_code)
        return build_error_result(
            command=command,
            message=message or "Command handler reported an error.",
            errors=errors,
        )

    if mutation_requires_edit_mode:
        set_edit_mode(resolved_project_root, active=False)

    return build_ok_result(
        command=command,
        message=message,
        data=handler_output,
    )
