from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def ui_root() -> Path:
    return Path(__file__).resolve().parents[1]


def templates_dir() -> Path:
    return ui_root() / "templates"


def static_dir() -> Path:
    return ui_root() / "static"