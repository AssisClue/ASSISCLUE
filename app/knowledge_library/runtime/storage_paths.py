from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .paths import data_root, runtime_root


@dataclass(slots=True)
class KnowledgeLibraryStoragePaths:
    def data_root(self) -> Path:
        return data_root()

    def runtime_root(self) -> Path:
        return runtime_root()

    def manifests_dir(self) -> Path:
        return self.data_root() / "manifests"

    def maps_dir(self) -> Path:
        return self.runtime_root() / "maps"

    def logs_dir(self) -> Path:
        return self.runtime_root() / "logs"

    def library_roots_path(self) -> Path:
        return self.manifests_dir() / "library_roots.json"

    def library_map_path(self) -> Path:
        return self.maps_dir() / "library_map.json"

    def file_hash_index_path(self) -> Path:
        return self.maps_dir() / "file_hash_index.json"

    def scan_status_path(self) -> Path:
        return self.maps_dir() / "folder_scan_status.json"

    def ensure_directories(self) -> None:
        self.manifests_dir().mkdir(parents=True, exist_ok=True)
        self.maps_dir().mkdir(parents=True, exist_ok=True)
        self.logs_dir().mkdir(parents=True, exist_ok=True)