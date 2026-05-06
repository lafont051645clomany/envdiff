"""Tests for envdiff.exporter module."""

import json
import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export_diff, EXPORT_FORMATS


@pytest.fixture
def empty_diff():
    return DiffResult(missing_in={}, mismatches={})


@pytest.fixture
def rich_diff():
    return DiffResult(
        missing_in={
            "production": {"DEBUG": "true"},
            "staging": {"SECRET_KEY": "abc123"},
        },
        mismatches={
            "DB_HOST": {"development": "localhost", "production": "db.prod.example.com"},
        },
    )


def test_export_formats_constant():
    assert "json" in EXPORT_FORMATS
    assert "csv" in EXPORT_FORMATS
    assert "markdown" in EXPORT_FORMATS


def test_unsupported_format_raises(empty_diff):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_diff(empty_diff, "xml")


def test_export_json_structure(rich_diff):
    result = export_diff(rich_diff, "json")
    data = json.loads(result)
    assert "missing_in" in data
    assert "mismatches" in data
    assert "production" in data["missing_in"]
    assert "DB_HOST" in data["mismatches"]


def test_export_json_empty(empty_diff):
    result = export_diff(empty_diff, "json")
    data = json.loads(result)
    assert data["missing_in"] == {}
    assert data["mismatches"] == {}


def test_export_csv_headers(rich_diff):
    result = export_diff(rich_diff, "csv")
    first_line = result.splitlines()[0]
    assert "type" in first_line
    assert "key" in first_line
    assert "environment" in first_line
    assert "value" in first_line


def test_export_csv_contains_missing_rows(rich_diff):
    result = export_diff(rich_diff, "csv")
    assert "missing" in result
    assert "DEBUG" in result
    assert "production" in result


def test_export_csv_contains_mismatch_rows(rich_diff):
    result = export_diff(rich_diff, "csv")
    assert "mismatch" in result
    assert "DB_HOST" in result


def test_export_markdown_headings(rich_diff):
    result = export_diff(rich_diff, "markdown")
    assert "## Missing Keys" in result
    assert "## Mismatched Values" in result


def test_export_markdown_no_diff_message(empty_diff):
    result = export_diff(empty_diff, "markdown")
    assert "No differences found" in result


def test_export_markdown_contains_key_details(rich_diff):
    """Ensure markdown output includes key names and environment details."""
    result = export_diff(rich_diff, "markdown")
    assert "DEBUG" in result
    assert "production" in result
    assert "DB_HOST" in result
    assert "localhost" in result or "db.prod.example.com" in result


def test_export_mask_secrets(rich_diff):
    result = export_diff(rich_diff, "json", mask_secrets=True)
    data = json.loads(result)
    # SECRET_KEY in staging missing_in should be masked
    staging_missing = data["missing_in"].get("staging", {})
    if "SECRET_KEY" in staging_missing:
        assert staging_missing["SECRET_KEY"] == "****"


def test_export_mask_secrets_csv(rich_diff):
    """Ensure secret values are masked in CSV output when mask_secrets is enabled."""
    result = export_diff(rich_diff, "csv", mask_secrets=True)
    assert "abc123" not in result
