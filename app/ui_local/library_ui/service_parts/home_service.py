from __future__ import annotations

from .common import BaseUiService


class HomeViewService(BaseUiService):
    def _filter_library_items(
        self,
        items: list[dict],
        *,
        search: str = "",
        extension: str = "",
        root_id: str = "",
    ) -> list[dict]:
        search_q = self.normalize_query(search)
        ext_q = self.normalize_extension(extension)
        root_q = str(root_id or "").strip()

        filtered: list[dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue

            if root_q and str(item.get("root_id", "")).strip() != root_q:
                continue

            item_ext = str(item.get("extension", "")).strip().lower()
            if ext_q and item_ext != ext_q:
                continue

            if search_q:
                if not self.flexible_match(
                    query=search_q,
                    name=str(item.get("file_name", "") or ""),
                    path=str(item.get("relative_path", "") or ""),
                    extension=item_ext,
                    extra_terms=[
                        str(item.get("root_name", "") or ""),
                        str(item.get("absolute_path", "") or ""),
                    ],
                ):
                    continue

            filtered.append(item)

        return filtered

    def get_home_payload(
        self,
        *,
        search: str = "",
        extension: str = "",
        root_id: str = "",
    ) -> dict:
        roots = self.facade.list_roots()
        library_map = self.facade.get_library_map()
        all_items = library_map.get("items", []) if isinstance(library_map, dict) else []
        items = self._filter_library_items(
            all_items,
            search=search,
            extension=extension,
            root_id=root_id,
        )

        should_retry_with_scan = bool(str(search or "").strip() or str(extension or "").strip() or str(root_id or "").strip())
        if should_retry_with_scan and not items:
            try:
                self.facade.scan_all()
            except Exception:
                pass
            library_map = self.facade.get_library_map()
            all_items = library_map.get("items", []) if isinstance(library_map, dict) else []
            items = self._filter_library_items(
                all_items,
                search=search,
                extension=extension,
                root_id=root_id,
            )

        return {
            "roots": roots,
            "library_map": library_map if isinstance(library_map, dict) else {},
            "items": items,
            "all_item_count": len(all_items),
            "root_count": len(roots),
            "item_count": len(items),
            "areas": self.system_areas(),
            "filters": {
                "search": str(search or "").strip(),
                "extension": self.normalize_extension(extension),
                "root_id": str(root_id or "").strip(),
            },
            "extension_options": self.collect_library_extensions(all_items),
        }
