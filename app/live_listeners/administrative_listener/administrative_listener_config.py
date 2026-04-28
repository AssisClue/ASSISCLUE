from __future__ import annotations

import os


ADMINISTRATIVE_LISTENER_NAME = "administrative_listener"

ADMINISTRATIVE_LISTENER_POLL_SECONDS = float(
    os.getenv("ADMINISTRATIVE_LISTENER_POLL_SECONDS", "0.60")
)

MOMENT_WINDOW_MAX_RECORDS = int(
    os.getenv("MOMENT_WINDOW_MAX_RECORDS", "6")
)

MOMENT_WINDOW_MAX_SECONDS = float(
    os.getenv("MOMENT_WINDOW_MAX_SECONDS", "20")
)

MIN_PARAGRAPH_CHARS = int(
    os.getenv("MIN_PARAGRAPH_CHARS", "12")
)

MIN_PARAGRAPH_WORDS = int(
    os.getenv("MIN_PARAGRAPH_WORDS", "3")
)

QUESTION_HINTS = {
    "?",
    "what",
    "when",
    "where",
    "who",
    "why",
    "how",
    "which",
    "can",
    "could",
    "did",
    "do",
    "does",
    "is",
    "are",
    "was",
    "were",
}

ADMINISTRATIVE_EXECUTE_COMMANDS = os.getenv(
    "ADMINISTRATIVE_EXECUTE_COMMANDS",
    "1",
).strip() not in {"0", "false", "False", "no", "NO"}

ADMINISTRATIVE_EXECUTE_BROWSER_COMMANDS = os.getenv(
    "ADMINISTRATIVE_EXECUTE_BROWSER_COMMANDS",
    "1",
).strip() not in {"0", "false", "False", "no", "NO"}