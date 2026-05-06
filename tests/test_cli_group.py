"""Tests for envdiff.cli_group."""

import json
import types
from pathlib import Path

import pytest

from envdiff.cli_group import run_group


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _args(files, delimiter="_", min_size=2, fmt="text"):
    ns = types.SimpleNamespace(
        files=files,
        delimiter=delimiter,
        min_size=min_size,
        fmt=fmt,
    )
    return ns


@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "DB_NAME=mydb\n"
        "APP_ENV=production\n"
        "APP_DEBUG=false\n"
        "PORT=8080\n"
    )
    return p


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_run_group_text_output(env_file, capsys):
    rc = run_group(_args([str(env_file)]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "[DB]" in out
    assert "[APP]" in out
    assert "DB_HOST" in out


def test_run_group_ungrouped_shown(env_file, capsys):
    rc = run_group(_args([str(env_file)]))
    out = capsys.readouterr().out
    assert "[ungrouped]" in out
    assert "PORT" in out


def test_run_group_json_output(env_file, capsys):
    rc = run_group(_args([str(env_file)], fmt="json"))
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert "groups" in data
    assert "ungrouped" in data
    assert "total_keys" in data
    assert "DB" in data["groups"]


def test_run_group_json_total_keys(env_file, capsys):
    run_group(_args([str(env_file)], fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total_keys"] == 6


def test_run_group_custom_min_size(env_file, capsys):
    # With min_size=4 no prefix has enough keys → everything ungrouped
    rc = run_group(_args([str(env_file)], min_size=4))
    out = capsys.readouterr().out
    assert rc == 0
    assert "[ungrouped]" in out


def test_run_group_empty_file(tmp_path, capsys):
    empty = tmp_path / ".env"
    empty.write_text("")
    rc = run_group(_args([str(empty)]))
    out = capsys.readouterr().out
    assert rc == 0
    assert "No keys found" in out
