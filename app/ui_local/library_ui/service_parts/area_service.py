from __future__ import annotations

from pathlib import Path

from .common import BaseUiService


class AreaViewService(BaseUiService):
    def get_area_payload(self, area_key: str) -> dict:
        areas = self.system_areas()
        target = next((area for area in areas if str(area.get("key", "")).strip() == str(area_key).strip()), None)
        if target is None:
            raise ValueError(f"Unknown area_key: {area_key}")

        roots = []
        for folder in target.get("folders", []):
            roots.append(
                {
                    "name": folder["name"],
                    "path": folder["path"],
                    "exists": folder["exists"],
                }
            )

        return {
            "area": target,
            "roots": roots,
        }

    def _filter_entries(
        self,
        entries: list[dict],
        *,
        search: str = "",
        extension: str = "",
        entry_type: str = "",
    ) -> list[dict]:
        search_q = self.normalize_query(search)
        ext_q = self.normalize_extension(extension)
        type_q = str(entry_type or "").strip().lower()

        filtered: list[dict] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue

            current_type = str(entry.get("entry_type", "")).strip().lower()
            if type_q and type_q != "all" and current_type != type_q:
                continue

            current_ext = str(entry.get("extension", "")).strip().lower()
            if ext_q and current_ext != ext_q:
                continue

            if search_q:
                if not self.flexible_match(
                    query=search_q,
                    name=str(entry.get("name", "") or ""),
                    path=str(entry.get("path", "") or ""),
                    extension=current_ext,
                    extra_terms=[current_type],
                ):
                    continue

            filtered.append(entry)

        return filtered

    def _recursive_area_search(self, roots: list[Path], limit: int | None = None) -> list[dict]:
        results: list[dict] = []

        for root in roots:
            if not root.exists() or not root.is_dir():
                continue

            try:
                for path in root.rglob("*"):
                    if limit is not None and len(results) >= limit:
                        return results

                    entry_type = "dir" if path.is_dir() else "file"
                    extension = path.suffix.lower() if path.is_file() else ""

                    try:
                        size = int(path.stat().st_size) if path.is_file() else 0
                    except Exception:
                        size = 0

                    results.append(
                        {
                            "name": path.name,
                            "path": str(path),
                            "entry_type": entry_type,
                            "extension": extension,
                            "size_bytes": size,
                            "size_label": "--" if entry_type == "dir" else self.format_size(size),
                        }
                    )
            except Exception:
                continue

        return results

    def get_area_browser_payload(
        self,
        area_key: str,
        *,
        current_path: str = "",
        search: str = "",
        extension: str = "",
        entry_type: str = "",
    ) -> dict:
        areas = self.system_areas()
        target = next((area for area in areas if str(area.get("key", "")).strip() == str(area_key).strip()), None)
        if target is None:
            raise ValueError(f"Unknown area_key: {area_key}")

        allowed_roots = [
            self.safe_resolve(str(folder.get("path", "")).strip())
            for folder in target.get("folders", [])
            if str(folder.get("path", "")).strip()
        ]

        search_q = self.normalize_query(search)
        current_path_q = str(current_path or "").strip()

        # SEARCH GLOBAL DEL ÁREA
        if search_q or not current_path_q:
            all_entries = self._recursive_area_search(allowed_roots)
            entries = self._filter_entries(
                all_entries,
                search=search,
                extension=extension,
                entry_type=entry_type,
            )

            return {
                "area": target,
                "entries": entries,
                "all_entry_count": len(all_entries),
                "filters": {
                    "search": str(search or "").strip(),
                    "extension": self.normalize_extension(extension),
                    "entry_type": str(entry_type or "").strip().lower(),
                },
                "extension_options": self.collect_system_extensions(all_entries),
                "current_folder_path": "",
                "breadcrumbs": [],
                "search_scope": "area",
            }

        base_path = self.safe_resolve(current_path_q)
        if not base_path.exists() or not base_path.is_dir():
            raise ValueError("Current folder does not exist.")
        if not self.is_within_any_root(base_path, allowed_roots):
            raise ValueError("Current folder is outside allowed area folders.")

        all_entries = self.list_folder_entries(base_path)
        entries = self._filter_entries(
            all_entries,
            search=search,
            extension=extension,
            entry_type=entry_type,
        )

        return {
            "area": target,
            "entries": entries,
            "all_entry_count": len(all_entries),
            "filters": {
                "search": str(search or "").strip(),
                "extension": self.normalize_extension(extension),
                "entry_type": str(entry_type or "").strip().lower(),
            },
            "extension_options": self.collect_system_extensions(all_entries),
            "current_folder_path": str(base_path),
            "breadcrumbs": self.build_breadcrumbs(base_path, allowed_roots),
            "search_scope": "folder",
        }

    def get_system_file_payload(self, area_key: str, file_path: str) -> dict:
        target_path = Path(file_path).resolve()
        areas = self.system_areas()
        area = next((item for item in areas if str(item.get("key", "")).strip() == str(area_key).strip()), None)
        if area is None:
            raise ValueError(f"Unknown area_key: {area_key}")

        allowed_roots = [
            Path(str(folder.get("path", "")).strip()).resolve()
            for folder in area.get("folders", [])
            if str(folder.get("path", "")).strip()
        ]

        if not any(target_path == root or root in target_path.parents for root in allowed_roots):
            raise ValueError("File path is outside allowed area folders.")

        if not target_path.exists() or not target_path.is_file():
            raise ValueError("System file not found.")

        extension = target_path.suffix.lower()
        preview_text = ""
        if extension not in {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}:
            preview_text = self.read_text_file_preview(target_path)

        entry = {
            "name": target_path.name,
            "path": str(target_path),
            "entry_type": "file",
            "extension": extension,
            "size_bytes": int(target_path.stat().st_size),
            "size_label": self.format_size(int(target_path.stat().st_size)),
        }

        return {
            "area_key": area_key,
            "entry": entry,
            "preview": {
                "text": preview_text,
            },
        }
