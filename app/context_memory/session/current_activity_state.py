from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CurrentActivityState:
    active_task: str = ""
    active_project: str = ""
    current_focus: str = ""
    active_topics: list[str] = field(default_factory=list)
    open_issues: list[str] = field(default_factory=list)
    last_user_text: str = ""
    last_assistant_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def set_task(self, task: str) -> None:
        self.active_task = task.strip()

    def set_project(self, project: str) -> None:
        self.active_project = project.strip()

    def set_focus(self, focus: str) -> None:
        self.current_focus = focus.strip()

    def set_last_user_text(self, text: str) -> None:
        self.last_user_text = text.strip()

    def set_last_assistant_text(self, text: str) -> None:
        self.last_assistant_text = text.strip()

    def set_topics(self, topics: list[str]) -> None:
        self.active_topics = [topic.strip() for topic in topics if topic.strip()]

    def add_topic(self, topic: str) -> None:
        cleaned = topic.strip()
        if cleaned and cleaned not in self.active_topics:
            self.active_topics.append(cleaned)

    def set_open_issues(self, issues: list[str]) -> None:
        self.open_issues = [issue.strip() for issue in issues if issue.strip()]

    def add_open_issue(self, issue: str) -> None:
        cleaned = issue.strip()
        if cleaned and cleaned not in self.open_issues:
            self.open_issues.append(cleaned)

    def clear(self) -> None:
        self.active_task = ""
        self.active_project = ""
        self.current_focus = ""
        self.active_topics.clear()
        self.open_issues.clear()
        self.last_user_text = ""
        self.last_assistant_text = ""
        self.metadata.clear()