from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import importlib


def _to_plain_data(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, list):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, tuple):
        return [_to_plain_data(item) for item in value]

    if isinstance(value, dict):
        return {str(key): _to_plain_data(val) for key, val in value.items()}

    if hasattr(value, "__dataclass_fields__"):
        result: dict[str, Any] = {}
        for field_name in value.__dataclass_fields__.keys():
            result[field_name] = _to_plain_data(getattr(value, field_name))
        return result

    if hasattr(value, "__dict__"):
        raw = vars(value)
        return {str(key): _to_plain_data(val) for key, val in raw.items()}

    return str(value)


@dataclass(slots=True)
class CapabilitiesAdapter:
    """
    MCP-facing adapter for app capabilities.

    Read-only.
    Uses tolerant imports because the capability block names may differ.
    """

    def _load_default_capabilities(self) -> list[Any]:
        module = importlib.import_module("app.capabilities.default_capabilities")

        candidate_names = [
            "build_default_capabilities",
            "get_default_capabilities",
            "create_default_capabilities",
            "DEFAULT_CAPABILITIES",
            "default_capabilities",
        ]

        for name in candidate_names:
            if not hasattr(module, name):
                continue

            value = getattr(module, name)

            if callable(value):
                try:
                    result = value()
                except TypeError:
                    continue
                if isinstance(result, list):
                    return result

            if isinstance(value, list):
                return value

        return []

    def _extract_action_name(self, item: Any) -> str:
        if item is None:
            return ""

        if isinstance(item, dict):
            return str(item.get("action_name", "") or "").strip()

        for attr_name in ("action_name", "name", "capability_name", "id"):
            if hasattr(item, attr_name):
                value = str(getattr(item, attr_name) or "").strip()
                if value:
                    return value

        return ""

    def list_capabilities(self) -> dict[str, Any]:
        items = self._load_default_capabilities()

        plain_items = [_to_plain_data(item) for item in items]

        return {
            "count": len(plain_items),
            "items": plain_items,
        }

    def get_capability_by_action_name(self, *, action_name: str) -> dict[str, Any]:
        clean_action_name = str(action_name or "").strip()
        items = self._load_default_capabilities()

        matched_item: Any | None = None
        for item in items:
            if self._extract_action_name(item) == clean_action_name:
                matched_item = item
                break

        return {
            "action_name": clean_action_name,
            "found": matched_item is not None,
            "item": _to_plain_data(matched_item) if matched_item is not None else None,
        }