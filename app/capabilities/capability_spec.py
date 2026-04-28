from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CapabilitySpec:
    capability_id: str
    action_name: str
    block_id: str
    target_queue: str
    target_runner: str
    handler_key: str
    enabled: bool = True
