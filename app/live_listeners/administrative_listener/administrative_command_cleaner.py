from __future__ import annotations


def normalize_administrative_command_text(text: str) -> str:
    """
    Keep this intentionally simple for administrative listener.

    We do not try to do smart NLP here.
    We only normalize spacing/casing so alias matching can be stable.
    """
    return " ".join(str(text or "").strip().lower().split())