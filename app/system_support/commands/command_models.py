from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CommandPayload:
    text: str = ""
    item_id: str = ""
    item_name: str = ""
    patch: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CommandDestination:
    space: str = ""
    folder: str = ""


@dataclass(slots=True)
class ParsedCommand:
    source_text: str
    action: str = ""
    target: str = ""
    payload: CommandPayload = field(default_factory=CommandPayload)
    destination: CommandDestination = field(default_factory=CommandDestination)
    options: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    requires_confirmation: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors and bool(self.action and self.target)


@dataclass(slots=True)
class CommandResult:
    ok: bool
    message: str
    action: str = ""
    target: str = ""
    status: str = "ok"
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    requires_confirmation: bool = False