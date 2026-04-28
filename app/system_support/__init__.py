"""
Small helpers used across the app (read/write runtime files, time formatting, etc).

Keep this module "light":
- re-export only simple utilities
- avoid importing heavy modules at import time
"""

from app.system_support.runtime_files import build_runtime_message_payload, read_runtime_json, write_runtime_json
from app.system_support.runtime_jsonl import append_runtime_jsonl, build_chat_history_item, read_runtime_jsonl
from app.system_support.system_runtime_state import (
    read_play_loop_state,
    read_system_runtime_state,
    system_runtime_state_path,
    write_play_loop_state,
    write_play_loop_state_if_changed,
    write_system_runtime_state,
)
from app.system_support.text_cleaning import normalize_pipeline_text, repair_common_mojibake
from app.system_support.time_utils import add_pretty_ts, format_ts, format_ts_short

__all__ = [
    "add_pretty_ts",
    "append_runtime_jsonl",
    "build_chat_history_item",
    "build_runtime_message_payload",
    "format_ts",
    "format_ts_short",
    "normalize_pipeline_text",
    "read_play_loop_state",
    "read_runtime_json",
    "read_runtime_jsonl",
    "read_system_runtime_state",
    "repair_common_mojibake",
    "system_runtime_state_path",
    "write_play_loop_state",
    "write_play_loop_state_if_changed",
    "write_runtime_json",
    "write_system_runtime_state",
]
