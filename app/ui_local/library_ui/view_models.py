from __future__ import annotations


def build_home_vm(payload: dict) -> dict:
    roots = payload.get("roots", [])
    items = payload.get("items", [])
    areas = payload.get("areas", [])
    filters = payload.get("filters", {}) if isinstance(payload.get("filters", {}), dict) else {}

    return {
        "roots": roots,
        "items": items,
        "areas": areas,
        "root_count": payload.get("root_count", len(roots)),
        "item_count": payload.get("item_count", len(items)),
        "all_item_count": payload.get("all_item_count", len(items)),
        "library_map": payload.get("library_map", {}),
        "filters": filters,
        "extension_options": payload.get("extension_options", []),
    }


def build_file_vm(payload: dict) -> dict:
    item = payload.get("item", {}) if isinstance(payload.get("item", {}), dict) else {}
    preview = payload.get("preview", {}) if isinstance(payload.get("preview", {}), dict) else {}
    summary = payload.get("summary", {}) if isinstance(payload.get("summary", {}), dict) else {}
    index_status = payload.get("index_status", {}) if isinstance(payload.get("index_status", {}), dict) else {}
    promoted = bool(payload.get("promoted", False))

    extension = str(item.get("extension", "") or "").strip().lower()
    preview_kind = "text"
    if extension in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}:
        preview_kind = "image"
    elif extension == ".pdf":
        preview_kind = "pdf"

    flags = {
        "has_summary": bool(str(summary.get("summary_text", "") or "").strip()),
        "is_indexed": bool(index_status),
        "is_promoted": promoted,
    }

    item_id = str(item.get("item_id", "") or "").strip()

    return {
        "item": item,
        "preview": preview,
        "summary": summary,
        "index_status": index_status,
        "promoted": promoted,
        "flags": flags,
        "preview_kind": preview_kind,
        "raw_file_url": f"/raw-file/{item_id}" if item_id else "",
    }


def build_area_vm(payload: dict) -> dict:
    return {
        "area": payload.get("area", {}) if isinstance(payload.get("area", {}), dict) else {},
        "roots": payload.get("roots", []) if isinstance(payload.get("roots", []), list) else [],
    }


def build_area_browser_vm(payload: dict) -> dict:
    return {
        "area": payload.get("area", {}) if isinstance(payload.get("area", {}), dict) else {},
        "entries": payload.get("entries", []) if isinstance(payload.get("entries", []), list) else [],
        "all_entry_count": payload.get("all_entry_count", len(payload.get("entries", []))),
        "filters": payload.get("filters", {}) if isinstance(payload.get("filters", {}), dict) else {},
        "extension_options": payload.get("extension_options", []),
        "current_folder_path": str(payload.get("current_folder_path", "") or "").strip(),
        "breadcrumbs": payload.get("breadcrumbs", []) if isinstance(payload.get("breadcrumbs", []), list) else [],
    }


def build_system_file_vm(payload: dict) -> dict:
    entry = payload.get("entry", {}) if isinstance(payload.get("entry", {}), dict) else {}
    preview = payload.get("preview", {}) if isinstance(payload.get("preview", {}), dict) else {}
    area_key = str(payload.get("area_key", "") or "").strip()

    extension = str(entry.get("extension", "") or "").strip().lower()
    preview_kind = "text"
    if extension in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}:
        preview_kind = "image"
    elif extension == ".pdf":
        preview_kind = "pdf"

    raw_url = f"/system-raw-file?area_key={area_key}&file_path={entry.get('path', '')}"

    return {
        "area_key": area_key,
        "entry": entry,
        "preview": preview,
        "preview_kind": preview_kind,
        "raw_file_url": raw_url,
        "item": entry,
    }