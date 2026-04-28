from __future__ import annotations

from pathlib import Path

from app.system_support.runtime_files import read_runtime_json


def _resolve_latest_screenshot_path(project_root: Path) -> Path | None:
    runtime_input = read_runtime_json(project_root / "runtime" / "input" / "latest_screenshot.json") or {}
    loop_state = read_runtime_json(project_root / "runtime" / "state" / "screenshot_capture_loop.json") or {}

    for raw_path in (
        runtime_input.get("output_path"),
        loop_state.get("last_output_path"),
        ((loop_state.get("extra") or {}).get("output_path")),
    ):
        text = str(raw_path or "").strip()
        if not text:
            continue
        path = Path(text)
        if path.exists():
            return path
    return None


def build_screenshots_panel(project_root: str | Path) -> dict[str, str]:
    root = Path(project_root).resolve()
    latest_path = _resolve_latest_screenshot_path(root)
    latest_name = latest_path.name if latest_path else ""
    latest_ts = latest_path.stat().st_mtime if latest_path and latest_path.exists() else 0

    return {
        "title": "Latest Screenshot",
        "status": "ready" if latest_path else "idle",
        "description": "Manual, interval, and hotkey screenshot capture.",
        "image_name": latest_name,
        "image_path": str(latest_path) if latest_path else "",
        "image_url": f"/screenshots/{latest_name}?v={int(latest_ts)}" if latest_name else "",
    }
