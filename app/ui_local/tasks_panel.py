from __future__ import annotations


def build_tasks_panel(important_tasks: list[dict] | None = None) -> dict[str, object]:
    tasks = important_tasks or []

    return {
        "title": "Important Queue",
        "status": "active" if tasks else "idle",
        "description": "Pending work, latest decision, latest plan, and execution state.",
        "items": tasks,
    }