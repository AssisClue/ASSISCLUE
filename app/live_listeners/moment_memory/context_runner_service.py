from __future__ import annotations

import json
import time
from typing import Any

from .live_moment_reader import LiveMomentReader




from app.live_listeners.shared.listener_paths import (
    CONTEXT_RUNNER_CURSOR_JSON,
    LIVE_MOMENT_HISTORY_JSONL,
)

from .context_runner_config import CONTEXT_RUNNER_POLL_SECONDS
from .context_window_builder import ContextWindowBuilder
from .memory_snapshot_writer import (
    write_context_runner_status,
    write_context_snapshot,
    write_memory_snapshot,
    write_world_state,
)
from .summary_builder import build_summary
from .world_state_builder import build_world_state


class ContextRunnerService:
    def __init__(self) -> None:
        self.reader = LiveMomentReader(
            transcript_path=LIVE_MOMENT_HISTORY_JSONL,
            cursor_path=CONTEXT_RUNNER_CURSOR_JSON,
        )


        self.window_builder = ContextWindowBuilder()
        self._window: list[dict[str, Any]] = []
        self._running = False

    def process_moment(self, moment: dict[str, Any]) -> None:
        self._window = self.window_builder.build_window(self._window, moment)

        paragraphs = [
            str(item.get("paragraph", "")).strip()
            for item in self._window
            if str(item.get("paragraph", "")).strip()
        ]

        summary = build_summary(paragraphs)
        world_state = build_world_state(self._window)

        context_snapshot = {
            "updated_at": time.time(),
            "moment_count": len(self._window),
            "latest_summary": summary,
            "latest_source_session_id": moment.get("source_session_id", ""),
        }

        memory_snapshot = {
            "updated_at": time.time(),
            "latest_summary": summary,
            "recent_paragraphs": paragraphs[-5:],
        }

        write_context_snapshot(context_snapshot)
        write_memory_snapshot(memory_snapshot)
        write_world_state(world_state)

    def run_forever(self) -> None:
        self._running = True

        write_context_runner_status("starting")

        try:
            write_context_runner_status("running")

            while self._running:
                moments = self.reader.read_new_records()

                for moment in moments:
                    self.process_moment(moment)

                    write_context_runner_status(
                        "running",
                        last_event="context_snapshot_updated",
                        last_live_moment_id=moment.get("event_id", ""),
                        last_intent_type=moment.get("intent_type", ""),
                    )

                    print(json.dumps(moment, ensure_ascii=False), flush=True)

                time.sleep(CONTEXT_RUNNER_POLL_SECONDS)

        except KeyboardInterrupt:
            write_context_runner_status("stopped", reason="keyboard_interrupt")

        except Exception as exc:
            write_context_runner_status(
                "error",
                error=f"{type(exc).__name__}: {exc}",
            )
            raise

        finally:
            write_context_runner_status("stopped")

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    ContextRunnerService().run_forever()