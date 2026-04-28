from __future__ import annotations

from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from app.knowledge_library.contracts.library_types import FileScanRecord, RegisteredRoot

from .metadata_extractor import extract_file_metadata


class FileRegistry:
    def build_record(self, *, root: RegisteredRoot, file_path: Path) -> FileScanRecord:
        rel_path = str(file_path.relative_to(Path(root.path))).replace("\\", "/")
        meta = extract_file_metadata(file_path)
        return FileScanRecord(
            root_id=root.root_id,
            relative_path=rel_path,
            absolute_path=str(file_path),
            file_name=meta["file_name"],
            extension=meta["extension"],
            size_bytes=meta["size_bytes"],
            modified_ts=meta["modified_ts"],
            sha1=meta["sha1"],
            tags=list(root.tags),
        )

    def build_item_id(self, root_id: str, relative_path: str) -> str:
        return str(uuid5(NAMESPACE_URL, f"knowledge-library:{root_id}:{relative_path}"))