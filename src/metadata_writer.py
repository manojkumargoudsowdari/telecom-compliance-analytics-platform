from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_run_metadata(
    metadata_root: str | Path,
    run_id: str,
    metadata: dict[str, Any],
) -> Path:
    metadata_directory = Path(metadata_root)
    metadata_directory.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_directory / f"{run_id}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata_path
