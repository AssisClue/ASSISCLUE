from __future__ import annotations

import os
from pathlib import Path


PRIMARY_LISTENER_NAME = "primary_listener"

# Wakeword
DEFAULT_WAKEWORDS = [
    "assistant",
    "rick",
    "assis",
    "ai",
    "hey",
    "hello assistant",
    "hey assistant",
    "hey rick",
    "ok assistant",
    "say assistant",
    "say rick",
]

# Quick question
QUICK_QUESTION_MAX_WORDS = int(os.getenv("PRIMARY_QUICK_QUESTION_MAX_WORDS", "12"))
SPOKEN_QUESTION_MAX_WORDS = int(os.getenv("PRIMARY_SPOKEN_QUESTION_MAX_WORDS", "40"))

# Loop
PRIMARY_LISTENER_POLL_SECONDS = float(os.getenv("PRIMARY_LISTENER_POLL_SECONDS", "0.35"))

# Paths
PRIMARY_LISTENER_DIR = Path(__file__).resolve().parent
COMMAND_CATALOG_PATH = PRIMARY_LISTENER_DIR / "command_catalog.json"

# Event types
EVENT_TYPE_COMMAND = "primary_command"
EVENT_TYPE_QUICK_QUESTION = "primary_quick_question"
EVENT_TYPE_WAKEWORD_ONLY = "primary_wakeword_only"

EDIT_MODE_ALIASES = [
    "edit mode",
]


#ECHO KILL BLOCK PLAYBACKimport os

PLAYBACK_ECHO_COOLDOWN_SECONDS = float(
    os.getenv("PLAYBACK_ECHO_COOLDOWN_SECONDS", "2.0")
)

PLAYBACK_EXACT_TEXT_BLOCK_SECONDS = float(
    os.getenv("PLAYBACK_EXACT_TEXT_BLOCK_SECONDS", "10.0")
)
