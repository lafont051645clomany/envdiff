"""Tests for envdiff.cli_trace."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from envdiff.cli_trace import _json_output, _parse_named_files, _text_output, run_trace
from envdiff.tracer import trace_all


@pytest.fixture()
def env_files(tmp_path: Path):
    dev = tmp_path / "dev.env"
    dev.write_text("APP=myapp\nDEBUG=true\nDB_HOST=localhost\n")
    prod = tmp_path / "prod.env"
    prod.write_text("APP=myapp\nDEBUG=false\nDB_HOST=prod-db\nSECRET=xyz\n")
    return dev, prod


@pytest.fixture()
def sample_report():
    envs = {
        "dev": {"APP": "myapp", "DEBUG": "true"},
        "prod": {"APP": "myapp", "DEBUG": "false"},
    }
    return trace_all(envs)


# --- _parse_named_files ---

def test_parse_named_files_valid():
    result = _parse_named_files(["dev=/tmp/dev.env", "prod=/tmp/prod.env"])
    assert result == {"dev": "/tmp/dev.env", "prod": "/tmp/prod.env"}


def test_parse_named_files_invalid_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        _parse_named_files(["badvalue"])
    assert exc.value.code == 2


# --- _text_output ---

def test_text_output_shows_diff_status(sample_report):
    out = _text_output(sample_report, inconsistent_only=False)
    assert "[DIFF]" in out
    assert "DEBUG" in out


def test_text_output_shows_ok_status(sample_report):
    out = _text_output(sample_report, inconsistent_only=False)
    assert "[OK  ]" in out
    assert "APP" in out


def test_text_output_inconsistent_only_filters(sample_report):
    out = _text_output(sample_report, inconsistent_only=True)
    assert "DEBUG" in out
    assert "APP" not in out


def test_text_output_missing_shown_as_missing():
    envs = {"dev": {"ONLY_DEV": "val"}, "prod": {}}
    report = trace_all(envs)
    out = _text_output(report, inconsistent_only=False)
    assert "<missing>" in out


# --- _json_output ---

def test_json_output_structure(sample_report):
    raw = _json_output(sample_report, inconsistent_only=False)
    data = json.loads(raw)
    assert "env_names" in data
    assert "keys" in data
    assert "DEBUG" in data["keys"]


def test_json_output_inconsistent_flag(sample_report):
    raw = _json_output(sample_report, inconsistent_only=False)
    data = json.loads(raw)
    assert data["keys"]["DEBUG"]["consistent"] is False
    assert data["keys"]["APP"]["consistent"] is True


# --- run_trace integration ---

def test_run_trace_text(env_files, capsys):
    dev, prod = env_files
    args = SimpleNamespace(
        files=[f"dev={dev}", f"prod={prod}"],
        inconsistent_only=False,
        format="text",
        func=run_trace,
    )
    run_trace(args)
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out


def test_run_trace_json(env_files, capsys):
    dev, prod = env_files
    args = SimpleNamespace(
        files=[f"dev={dev}", f"prod={prod}"],
        inconsistent_only=False,
        format="json",
        func=run_trace,
    )
    run_trace(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "keys" in data
