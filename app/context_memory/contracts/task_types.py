from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskType(str, Enum):
    GENERAL = "general"
    SCREENSHOT_ANALYSIS = "screenshot_analysis"
    SCREENSHOT_CODE = "screenshot_code"
    CODING_HELP = "coding_help"
    TIMELINE_LOOKUP = "timeline_lookup"
    MEETING_LOOKUP = "meeting_lookup"
    PROJECT_FOLLOWUP = "project_followup"
    USER_PREFERENCE = "user_preference"
    MEMORY_SEARCH = "memory_search"


@dataclass(slots=True)
class TaskContextHint:
    project_name: str | None = None
    preferred_sources: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)