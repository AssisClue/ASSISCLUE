from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def data_root() -> Path:
    return project_root() / "data" / "knowledge_library"


def runtime_root() -> Path:
    return project_root() / "runtime" / "knowledge_library"