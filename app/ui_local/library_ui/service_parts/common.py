from __future__ import annotations

import json
import re
from pathlib import Path

from app.knowledge_library.services.knowledge_library_facade import KnowledgeLibraryFacade

from ..runtime.ui_paths import project_root
from ..system_areas import build_system_areas


COMMON_LIBRARY_EXTENSIONS = [
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".json",
    ".jsonl",
    ".csv",
    ".log",
    ".html",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
]

COMMON_SYSTEM_EXTENSIONS = [
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".json",
    ".jsonl",
    ".csv",
    ".log",
    ".html",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".wav",
    ".mp3",
    ".mp4",
]


class BaseUiService:
    def __init__(self) -> None:
        self.facade = KnowledgeLibraryFacade()

    def project_root(self) -> Path:
        return project_root()

    def runtime_root(self) -> Path:
        return self.project_root() / "runtime" / "knowledge_library"

    def format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        if size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def normalize_query(self, value: str | None) -> str:
        return str(value or "").strip().lower()

    def normalize_extension(self, value: str | None) -> str:
        raw = str(value or "").strip().lower()
        if not raw or raw == "all":
            return ""
        return raw if raw.startswith(".") else f".{raw}"

    def safe_resolve(self, value: str) -> Path:
        return Path(value).resolve()

    def is_within_any_root(self, target: Path, roots: list[Path]) -> bool:
        for root in roots:
            if target == root or root in target.parents:
                return True
        return False

    def list_folder_entries(self, folder_path: Path, limit: int = 200) -> list[dict]:
        if not folder_path.exists() or not folder_path.is_dir():
            return []

        children = sorted(folder_path.iterdir(), key=lambda p: (not p.is_dir(), str(p.name).lower()))
        entries: list[dict] = []

        for child in children[:limit]:
            try:
                size = int(child.stat().st_size) if child.is_file() else 0
            except Exception:
                size = 0

            entries.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "entry_type": "dir" if child.is_dir() else "file",
                    "extension": child.suffix.lower() if child.is_file() else "",
                    "size_bytes": size,
                    "size_label": "--" if child.is_dir() else self.format_size(size),
                }
            )
        return entries

    def read_text_file_preview(self, path: Path, max_chars: int = 12000) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
        except Exception:
            try:
                return path.read_text(encoding="latin-1", errors="replace")[:max_chars]
            except Exception:
                return ""

    def read_latest_summary_for_item(self, item_id: str) -> dict:
        candidates = [
            self.runtime_root() / "summaries" / "book_summaries.jsonl",
            self.runtime_root() / "summaries" / "file_summaries.jsonl",
        ]

        latest: dict = {}
        for path in candidates:
            if not path.exists() or not path.is_file():
                continue
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except Exception:
                    continue
                if str(payload.get("item_id", "")).strip() == str(item_id).strip():
                    latest = payload
        return latest if isinstance(latest, dict) else {}

    def read_index_status_for_item(self, item_id: str) -> dict:
        path = self.runtime_root() / "indexing" / "indexed_files.json"
        if not path.exists() or not path.is_file():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}
        if str(payload.get("item_id", "")).strip() != str(item_id).strip():
            return {}
        return payload

    def collect_library_extensions(self, items: list[dict]) -> list[str]:
        found = {
            str(item.get("extension", "")).strip().lower()
            for item in items
            if str(item.get("extension", "")).strip()
        }
        merged = sorted(set(COMMON_LIBRARY_EXTENSIONS) | found)
        return merged

    def collect_system_extensions(self, entries: list[dict]) -> list[str]:
        found = {
            str(entry.get("extension", "")).strip().lower()
            for entry in entries
            if str(entry.get("extension", "")).strip()
        }
        merged = sorted(set(COMMON_SYSTEM_EXTENSIONS) | found)
        return merged

    def system_areas(self) -> list[dict]:
        return build_system_areas(self.project_root())

    def build_breadcrumbs(self, current_path: Path, allowed_roots: list[Path]) -> list[dict]:
        matching_roots = [root for root in allowed_roots if current_path == root or root in current_path.parents]
        if not matching_roots:
            return []

        root = max(matching_roots, key=lambda p: len(str(p)))
        crumbs = [{"label": root.name, "path": str(root)}]

        if current_path == root:
            return crumbs

        rel_parts = current_path.relative_to(root).parts
        walk = root
        for part in rel_parts:
            walk = walk / part
            crumbs.append({"label": part, "path": str(walk)})
        return crumbs

    def _wildcard_to_regex(self, pattern: str) -> re.Pattern[str] | None:
        clean = self.normalize_query(pattern)
        if not clean:
            return None
        escaped = re.escape(clean).replace(r"\*", ".*")
        return re.compile(escaped, re.IGNORECASE)

    def _query_looks_like_extension(self, query: str) -> bool:
        clean = self.normalize_query(query)
        if not clean:
            return False
        clean = clean.replace("*", "")
        if not clean:
            return False
        if clean.startswith("."):
            clean = clean[1:]
        return clean.isalnum() and len(clean) <= 5

    def _extension_matches_query(self, actual_extension: str, query: str) -> bool:
        actual = str(actual_extension or "").strip().lower()
        clean = self.normalize_query(query)
        if not actual or not clean:
            return False

        clean_no_star = clean.replace("*", "")
        if not clean_no_star:
            return False

        normalized = clean_no_star if clean_no_star.startswith(".") else f".{clean_no_star}"
        if actual == normalized:
            return True

        if "*" in clean:
            regex = self._wildcard_to_regex(normalized)
            if regex and regex.search(actual):
                return True

        return False

    def flexible_match(
        self,
        *,
        query: str,
        name: str = "",
        path: str = "",
        extension: str = "",
        extra_terms: list[str] | None = None,
    ) -> bool:
        clean = self.normalize_query(query)
        if not clean:
            return True

        hay_parts = [
            str(name or ""),
            str(path or ""),
            str(extension or ""),
        ]
        hay_parts.extend([str(term or "") for term in (extra_terms or [])])
        haystack = " ".join(hay_parts).lower()

        if clean in haystack:
            return True

        if self._query_looks_like_extension(clean) and self._extension_matches_query(extension, clean):
            return True

        if "*" in clean:
            regex = self._wildcard_to_regex(clean)
            if regex and regex.search(haystack):
                return True

            if self._query_looks_like_extension(clean) and self._extension_matches_query(extension, clean):
                return True

        tokens = [token for token in re.split(r"[\s_\-\.]+", clean.replace("*", " ")) if token]
        if tokens and all(token in haystack for token in tokens):
            return True

        return False