from __future__ import annotations

from typing import Any

from app.live_listeners.shared.listener_record_utils import get_record_ts

from .administrative_listener_config import (
    MOMENT_WINDOW_MAX_RECORDS,
    MOMENT_WINDOW_MAX_SECONDS,
)


class MomentWindowBuilder:
    def __init__(
        self,
        *,
        max_records: int = MOMENT_WINDOW_MAX_RECORDS,
        max_seconds: float = MOMENT_WINDOW_MAX_SECONDS,
    ) -> None:
        self.max_records = max_records
        self.max_seconds = max_seconds

    def build_window(
        self,
        current_window: list[dict[str, Any]],
        new_record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        records = [*current_window, new_record]

        if len(records) > self.max_records:
            records = records[-self.max_records :]

        newest_ts = get_record_ts(new_record)
        if newest_ts is None:
            return records

        filtered: list[dict[str, Any]] = []
        for record in records:
            record_ts = get_record_ts(record)
            if record_ts is None:
                continue
            if newest_ts - record_ts <= self.max_seconds:
                filtered.append(record)

        return filtered