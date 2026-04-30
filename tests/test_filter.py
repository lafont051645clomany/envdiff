"""Tests for envdiff.filter module."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.filter import filter_keys_by_pattern, filter_diff_by_pattern


@pytest.fixture
def sample_diff():
    return DiffResult(
        missing={
            "prod": ["DB_HOST", "APP_SECRET", "LOG_LEVEL"],
            "dev": ["REDIS_URL"],
        },
        mismatches=[
            ("DB_PORT", "5432", "5433"),
            ("API_KEY", "abc", "xyz"),
        ],
    )


def test_filter_keys_by_pattern_basic():
    keys = ["DB_HOST", "DB_PORT", "APP_NAME", "LOG_LEVEL"]
    result = filter_keys_by_pattern(keys, r"^DB_")
    assert result == ["DB_HOST", "DB_PORT"]


def test_filter_keys_by_pattern_case_insensitive():
    keys = ["db_host", "APP_NAME"]
    result = filter_keys_by_pattern(keys, r"db")
    assert result == ["db_host"]


def test_filter_keys_by_pattern_invert():
    keys = ["DB_HOST", "APP_NAME", "DB_PORT"]
    result = filter_keys_by_pattern(keys, r"^DB_", invert=True)
    assert result == ["APP_NAME"]


def test_filter_keys_by_pattern_no_match():
    keys = ["APP_NAME", "LOG_LEVEL"]
    result = filter_keys_by_pattern(keys, r"^DB_")
    assert result == []


def test_filter_diff_by_pattern_missing(sample_diff):
    result = filter_diff_by_pattern(sample_diff, r"^DB")
    assert result.missing == {"prod": ["DB_HOST"]}
    assert result.mismatches == [("DB_PORT", "5432", "5433")]


def test_filter_diff_by_pattern_none_returns_unchanged(sample_diff):
    result = filter_diff_by_pattern(sample_diff, None)
    assert result.missing == sample_diff.missing
    assert result.mismatches == sample_diff.mismatches


def test_filter_diff_by_pattern_invert(sample_diff):
    result = filter_diff_by_pattern(sample_diff, r"^DB", invert=True)
    assert "DB_HOST" not in result.missing.get("prod", [])
    assert all(key != "DB_PORT" for key, _, _ in result.mismatches)


def test_filter_diff_removes_empty_env_entries(sample_diff):
    # dev only has REDIS_URL, filtering for DB should remove dev entirely
    result = filter_diff_by_pattern(sample_diff, r"^DB")
    assert "dev" not in result.missing


def test_filter_diff_all_filtered_out(sample_diff):
    result = filter_diff_by_pattern(sample_diff, r"^NONEXISTENT")
    assert result.missing == {}
    assert result.mismatches == []
