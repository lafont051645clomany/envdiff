"""Tests for envdiff.snapshot."""

import json
import pytest
from pathlib import Path

from envdiff.snapshot import (
    create_snapshot,
    save_snapshot,
    load_snapshot,
    diff_against_snapshot,
    SNAPSHOT_VERSION,
)


@pytest.fixture()
def sample_env():
    return {"APP_ENV": "production", "DB_HOST": "db.example.com", "PORT": "5432"}


def test_create_snapshot_structure(sample_env):
    snap = create_snapshot(sample_env, label="prod")
    assert snap["version"] == SNAPSHOT_VERSION
    assert snap["label"] == "prod"
    assert snap["env"] == sample_env
    assert "created_at" in snap


def test_create_snapshot_empty_label(sample_env):
    snap = create_snapshot(sample_env)
    assert snap["label"] == ""


def test_save_and_load_roundtrip(tmp_path, sample_env):
    dest = tmp_path / "snapshots" / "prod.json"
    returned_path = save_snapshot(sample_env, dest, label="prod")
    assert returned_path == dest
    assert dest.exists()

    loaded = load_snapshot(dest)
    assert loaded["env"] == sample_env
    assert loaded["label"] == "prod"
    assert loaded["version"] == SNAPSHOT_VERSION


def test_load_snapshot_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError, match="Snapshot not found"):
        load_snapshot(tmp_path / "missing.json")


def test_load_snapshot_invalid_json(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not-json", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid snapshot JSON"):
        load_snapshot(bad)


def test_load_snapshot_missing_fields(tmp_path):
    incomplete = tmp_path / "incomplete.json"
    incomplete.write_text(json.dumps({"version": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required fields"):
        load_snapshot(incomplete)


def test_diff_against_snapshot_no_changes(tmp_path, sample_env):
    dest = tmp_path / "snap.json"
    save_snapshot(sample_env, dest)
    changes = diff_against_snapshot(sample_env, dest)
    assert changes == {}


def test_diff_against_snapshot_detects_changed_value(tmp_path, sample_env):
    dest = tmp_path / "snap.json"
    save_snapshot(sample_env, dest)
    current = {**sample_env, "PORT": "6543"}
    changes = diff_against_snapshot(current, dest)
    assert "PORT" in changes
    assert changes["PORT"] == {"snapshot": "5432", "current": "6543"}


def test_diff_against_snapshot_detects_added_key(tmp_path, sample_env):
    dest = tmp_path / "snap.json"
    save_snapshot(sample_env, dest)
    current = {**sample_env, "NEW_KEY": "hello"}
    changes = diff_against_snapshot(current, dest)
    assert "NEW_KEY" in changes
    assert changes["NEW_KEY"] == {"snapshot": None, "current": "hello"}


def test_diff_against_snapshot_detects_removed_key(tmp_path, sample_env):
    dest = tmp_path / "snap.json"
    save_snapshot(sample_env, dest)
    current = {k: v for k, v in sample_env.items() if k != "DB_HOST"}
    changes = diff_against_snapshot(current, dest)
    assert "DB_HOST" in changes
    assert changes["DB_HOST"] == {"snapshot": "db.example.com", "current": None}
