from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.system_support.runtime_jsonl import append_jsonl, read_new_runtime_jsonl_lines
from app.web_tools.browser.browser_service import (
    BROWSER_REQUEST_QUEUE_JSONL,
    BROWSER_RESULT_QUEUE_JSONL,
    ensure_browser_runtime_dirs,
)


def call_browser_service(action: str, payload: dict[str, Any] | None = None, *, timeout_seconds: float = 15.0) -> dict[str, Any]:
    ensure_browser_runtime_dirs()
    request_id = f"bsr_{uuid4().hex}"
    result_offset = Path(BROWSER_RESULT_QUEUE_JSONL).stat().st_size if Path(BROWSER_RESULT_QUEUE_JSONL).exists() else 0

    append_jsonl(
        BROWSER_REQUEST_QUEUE_JSONL,
        {
            "request_id": request_id,
            "ts": time.time(),
            "action": str(action or "").strip(),
            "payload": payload if isinstance(payload, dict) else {},
        },
    )

    deadline = time.time() + max(0.1, float(timeout_seconds or 0.1))
    current_offset = result_offset
    while time.time() < deadline:
        for raw_line, line_end_offset in read_new_runtime_jsonl_lines(BROWSER_RESULT_QUEUE_JSONL, current_offset, bom_at_start=True):
            current_offset = line_end_offset
            try:
                result = json.loads(raw_line.lstrip("\ufeff").strip())
            except Exception:
                continue
            if isinstance(result, dict) and str(result.get("request_id") or "").strip() == request_id:
                return result
        time.sleep(0.10)

    return {
        "request_id": request_id,
        "action": str(action or "").strip(),
        "ok": False,
        "executed_via": "browser_service_client",
        "error": "browser_service_timeout",
    }
