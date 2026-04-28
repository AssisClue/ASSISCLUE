from __future__ import annotations

from collections.abc import Callable

from app.tools.file_reader import read_text_file, safe_read_text_file
from app.tools.note_writer import append_note, overwrite_note
from app.tools.summary_tools import summarize_lines, summarize_text_blocks
from app.tools.web_search import web_search_placeholder


def build_tool_registry() -> dict[str, Callable]:
    return {
        "web_search": web_search_placeholder,
        "read_text_file": read_text_file,
        "safe_read_text_file": safe_read_text_file,
        "append_note": append_note,
        "overwrite_note": overwrite_note,
        "summarize_lines": summarize_lines,
        "summarize_text_blocks": summarize_text_blocks,
    }