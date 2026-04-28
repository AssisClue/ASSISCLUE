from __future__ import annotations


def build_memory_status_panel(mem0_runtime: dict | None, session_snapshot: dict | None) -> dict[str, object]:
    mem0_runtime = mem0_runtime or {}
    session_snapshot = session_snapshot or {}

    return {
        "title": "Memory Backend",
        "status": "active" if mem0_runtime.get("active_backend") else "idle",
        "description": "Active memory backend, readiness, and session snapshot.",
        "items": [
            {
                "label": "configured_backend",
                "value": mem0_runtime.get("configured_backend") or "n/a",
            },
            {
                "label": "active_backend",
                "value": mem0_runtime.get("active_backend") or "n/a",
            },
            {
                "label": "mem0_ready",
                "value": mem0_runtime.get("mem0_ready"),
            },
            {
                "label": "process_running",
                "value": mem0_runtime.get("process_running"),
            },
            {
                "label": "memory_count",
                "value": session_snapshot.get("memory_count", 0),
            },
        ],
    }