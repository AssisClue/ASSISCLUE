from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


def _project_root(project_root: str | Path) -> Path:
    return Path(project_root).resolve()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _ensure_screenshot_dir(root: Path) -> Path:
    screenshot_dir = root / "data" / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    return screenshot_dir


def _write_placeholder_png(path: Path, label: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (400, 300), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    text = f"Placeholder for {label}"

    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = draw.textsize(text, font=font)

    x = (img.width - text_width) / 2
    y = (img.height - text_height) / 2

    draw.text((x, y), text, fill=(255, 255, 0), font=font)
    img.save(path, format="PNG")


def run_screenshot_capture_once(
    project_root: str | Path,
    *,
    trigger: str = "ui_manual",
    boot: Any | None = None,
) -> dict[str, Any]:
    root = _project_root(project_root)
    screenshot_dir = _ensure_screenshot_dir(root)

    ts = time.time()
    filename = f"screenshot_{int(ts * 1000)}.png"
    output_path = screenshot_dir / filename

    _write_placeholder_png(output_path, label=trigger)

    payload = {
        "ts": ts,
        "ok": True,
        "trigger": trigger,
        "filename": filename,
        "output_path": str(output_path),
        "source_type": "screenshot",
    }

    _write_json(root / "runtime" / "state" / "screenshot_capture_loop.json", payload)
    return payload


def should_run_screenshot_interval(
    project_root: str | Path,
    *,
    boot: Any | None = None,
) -> bool:
    return False