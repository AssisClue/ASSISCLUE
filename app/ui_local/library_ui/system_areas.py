from __future__ import annotations

from pathlib import Path


def build_system_areas(project_root: Path) -> list[dict]:
    areas = [
        {
            "key": "library_sources",
            "title": "Library Sources",
            "kind": "source",
            "description": "Manual folders where the user can place files for the knowledge library.",
            "folders": [
                project_root / "data" / "knowledge_library" / "libraries",
                project_root / "data" / "knowledge_library" / "collections",
                project_root / "data" / "knowledge_library" / "manifests",
            ],
        },
        {
            "key": "knowledge_runtime",
            "title": "Knowledge Runtime",
            "kind": "runtime",
            "description": "Outputs produced by the knowledge library block.",
            "folders": [
                project_root / "runtime" / "knowledge_library" / "maps",
                project_root / "runtime" / "knowledge_library" / "summaries",
                project_root / "runtime" / "knowledge_library" / "indexing",
            ],
        },
        {
            "key": "display_actions",
            "title": "Display Actions",
            "kind": "runtime",
            "description": "Screenshots and results produced by display actions.",
            "folders": [
                project_root / "runtime" / "display_actions" / "screenshots",
                project_root / "runtime" / "display_actions" / "results",
                project_root / "runtime" / "display_actions" / "status",
            ],
        },
        {
            "key": "web_tools",
            "title": "Web Tools",
            "kind": "runtime",
            "description": "Saved pages and screenshots from Playwright / web automation.",
            "folders": [
                project_root / "runtime" / "web" / "pages",
                project_root / "runtime" / "web" / "screenshots",
            ],
        },
        {
            "key": "router_dispatch",
            "title": "Router / Queues",
            "kind": "runtime",
            "description": "Router status and queue files used by the runtime pipeline.",
            "folders": [
                project_root / "runtime" / "router_dispatch",
            ],
        },
        {
            "key": "memory_qdrant",
            "title": "Memory / Qdrant",
            "kind": "runtime",
            "description": "Memory and semantic index runtime folders.",
            "folders": [
                project_root / "runtime" / "memory",
                project_root / "runtime" / "qdrant",
            ],
        },
    ]

    normalized: list[dict] = []
    for area in areas:
        folders = []
        for folder in area["folders"]:
            path = Path(folder)
            folders.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "exists": path.exists(),
                }
            )

        normalized.append(
            {
                "key": area["key"],
                "title": area["title"],
                "kind": area["kind"],
                "description": area["description"],
                "folders": folders,
                "folder_count": len(folders),
            }
        )

    return normalized