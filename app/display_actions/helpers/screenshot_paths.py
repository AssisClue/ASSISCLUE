from __future__ import annotations

import time
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = APP_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"

DISPLAY_ACTIONS_DIR = RUNTIME_DIR / "display_actions"
RESULTS_DIR = DISPLAY_ACTIONS_DIR / "results"
STATUS_DIR = DISPLAY_ACTIONS_DIR / "status"
SCREENSHOTS_DIR = DISPLAY_ACTIONS_DIR / "screenshots"

DISPLAY_ACTION_RESULTS_JSONL = RESULTS_DIR / "display_action_results.jsonl"
DISPLAY_ACTION_STATUS_JSON = STATUS_DIR / "display_action_runner_status.json"

SCREENSHOT_RECENT_SECONDS = 120


def ensure_display_action_runtime_dirs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not DISPLAY_ACTION_RESULTS_JSONL.exists():
        DISPLAY_ACTION_RESULTS_JSONL.write_text("", encoding="utf-8")


def get_new_screenshot_path(*, prefix: str = "screenshot") -> Path:
    ensure_display_action_runtime_dirs()
    return SCREENSHOTS_DIR / f"{prefix}_{int(time.time() * 1000)}.png"


def get_latest_screenshot_path() -> Path | None:
    ensure_display_action_runtime_dirs()
    candidates = sorted(SCREENSHOTS_DIR.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    return candidates[0]


def is_recent_screenshot(path: Path | None, *, max_age_seconds: int = SCREENSHOT_RECENT_SECONDS) -> bool:
    if path is None or not path.exists():
        return False

    try:
        age_seconds = time.time() - path.stat().st_mtime
    except Exception:
        return False

    return age_seconds <= max_age_seconds