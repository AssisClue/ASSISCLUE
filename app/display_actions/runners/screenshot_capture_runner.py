from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from uuid import uuid4


def _capture_screenshot_png(path: Path, *, full: bool) -> None:
    import mss
    import mss.tools
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)

    with mss.mss() as sct:
        monitor = sct.monitors[0] if full else sct.monitors[1]
        shot = sct.grab(monitor)

        image = Image.frombytes("RGB", shot.size, shot.rgb)

        target_size = 1280
        border = min(64, max(0, min(image.width, image.height) // 8))
        if border * 2 < image.width and border * 2 < image.height:
            image = image.crop((border, border, image.width - border, image.height - border))

        side = min(image.width, image.height)
        left = (image.width - side) // 2
        top = (image.height - side) // 2
        image = image.crop((left, top, left + side, top + side)).resize(
            (target_size, target_size),
            resample=Image.Resampling.LANCZOS,
        )

        image.save(str(path), format="PNG", optimize=True)


def run_screenshot_capture_action(request: dict[str, Any]) -> dict[str, Any]:
    from app.display_actions.helpers.screenshot_paths import get_new_screenshot_path

    command = request.get("command", {}) if isinstance(request.get("command", {}), dict) else {}
    action_name = str(command.get("action_name", "")).strip()

    is_full = action_name == "take_full_screenshot"
    screenshot_path = get_new_screenshot_path(prefix="full_screenshot" if is_full else "screenshot")

    try:
        _capture_screenshot_png(screenshot_path, full=is_full)
        created = True
        error = ""
    except Exception as exc:
        created = False
        error = f"{type(exc).__name__}: {exc}"

    return {
        "result_id": f"dres_{uuid4().hex}",
        "ts": time.time(),
        "ok": created,
        "action_name": action_name,
        "source_event_id": str(request.get("source_event_id", "")).strip(),
        "routed_event_id": str(request.get("routed_event_id", "")).strip(),
        "screenshot_path": str(screenshot_path),
        "screenshot_created": created,
        "used_existing_screenshot": False,
        "analysis_text": "",
        "speech_text": (
            ("Full screenshot captured." if is_full else "Screenshot captured.")
            if created
            else "Screenshot failed."
        ),
        "flags": request.get("flags", {}) if isinstance(request.get("flags", {}), dict) else {},
        "meta": {
            "capture_mode": "full" if is_full else "standard",
            "capture_backend": "mss+pillow",
            "error": error,
        },
    }
