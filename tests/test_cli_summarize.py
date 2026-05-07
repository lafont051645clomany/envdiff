"""Tests for envdiff.cli_summarize."""

import json
import pytest

from envdiff.cli_summarize import run_summarize, _format_text, _format_json
from envdiff.summarizer import summarize_env


class _Args:
    def __init__(self, files, fmt="text"):
        self.files = files
        self.fmt = fmt


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(
        "DB_HOST=localhost\n"
        "DB_PASSWORD=secret\n"
        "EMPTY=\n"
        "DEBUG=true\n"
    )
    return str(p)


def test_run_summarize_text_output(env_file, capsys):
    args = _Args(files=[env_file], fmt="text")
    run_summarize(args)
    captured = capsys.readouterr()
    assert "Total keys" in captured.out
    assert "Secret keys" in captured.out


def test_run_summarize_json_output(env_file, capsys):
    args = _Args(files=[env_file], fmt="json")
    run_summarize(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["total_keys"] == 4


def test_format_text_shows_label():
    s = summarize_env("production", {"KEY": "val"})
    output = _format_text([s])
    assert "production" in output


def test_format_text_shows_counts():
    s = summarize_env("dev", {"API_KEY": "abc", "HOST": "localhost", "EMPTY": ""})
    output = _format_text([s])
    assert "Empty keys" in output
    assert "Secret keys" in output


def test_format_json_structure():
    s = summarize_env("dev", {"DB_PASSWORD": "x", "HOST": "h"})
    output = _format_json([s])
    data = json.loads(output)
    assert data[0]["label"] == "dev"
    assert "categories" in data[0]


def test_format_text_multiple_envs():
    s1 = summarize_env("dev", {"A": "1"})
    s2 = summarize_env("prod", {"A": "1", "B": "2"})
    output = _format_text([s1, s2])
    assert "dev" in output
    assert "prod" in output
