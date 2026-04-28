from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot


@dataclass(slots=True)
class RecentContextSummary:
    def build_lines(self, snapshot: RecentContextSnapshot, max_items: int = 10) -> list[str]:
        lines: list[str] = []

        lines.extend(snapshot.summary_lines[:5])

        for topic in snapshot.recent_topics[:3]:
            lines.append(f"Recent topic: {topic}")

        for project in snapshot.recent_projects[:3]:
            lines.append(f"Recent project: {project}")

        for error in snapshot.recent_errors[:3]:
            lines.append(f"Recent error: {error}")

        return lines[:max_items]