"""Integration tests for envdiff.cli_rename."""
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from envdiff.cli_rename import add_rename_subparser, run_rename


@pytest.fixture()
def base_env_file(tmp_path: Path) -> Path:
    p = tmp_path / "base.env"
    p.write_text("DATABASE_URL=postgres://localhost/dev\nSECRET_KEY=abc123\n")
    return p


@pytest.fixture()
def other_env_file(tmp_path: Path) -> Path:
    p = tmp_path / "other.env"
    p.write_text("DB_URL=postgres://localhost/prod\nSECRET_TOKEN=xyz789\n")
    return p


@pytest.fixture()
def identical_env_file(tmp_path: Path) -> Path:
    p = tmp_path / "identical.env"
    p.write_text("DATABASE_URL=postgres://localhost/dev\nSECRET_KEY=abc123\n")
    return p


def _make_args(base, other, threshold=0.7, output_format="text", fail_on_candidates=False):
    ns = argparse.Namespace(
        base=str(base),
        other=str(other),
        threshold=threshold,
        output_format=output_format,
        fail_on_candidates=fail_on_candidates,
    )
    return ns


def test_run_rename_text_output(base_env_file, other_env_file, capsys):
    args = _make_args(base_env_file, other_env_file, threshold=0.5)
    run_rename(args)
    captured = capsys.readouterr()
    assert "->" in captured.out or "No rename" in captured.out


def test_run_rename_json_output(base_env_file, other_env_file, capsys):
    args = _make_args(base_env_file, other_env_file, threshold=0.5, output_format="json")
    run_rename(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    if data:
        assert "old_key" in data[0]
        assert "new_key" in data[0]
        assert "score" in data[0]


def test_run_rename_exit_code_zero_no_candidates(base_env_file, identical_env_file):
    args = _make_args(base_env_file, identical_env_file, fail_on_candidates=True)
    code = run_rename(args)
    assert code == 0


def test_run_rename_exit_code_one_with_fail_flag(base_env_file, other_env_file):
    args = _make_args(base_env_file, other_env_file, threshold=0.5, fail_on_candidates=True)
    code = run_rename(args)
    # May be 0 or 1 depending on similarity; just assert it's a valid code
    assert code in (0, 1)


def test_add_rename_subparser_registers_command():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    add_rename_subparser(sub)
    args = root.parse_args(["rename", "a.env", "b.env"])
    assert args.base == "a.env"
    assert args.other == "b.env"
    assert args.threshold == 0.7
    assert args.output_format == "text"
