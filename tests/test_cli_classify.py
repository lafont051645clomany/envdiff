"""Tests for envdiff.cli_classify."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envdiff.cli_classify import run_classify, add_classify_subparser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Args:
    def __init__(self, files, fmt="text", category=None):
        self.files = files
        self.fmt = fmt
        self.category = category


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env.dev"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "JWT_SECRET=topsecret\n"
        "LOG_LEVEL=debug\n"
        "APP_ENV=development\n"
    )
    return p


# ---------------------------------------------------------------------------
# Text output
# ---------------------------------------------------------------------------

def test_run_classify_text_output(env_file, capsys):
    args = _Args(files=[str(env_file)])
    run_classify(args)
    captured = capsys.readouterr()
    assert "[database]" in captured.out
    assert "DB_HOST" in captured.out


def test_run_classify_text_shows_auth(env_file, capsys):
    args = _Args(files=[str(env_file)])
    run_classify(args)
    captured = capsys.readouterr()
    assert "[auth]" in captured.out
    assert "JWT_SECRET" in captured.out


def test_run_classify_text_shows_other(env_file, capsys):
    args = _Args(files=[str(env_file)])
    run_classify(args)
    captured = capsys.readouterr()
    assert "APP_ENV" in captured.out


# ---------------------------------------------------------------------------
# Category filter
# ---------------------------------------------------------------------------

def test_run_classify_category_filter(env_file, capsys):
    args = _Args(files=[str(env_file)], category="database")
    run_classify(args)
    captured = capsys.readouterr()
    assert "DB_HOST" in captured.out
    assert "JWT_SECRET" not in captured.out


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def test_run_classify_json_output(env_file, capsys):
    args = _Args(files=[str(env_file)], fmt="json")
    run_classify(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    env_name = str(env_file)
    assert env_name in data
    assert "database" in data[env_name]
    assert "DB_HOST" in data[env_name]["database"]


def test_run_classify_json_category_filter(env_file, capsys):
    args = _Args(files=[str(env_file)], fmt="json", category="database")
    run_classify(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    env_name = str(env_file)
    assert list(data[env_name].keys()) == ["database"]


# ---------------------------------------------------------------------------
# Subparser registration
# ---------------------------------------------------------------------------

def test_add_classify_subparser_registers():
    import argparse
    main_parser = argparse.ArgumentParser()
    subs = main_parser.add_subparsers()
    add_classify_subparser(subs)
    args = main_parser.parse_args(["classify", "some_file"])
    assert args.func is run_classify
