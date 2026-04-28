from __future__ import annotations

from pathlib import Path

from app.context_memory.user_spaces.user_spaces_service import UserSpacesService
from app.personas.services.persona_service import PersonaService
from app.system_support.commands.command_contract import (
    ACTION_ACTIVATE,
    ACTION_ADD,
    ACTION_CHANGE,
    ACTION_LIST,
    ACTION_READ,
    ACTION_REMOVE,
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
from app.system_support.commands.command_models import ParsedCommand


def _not_implemented(message: str) -> dict:
    return {
        "ok": False,
        "message": message,
        "error_code": "not_implemented",
    }


def handle_notes(command: ParsedCommand) -> dict:
    if command.action == ACTION_ADD:
        note_text = str(command.payload.text or "").strip()
        if not note_text:
            return {
                "ok": False,
                "message": "Missing note text.",
                "error_code": "empty_note_text",
            }

        user_spaces = UserSpacesService.create_default()
        created = user_spaces.add_note(text=note_text, title=str(command.payload.item_name or "").strip())
        return {
            "ok": True,
            "message": "Note added.",
            "space_id": created.space_id,
            "item_id": created.item_id,
            "text": created.text,
        }
    if command.action == ACTION_READ:
        return _not_implemented("Reading notes is not implemented yet.")
    if command.action == ACTION_LIST:
        return _not_implemented("Listing notes is not implemented yet.")
    if command.action == ACTION_CHANGE:
        return _not_implemented("Changing notes is not implemented yet.")
    if command.action == ACTION_REMOVE:
        return _not_implemented("Removing notes is not implemented yet.")
    return _not_implemented("Notes command is not implemented yet for that action.")


def handle_rules(command: ParsedCommand) -> dict:
    return _not_implemented(f"Rules command is not implemented yet for action '{command.action}'.")


def handle_prompts(command: ParsedCommand) -> dict:
    return _not_implemented(f"Prompts command is not implemented yet for action '{command.action}'.")


def handle_projects(command: ParsedCommand) -> dict:
    return _not_implemented(f"Projects command is not implemented yet for action '{command.action}'.")


def handle_help(command: ParsedCommand) -> dict:
    return _not_implemented("Help command is not implemented yet.")


def handle_persona(command: ParsedCommand) -> dict:
    if command.action == ACTION_ACTIVATE:
        requested = str(command.payload.item_name or command.payload.text or "").strip().lower()
        if not requested:
            return {
                "ok": False,
                "message": "Missing persona name.",
                "error_code": "empty_persona_name",
            }

        project_root = Path(__file__).resolve().parents[3]
        persona_service = PersonaService(project_root / "app" / "personas" / "profiles")
        activation = persona_service.activate_persona(project_root=project_root, persona_id=requested)
        if not activation.get("ok", False):
            return {
                "ok": False,
                "message": str(activation.get("message") or "Persona activation failed."),
                "error_code": str(activation.get("error_code") or "persona_activation_failed"),
            }
        return {
            "ok": True,
            "message": f"Persona activated: {activation.get('active_persona', requested)}",
            "active_persona": str(activation.get("active_persona") or requested),
        }
    return _not_implemented(f"Persona command is not implemented yet for action '{command.action}'.")


def handle_state(command: ParsedCommand) -> dict:
    return _not_implemented("State read is not implemented yet.")


def handle_memory(command: ParsedCommand) -> dict:
    return _not_implemented("Memory read is not implemented yet.")


def handle_source_evidence(command: ParsedCommand) -> dict:
    return _not_implemented("Source evidence read is not implemented yet.")


HANDLER_MAP = {
    TARGET_NOTES: handle_notes,
    TARGET_RULES: handle_rules,
    TARGET_PROMPTS: handle_prompts,
    TARGET_PROJECTS: handle_projects,
    TARGET_HELP: handle_help,
    TARGET_PERSONA: handle_persona,
    TARGET_STATE: handle_state,
    TARGET_MEMORY: handle_memory,
    TARGET_SOURCE_EVIDENCE: handle_source_evidence,
}


def get_handler(target: str):
    return HANDLER_MAP.get(target)
