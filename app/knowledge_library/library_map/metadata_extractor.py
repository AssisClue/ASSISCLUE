from __future__ import annotations

import hashlib
from pathlib import Path


def sha1_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def extract_file_metadata(path: Path) -> dict:
    stat = path.stat()
    return {
        "file_name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": int(stat.st_size),
        "modified_ts": float(stat.st_mtime),
        "sha1": sha1_file(path),
    }