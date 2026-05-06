"""Tests for envdiff.cli_normalize."""

import json
import pytest
from argparse import Namespace
from unittest.mock import patch

from envdiff.cli_normalize import run_normalize, add_normalize_subparser


ENV_DEV = {"dev": {"DEBUG": "True", "PORT": "8080", "ACTIVE": "yes"}}
ENV_PROD = {"prod": {"DEBUG": "false", "PORT": "443", "ACTIVE": "no"}}


def _args(files=("dev.env",), fmt="text", only_changes=False):
    return Namespace(files=list(files), fmt=fmt, only_changes=only_changes)


def test_run_normalize_text_output(capsys):
    with patch("envdiff.cli_normalize.load_env_files", return_value=ENV_DEV):
        code = run_normalize(_args())
    out = capsys.readouterr().out
    assert code == 0
    assert "[dev]" in out
    assert "DEBUG=true" in out
    assert "PORT=8080" in out


def test_run_normalize_marks_changed_keys(capsys):
    with patch("envdiff.cli_normalize.load_env_files", return_value=ENV_DEV):
        run_normalize(_args())
    out = capsys.readouterr().out
    # Changed keys should have '*' marker
    assert "* DEBUG=true" in out
    assert "* ACTIVE=true" in out
    # Unchanged key should have ' ' marker
    assert "  PORT=8080" in out


def test_run_normalize_only_changes(capsys):
    with patch("envdiff.cli_normalize.load_env_files", return_value=ENV_DEV):
        run_normalize(_args(only_changes=True))
    out = capsys.readouterr().out
    assert "DEBUG" in out
    assert "->" in out
    assert "PORT" not in out


def test_run_normalize_only_changes_none(capsys):
    env = {"prod": {"HOST": "localhost", "PORT": "5432"}}
    with patch("envdiff.cli_normalize.load_env_files", return_value=env):
        run_normalize(_args(only_changes=True))
    out = capsys.readouterr().out
    assert "(no changes)" in out


def test_run_normalize_json_format(capsys):
    with patch("envdiff.cli_normalize.load_env_files", return_value=ENV_DEV):
        code = run_normalize(_args(fmt="json"))
    out = capsys.readouterr().out
    assert code == 0
    data = json.loads(out)
    assert "dev" in data
    assert data["dev"]["DEBUG"] == "true"


def test_run_normalize_json_only_changes(capsys):
    with patch("envdiff.cli_normalize.load_env_files", return_value=ENV_DEV):
        run_normalize(_args(fmt="json", only_changes=True))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "DEBUG" in data["dev"]
    assert "before" in data["dev"]["DEBUG"]
    assert "after" in data["dev"]["DEBUG"]
    assert "PORT" not in data["dev"]


def test_add_normalize_subparser():
    import argparse
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    add_normalize_subparser(sub)
    args = root.parse_args(["normalize", "dev.env", "--only-changes"])
    assert args.only_changes is True
    assert args.files == ["dev.env"]
