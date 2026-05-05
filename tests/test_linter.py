"""Tests for envdiff.linter module."""

import pytest
from pathlib import Path
from envdiff.linter import lint_env_file, lint_multiple, LintResult, LintIssue


@pytest.fixture
def valid_env_file(tmp_path: Path) -> str:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPI_KEY=secret\n")
    return str(p)


@pytest.fixture
def problematic_env_file(tmp_path: Path) -> str:
    p = tmp_path / ".env.bad"
    p.write_text(
        "db_host=localhost\n"          # lowercase key
        "DB_PORT=5432\n"
        "GREETING=hello world\n"       # unquoted value with space
        "DB_PORT=9999\n"               # duplicate key
        "EMPTY_KEY=\n"                 # empty value
        "no_equals_here\n"             # missing '='
    )
    return str(p)


def test_valid_file_no_issues(valid_env_file):
    result = lint_env_file(valid_env_file)
    assert isinstance(result, LintResult)
    assert not result.has_issues
    assert result.error_count == 0
    assert result.warning_count == 0


def test_file_not_found():
    result = lint_env_file("/nonexistent/path/.env")
    assert result.has_issues
    assert result.error_count == 1
    assert "not found" in result.issues[0].message.lower()


def test_lowercase_key_warning(problematic_env_file):
    result = lint_env_file(problematic_env_file)
    keys_warned = [i.key for i in result.issues if "UPPER_SNAKE_CASE" in i.message]
    assert "db_host" in keys_warned


def test_unquoted_space_warning(problematic_env_file):
    result = lint_env_file(problematic_env_file)
    space_issues = [i for i in result.issues if "spaces" in i.message]
    assert any(i.key == "GREETING" for i in space_issues)


def test_duplicate_key_error(problematic_env_file):
    result = lint_env_file(problematic_env_file)
    dup_issues = [i for i in result.issues if "Duplicate" in i.message]
    assert len(dup_issues) == 1
    assert dup_issues[0].key == "DB_PORT"
    assert dup_issues[0].severity == "error"


def test_empty_value_warning(problematic_env_file):
    result = lint_env_file(problematic_env_file)
    empty_issues = [i for i in result.issues if "empty value" in i.message]
    assert any(i.key == "EMPTY_KEY" for i in empty_issues)


def test_missing_equals_error(problematic_env_file):
    result = lint_env_file(problematic_env_file)
    eq_issues = [i for i in result.issues if "separator" in i.message]
    assert len(eq_issues) == 1
    assert eq_issues[0].severity == "error"


def test_lint_multiple_returns_all_results(valid_env_file, problematic_env_file):
    results = lint_multiple([valid_env_file, problematic_env_file])
    assert len(results) == 2
    assert not results[0].has_issues
    assert results[1].has_issues


def test_comments_and_blank_lines_ignored(tmp_path):
    p = tmp_path / ".env"
    p.write_text("# This is a comment\n\nDB_HOST=localhost\n")
    result = lint_env_file(str(p))
    assert not result.has_issues
