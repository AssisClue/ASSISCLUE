from __future__ import annotations

import os


CONTEXT_RUNNER_NAME = "context_runner"

CONTEXT_RUNNER_POLL_SECONDS = float(
    os.getenv("CONTEXT_RUNNER_POLL_SECONDS", "1.20")
)

CONTEXT_WINDOW_MAX_MOMENTS = int(
    os.getenv("CONTEXT_WINDOW_MAX_MOMENTS", "8")
)

SUMMARY_MAX_CHARS = int(
    os.getenv("SUMMARY_MAX_CHARS", "280")
)