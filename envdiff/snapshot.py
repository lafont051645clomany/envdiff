"""Snapshot module: save and load .env snapshots for drift detection."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

SNAPSHOT_VERSION = 1


def create_snapshot(env: Dict[str, str], label: str = "") -> dict:
    """Create a snapshot dict from an env mapping."""
    return {
        "version": SNAPSHOT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label,
        "env": dict(env),
    }


def save_snapshot(env: Dict[str, str], path: str | os.PathLike, label: str = "") -> Path:
    """Persist an env snapshot to a JSON file.

    Args:
        env: Mapping of key/value pairs to snapshot.
        path: Destination file path (will be created if missing).
        label: Optional human-readable label stored in the snapshot.

    Returns:
        Resolved Path of the written file.
    """
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    snapshot = create_snapshot(env, label=label)
    dest.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    return dest


def load_snapshot(path: str | os.PathLike) -> dict:
    """Load a snapshot from disk.

    Raises:
        FileNotFoundError: If the snapshot file does not exist.
        ValueError: If the file is not a valid snapshot.
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Snapshot not found: {src}")
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid snapshot JSON in {src}: {exc}") from exc
    if "env" not in data or "version" not in data:
        raise ValueError(f"Missing required fields in snapshot: {src}")
    return data


def diff_against_snapshot(
    current_env: Dict[str, str],
    snapshot_path: str | os.PathLike,
) -> Dict[str, dict]:
    """Compare a live env dict against a saved snapshot.

    Returns a dict mapping changed keys to {"snapshot": old, "current": new}.
    Keys present only in snapshot have current=None; keys only in current have
    snapshot=None.
    """
    snapshot_data = load_snapshot(snapshot_path)
    snapshot_env: Dict[str, Optional[str]] = snapshot_data["env"]

    all_keys = set(snapshot_env) | set(current_env)
    changes: Dict[str, dict] = {}
    for key in sorted(all_keys):
        snap_val = snapshot_env.get(key)
        curr_val = current_env.get(key)
        if snap_val != curr_val:
            changes[key] = {"snapshot": snap_val, "current": curr_val}
    return changes
