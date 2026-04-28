from __future__ import annotations

from dataclasses import dataclass

from app.context_memory.models.live_context_snapshot import LiveContextSnapshot
from app.context_memory.models.recent_context_snapshot import RecentContextSnapshot
from app.context_memory.models.task_context_packet import TaskContextPacket
from app.context_memory.models.user_profile_snapshot import UserProfileSnapshot


@dataclass(slots=True)
class ContextPacketBuilder:
    def build_packet(
        self,
        live_snapshot: LiveContextSnapshot,
        recent_snapshot: RecentContextSnapshot,
        profile_snapshot: UserProfileSnapshot,
        task_packet: TaskContextPacket,
    ) -> dict:
        return {
            "live_context": {
                "current_focus": live_snapshot.current_focus,
                "active_topics": live_snapshot.active_topics,
                "recent_events": live_snapshot.recent_events,
                "screenshot_notes": live_snapshot.screenshot_notes,
                "open_issues": live_snapshot.open_issues,
                "metadata": {
                    "ts": live_snapshot.metadata.ts,
                    "tags": live_snapshot.metadata.tags,
                },
            },
            "recent_context": {
                "summary_lines": recent_snapshot.summary_lines,
                "recent_topics": recent_snapshot.recent_topics,
                "recent_projects": recent_snapshot.recent_projects,
                "notable_events": recent_snapshot.notable_events,
                "recent_errors": recent_snapshot.recent_errors,
                "metadata": {
                    "ts": recent_snapshot.metadata.ts,
                    "tags": recent_snapshot.metadata.tags,
                },
            },
            "user_profile": {
                "stable_facts": profile_snapshot.stable_facts,
                "preferences": profile_snapshot.preferences,
                "active_projects": profile_snapshot.active_projects,
                "working_style": profile_snapshot.working_style,
                "metadata": {
                    "ts": profile_snapshot.metadata.ts,
                    "tags": profile_snapshot.metadata.tags,
                },
            },
            "task_context": {
                "task_type": task_packet.task_type.value,
                "query": task_packet.query,
                "summary_lines": task_packet.summary_lines,
                "memory_items": [
                    {
                        "item_id": item.item_id,
                        "text": item.text,
                        "kind": item.kind,
                        "source": item.source,
                        "importance": item.importance,
                        "ts": item.ts,
                        "tags": item.tags,
                        "related_ids": item.related_ids,
                        "project_name": item.project_name,
                        "metadata": item.metadata,
                    }
                    for item in task_packet.memory_items
                ],
                "recent_items": task_packet.recent_items,
                "profile_items": task_packet.profile_items,
                "screenshot_notes": task_packet.screenshot_notes,
                "project_name": task_packet.project_name,
                "metadata": task_packet.metadata,
            },
        }