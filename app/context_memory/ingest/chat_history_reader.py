from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.context_memory.contracts.input_types import ChatMessageInput


@dataclass(slots=True)
class ChatHistoryReader:
    history_path: str | Path

    def read(self, limit: int | None = None) -> list[ChatMessageInput]:
        path = Path(self.history_path)
        if not path.exists():
            return []

        messages: list[ChatMessageInput] = []
        with path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue

                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = str(payload.get("text") or payload.get("content") or "").strip()
                if not text:
                    continue

                role = str(payload.get("role") or payload.get("speaker") or "unknown").strip() or "unknown"
                ts = self._coerce_float(payload.get("ts"))
                message_id = self._coerce_str(payload.get("message_id") or payload.get("id"))
                source = str(payload.get("source") or "chat_history").strip() or "chat_history"

                messages.append(
                    ChatMessageInput(
                        role=role,
                        text=text,
                        ts=ts,
                        message_id=message_id,
                        source=source,
                    )
                )

        if limit is not None and limit > 0:
            return messages[-limit:]
        return messages

    def read_from_offset(self, start_offset: int) -> tuple[list[ChatMessageInput], int]:
        path = Path(self.history_path)
        if not path.exists():
            return [], max(0, int(start_offset or 0))

        items: list[ChatMessageInput] = []
        current_offset = max(0, int(start_offset or 0))
        file_size = path.stat().st_size
        if current_offset > file_size:
            current_offset = file_size

        encoding = "utf-8-sig" if current_offset == 0 else "utf-8"
        with path.open("r", encoding=encoding) as handle:
            handle.seek(current_offset)
            while True:
                line_start = handle.tell()
                raw_line = handle.readline()
                if raw_line == "":
                    break
                if not raw_line.endswith("\n"):
                    handle.seek(line_start)
                    break

                current_offset = handle.tell()
                item = self._parse_line(raw_line)
                if item is not None:
                    items.append(item)

        return items, current_offset

    def _parse_line(self, raw_line: str) -> ChatMessageInput | None:
        line = raw_line.strip().lstrip("\ufeff")
        if not line:
            return None

        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            return None

        text = str(payload.get("text") or payload.get("content") or "").strip()
        if not text:
            return None

        role = str(payload.get("role") or payload.get("speaker") or "unknown").strip() or "unknown"
        ts = self._coerce_float(payload.get("ts"))
        message_id = self._coerce_str(payload.get("message_id") or payload.get("id"))
        source = str(payload.get("source") or "chat_history").strip() or "chat_history"

        return ChatMessageInput(
            role=role,
            text=text,
            ts=ts,
            message_id=message_id,
            source=source,
        )

    @staticmethod
    def _coerce_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_str(value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None
