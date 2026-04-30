"""Tests for envdiff.sorter module."""

import pytest
from envdiff.comparator import DiffResult
from envdiff.sorter import (
    sort_keys_alphabetically,
    group_by_prefix,
    sort_diff_result,
    get_all_diff_keys,
)


@pytest.fixture
def unsorted_diff():
    return DiffResult(
        missing={"prod": ["ZEBRA_KEY", "APP_NAME", "DB_HOST"], "dev": ["LOG_LEVEL"]},
        mismatches=[("REDIS_URL", "redis://a", "redis://b"), ("API_KEY", "x", "y")],
    )


def test_sort_keys_alphabetically_basic():
    keys = ["ZEBRA", "apple", "Mango"]
    result = sort_keys_alphabetically(keys)
    assert result == ["apple", "Mango", "ZEBRA"]


def test_sort_keys_alphabetically_empty():
    assert sort_keys_alphabetically([]) == []


def test_group_by_prefix_standard():
    keys = ["DB_HOST", "DB_PORT", "APP_NAME", "LOG_LEVEL"]
    groups = group_by_prefix(keys)
    assert set(groups["DB"]) == {"DB_HOST", "DB_PORT"}
    assert groups["APP"] == ["APP_NAME"]
    assert groups["LOG"] == ["LOG_LEVEL"]


def test_group_by_prefix_no_delimiter():
    keys = ["HOST", "PORT", "DB_NAME"]
    groups = group_by_prefix(keys)
    assert set(groups[""] ) == {"HOST", "PORT"}
    assert groups["DB"] == ["DB_NAME"]


def test_group_by_prefix_custom_delimiter():
    keys = ["app.name", "app.version", "db.host"]
    groups = group_by_prefix(keys, delimiter=".")
    assert set(groups["app"]) == {"app.name", "app.version"}
    assert groups["db"] == ["db.host"]


def test_sort_diff_result_alphabetical(unsorted_diff):
    result = sort_diff_result(unsorted_diff, alphabetical=True)
    assert result.missing["prod"] == ["APP_NAME", "DB_HOST", "ZEBRA_KEY"]
    assert result.missing["dev"] == ["LOG_LEVEL"]
    assert result.mismatches[0][0] == "API_KEY"
    assert result.mismatches[1][0] == "REDIS_URL"


def test_sort_diff_result_preserves_values(unsorted_diff):
    result = sort_diff_result(unsorted_diff)
    mismatch_keys = [t[0] for t in result.mismatches]
    assert "API_KEY" in mismatch_keys
    assert "REDIS_URL" in mismatch_keys


def test_sort_diff_result_no_alphabetical(unsorted_diff):
    result = sort_diff_result(unsorted_diff, alphabetical=False)
    # Order preserved as-is
    assert result.missing["prod"] == ["ZEBRA_KEY", "APP_NAME", "DB_HOST"]


def test_get_all_diff_keys(unsorted_diff):
    keys = get_all_diff_keys(unsorted_diff)
    assert set(keys) == {"ZEBRA_KEY", "APP_NAME", "DB_HOST", "LOG_LEVEL", "REDIS_URL", "API_KEY"}


def test_get_all_diff_keys_empty():
    diff = DiffResult(missing={}, mismatches=[])
    assert get_all_diff_keys(diff) == []
