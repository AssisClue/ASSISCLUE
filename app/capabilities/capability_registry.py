from __future__ import annotations

from .default_capabilities import DEFAULT_CAPABILITIES
from .capability_spec import CapabilitySpec


_BY_ID = {item.capability_id: item for item in DEFAULT_CAPABILITIES}
_BY_ACTION_NAME = {item.action_name: item for item in DEFAULT_CAPABILITIES}


def list_capabilities() -> list[CapabilitySpec]:
    return list(DEFAULT_CAPABILITIES)


def find_capability_by_id(capability_id: str) -> CapabilitySpec | None:
    return _BY_ID.get(str(capability_id or "").strip())


def find_capability_by_action_name(action_name: str) -> CapabilitySpec | None:
    return _BY_ACTION_NAME.get(str(action_name or "").strip())
