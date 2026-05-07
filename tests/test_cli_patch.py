"""Tests for envdiff.cli_patch."""

import json
from types import SimpleNamespace

import pytest

from envdiff.cli_patch import _format_text, run_patch
from envdiff.patcher import PatchEntry, PatchReport


# ---------------------------------------------------------------------------
# Fixtures – temporary .env files
# ---------------------------------------------------------------------------

@pytest.fixture()
def source_env_file(tmp_path):
    f = tmp_path / "source.env"
    f.write_text("DB_HOST=prod-db\nDB_PORT=5432\nAPI_KEY=secret\n")
    return str(f)


@pytest.fixture()
def target_env_file(tmp_path):
    f = tmp_path / "target.env"
    f.write_text("DB_HOST=localhost\nDEBUG=true\n")
    return str(f)


@pytest.fixture()
def identical_env_file(tmp_path):
    f = tmp_path / "identical.env"
    f.write_text("DB_HOST=prod-db\nDB_PORT=5432\nAPI_KEY=secret\n")
    return str(f)


def _args(**kwargs):
    defaults = {"removals": False, "fmt": "text"}
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# _format_text
# ---------------------------------------------------------------------------

def test_format_text_no_patches():
    report = PatchReport(source_label="a", target_label="b", entries=[])
    out = _format_text(report)
    assert "sync" in out.lower()


def test_format_text_shows_entries():
    entries = [
        PatchEntry(key="FOO", action="add", new_value="bar"),
        PatchEntry(key="BAZ", action="remove", old_value="old"),
    ]
    report = PatchReport(source_label="src", target_label="tgt", entries=entries)
    out = _format_text(report)
    assert "FOO" in out
    assert "BAZ" in out


# ---------------------------------------------------------------------------
# run_patch – exit codes
# ---------------------------------------------------------------------------

def test_run_patch_exit_one_when_patches_exist(source_env_file, target_env_file):
    args = _args(source=source_env_file, target=target_env_file)
    assert run_patch(args) == 1


def test_run_patch_exit_zero_when_in_sync(source_env_file, identical_env_file):
    args = _args(source=source_env_file, target=identical_env_file)
    assert run_patch(args) == 0


def test_run_patch_missing_file_returns_two(source_env_file):
    args = _args(source=source_env_file, target="/nonexistent/.env")
    assert run_patch(args) == 2


# ---------------------------------------------------------------------------
# run_patch – JSON output
# ---------------------------------------------------------------------------

def test_run_patch_json_output(source_env_file, target_env_file, capsys):
    args = _args(source=source_env_file, target=target_env_file, fmt="json")
    run_patch(args)
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert "entries" in data
    assert isinstance(data["entries"], list)


# ---------------------------------------------------------------------------
# run_patch – removals flag
# ---------------------------------------------------------------------------

def test_run_patch_removals_flag(source_env_file, target_env_file, capsys):
    args = _args(source=source_env_file, target=target_env_file, removals=True)
    run_patch(args)
    captured = capsys.readouterr().out
    # DEBUG key exists only in target; should appear as a removal suggestion
    assert "DEBUG" in captured
