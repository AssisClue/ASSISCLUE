from __future__ import annotations

from app.system_support.commands.command_confirmation_policy import should_require_confirmation
from app.system_support.commands.command_contract import (
    ACTION_ALIASES,
    DEFAULT_TARGET_BY_ACTION,
    TARGET_ALIASES,
    VALID_ACTIONS,
    VALID_TARGETS,
)
from app.system_support.commands.command_models import ParsedCommand


def parse_command(text: str) -> ParsedCommand:
    raw_text = (text or "").strip()
    lowered = raw_text.lower()

    command = ParsedCommand(source_text=raw_text)

    if not raw_text:
        command.errors.append("Empty command text.")
        return command

    words = lowered.split()

    action, action_token = _find_action(words)
    target, target_token = _find_target(words)

    if not action:
        command.errors.append("Could not detect action.")
    else:
        command.action = action

    if not target and action:
        target = DEFAULT_TARGET_BY_ACTION.get(action, "")

    if not target:
        command.errors.append("Could not detect target.")
    else:
        command.target = target

    command.payload.item_name = _extract_item_name(raw_text)
    command.payload.text = _extract_payload_text(raw_text, action_token, target_token)
    command.destination.folder = _extract_folder(lowered)
    command.destination.space = _extract_space(lowered)

    command.confidence = _estimate_confidence(command)
    command.requires_confirmation = should_require_confirmation(command)

    return command


def _find_action(words: list[str]) -> tuple[str, str]:
    for word in words:
        normalized = ACTION_ALIASES.get(word)
        if normalized in VALID_ACTIONS:
            return normalized, word
    return "", ""


def _find_target(words: list[str]) -> tuple[str, str]:
    for word in words:
        normalized = TARGET_ALIASES.get(word)
        if normalized in VALID_TARGETS:
            return normalized, word
    return "", ""


def _extract_payload_text(raw_text: str, action_token: str, target_token: str) -> str:
    if not raw_text:
        return ""

    words = raw_text.split()
    cleaned_words: list[str] = []
    removed_action = False
    removed_target = False

    for word in words:
        normalized_word = word.strip(" ,:.-").lower()
        if not removed_action and action_token and normalized_word == action_token:
            removed_action = True
            continue
        if not removed_target and target_token and normalized_word == target_token:
            removed_target = True
            continue
        cleaned_words.append(word)

    payload = " ".join(cleaned_words).strip(" :,-")
    while True:
        lowered = payload.lower()
        for prefix in ("a ", "an ", "the ", "to ", "named ", "called "):
            if lowered.startswith(prefix):
                payload = payload[len(prefix) :].strip()
                break
        else:
            break

    payload = _remove_named_or_called_suffix(payload)
    payload = _remove_destination_suffix(payload, marker="folder ")
    payload = _remove_destination_suffix(payload, marker="in ")
    return payload


def _extract_item_name(raw_text: str) -> str:
    lowered = raw_text.lower()
    for marker in (" called ", " named "):
        if marker in lowered:
            value = raw_text[lowered.index(marker) + len(marker) :].strip(" :,-")
            value = _truncate_before_destination(value)
            return value.strip()
    return ""


def _extract_folder(lowered_text: str) -> str:
    marker = "folder "
    if marker in lowered_text:
        return lowered_text.split(marker, 1)[1].split()[0].strip(" ,:.-")
    return ""


def _extract_space(lowered_text: str) -> str:
    marker = "in "
    if marker in lowered_text:
        return lowered_text.split(marker, 1)[1].split()[0].strip(" ,:.-")
    return ""


def _remove_named_or_called_suffix(payload_text: str) -> str:
    lowered = payload_text.lower()
    cut_positions = [
        lowered.find(marker)
        for marker in (" called ", " named ")
        if marker in lowered
    ]
    if not cut_positions:
        return payload_text.strip()
    cut_index = min(position for position in cut_positions if position >= 0)
    return payload_text[:cut_index].strip(" :,-")


def _remove_destination_suffix(payload_text: str, *, marker: str) -> str:
    lowered = payload_text.lower()
    if marker not in lowered:
        return payload_text.strip()
    return payload_text[: lowered.index(marker)].strip(" :,-")


def _truncate_before_destination(value: str) -> str:
    lowered = value.lower()
    cut_positions = [
        lowered.find(marker)
        for marker in (" folder ", " in ")
        if marker in lowered
    ]
    if not cut_positions:
        return value.strip()
    cut_index = min(position for position in cut_positions if position >= 0)
    return value[:cut_index].strip(" :,-")


def _estimate_confidence(command: ParsedCommand) -> float:
    if command.errors:
        return 0.2
    if command.action and command.target and command.payload.text:
        return 0.95
    if command.action and command.target:
        return 0.8
    return 0.4
