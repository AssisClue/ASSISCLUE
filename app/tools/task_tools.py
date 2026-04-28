from __future__ import annotations

from app.schemas.task_packet import TaskPacket


def mark_task_done(task: TaskPacket) -> TaskPacket:
    task.status = "done"
    return task


def mark_task_failed(task: TaskPacket) -> TaskPacket:
    task.status = "failed"
    return task


def mark_task_running(task: TaskPacket) -> TaskPacket:
    task.status = "running"
    return task