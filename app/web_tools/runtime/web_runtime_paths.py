from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def runtime_root() -> Path:
    return project_root() / "runtime"


def web_runtime_root() -> Path:
    return runtime_root() / "web"


def screenshots_root() -> Path:
    return web_runtime_root() / "screenshots"


def pages_root() -> Path:
    return web_runtime_root() / "pages"


def ensure_web_runtime_dirs() -> None:
    screenshots_root().mkdir(parents=True, exist_ok=True)
    pages_root().mkdir(parents=True, exist_ok=True)