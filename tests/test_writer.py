"""Tests for envdiff.writer module."""

import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.writer import write_diff, suggest_filename


@pytest.fixture
def simple_diff():
    return DiffResult(
        missing_in={"prod": {"APP_ENV": "development"}},
        mismatches={"DB_URL": {"dev": "sqlite://", "prod": "postgres://"}},
    )


@pytest.fixture
def empty_diff():
    return DiffResult(missing_in={}, mismatches={})


def test_write_json_to_file(tmp_path, simple_diff):
    out = tmp_path / "report.json"
    write_diff(simple_diff, "json", output_path=str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert "missing_in" in data


def test_write_csv_to_file(tmp_path, simple_diff):
    out = tmp_path / "report.csv"
    write_diff(simple_diff, "csv", output_path=str(out))
    content = out.read_text()
    assert "type" in content
    assert "DB_URL" in content


def test_write_markdown_to_file(tmp_path, simple_diff):
    out = tmp_path / "report.md"
    write_diff(simple_diff, "markdown", output_path=str(out))
    content = out.read_text()
    assert "#" in content


def test_write_creates_parent_dirs(tmp_path, simple_diff):
    out = tmp_path / "nested" / "deep" / "report.json"
    write_diff(simple_diff, "json", output_path=str(out))
    assert out.exists()


def test_write_to_stdout(capsys, simple_diff):
    write_diff(simple_diff, "json")
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "mismatches" in data


def test_write_empty_diff_to_stdout(capsys, empty_diff):
    write_diff(empty_diff, "markdown")
    captured = capsys.readouterr()
    assert "No differences found" in captured.out


def test_suggest_filename_json():
    assert suggest_filename("report", "json") == "report.json"


def test_suggest_filename_csv():
    assert suggest_filename("output", "csv") == "output.csv"


def test_suggest_filename_markdown():
    assert suggest_filename("diff", "markdown") == "diff.md"


def test_suggest_filename_unknown_format():
    assert suggest_filename("diff", "txt") == "diff.txt"
