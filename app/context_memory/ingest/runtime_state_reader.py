from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.context_memory.contracts.input_types import RuntimeStateInput


@dataclass(slots=True)
class RuntimeStateReader:
    state_paths: dict[str, str | Path] = field(default_factory=dict)

    def read(self) -> list[RuntimeStateInput]:
        items: list[RuntimeStateInput] = []

        for source_name, raw_path in self.state_paths.items():
            path = Path(raw_path)
            if not path.exists() or not path.is_file():
                continue

            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            if not isinstance(payload, dict):
                continue

            items.append(
                RuntimeStateInput(
                    source_name=str(source_name).strip() or "runtime_state",
                    payload=payload,
                    ts=self._get_mtime(path),
                )
            )

        return items

    @staticmethod
    def _get_mtime(path: Path) -> float | None:
        try:
            return path.stat().st_mtime
        except OSError:
            return None