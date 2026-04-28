from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import Locator, Page

from app.web_tools.runtime.web_runtime_paths import ensure_web_runtime_dirs, screenshots_root


def _timestamp_for_filename() -> str:
    return datetime.now().strftime("%Y-%m-%d__%H-%M-%S")


def _clean_name_prefix(name_prefix: str, *, fallback: str) -> str:
    clean = str(name_prefix or "").strip().replace(" ", "_")
    return clean or fallback


def capture_page_screenshot(
    page: Page,
    *,
    name_prefix: str = "page",
    full_page: bool = False,
) -> dict[str, Any]:
    ensure_web_runtime_dirs()

    clean_prefix = _clean_name_prefix(name_prefix, fallback="page")
    filename = f"{clean_prefix}_{_timestamp_for_filename()}.png"
    path = screenshots_root() / filename

    viewport = page.viewport_size or {}
    page.screenshot(path=str(path), full_page=full_page)

    return {
        "ok": True,
        "path": str(path),
        "filename": filename,
        "full_page": full_page,
        "url": page.url,
        "title": page.title(),
        "viewport_width": int(viewport.get("width", 0) or 0),
        "viewport_height": int(viewport.get("height", 0) or 0),
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
    }


def capture_locator_screenshot(
    locator: Locator,
    *,
    name_prefix: str = "element",
) -> dict[str, Any]:
    ensure_web_runtime_dirs()

    clean_prefix = _clean_name_prefix(name_prefix, fallback="element")
    filename = f"{clean_prefix}_{_timestamp_for_filename()}.png"
    path = screenshots_root() / filename

    locator.screenshot(path=str(path))

    return {
        "ok": True,
        "path": str(path),
        "filename": filename,
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
    }


def screenshot_path_exists(path: str | Path) -> bool:
    return Path(path).exists()