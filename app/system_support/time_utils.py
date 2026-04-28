from __future__ import annotations

from datetime import datetime


def format_ts(ts: float | int | None) -> str:
    if ts is None:
        return ""

    try:
        value = float(ts)
    except Exception:
        return ""

    dt = datetime.fromtimestamp(value)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_ts_short(ts: float | int | None) -> str:
    if ts is None:
        return ""

    try:
        value = float(ts)
    except Exception:
        return ""

    dt = datetime.fromtimestamp(value)
    return dt.strftime("%H:%M:%S")


def add_pretty_ts(payload: dict | None) -> dict | None:
    if not payload:
        return payload

    enriched = dict(payload)
    enriched["ts_pretty"] = format_ts(payload.get("ts"))
    enriched["ts_short"] = format_ts_short(payload.get("ts"))
    return enriched