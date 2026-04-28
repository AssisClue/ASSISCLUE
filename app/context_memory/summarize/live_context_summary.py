from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.live_context_snapshot import LiveContextSnapshot


@dataclass(slots=True)
class LiveContextSummary:
    def build_lines(self, snapshot: LiveContextSnapshot, max_items: int = 8) -> list[str]:
        lines: list[str] = []

        if snapshot.current_focus:
            lines.append(f"Current focus: {snapshot.current_focus}")

        for topic in snapshot.active_topics[:3]:
            lines.append(f"Active topic: {topic}")

        for issue in snapshot.open_issues[:3]:
            lines.append(f"Open issue: {issue}")

        for note in snapshot.screenshot_notes[:2]:
            lines.append(f"Screenshot note: {note}")

        for event in snapshot.recent_events[:3]:
            lines.append(f"Recent event: {event}")

        return lines[:max_items]