"""Tests for envdiff.grouper."""

import pytest
from envdiff.grouper import (
    KeyGroup,
    GroupReport,
    extract_prefix,
    group_keys,
    group_env,
)


# ---------------------------------------------------------------------------
# extract_prefix
# ---------------------------------------------------------------------------

def test_extract_prefix_standard():
    assert extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_delimiter():
    assert extract_prefix("PORT") is None


def test_extract_prefix_custom_delimiter():
    assert extract_prefix("db.host", delimiter=".") == "db"


def test_extract_prefix_multiple_segments_returns_first():
    assert extract_prefix("AWS_S3_BUCKET") == "AWS"


# ---------------------------------------------------------------------------
# group_keys
# ---------------------------------------------------------------------------

def test_group_keys_basic():
    keys = ["DB_HOST", "DB_PORT", "APP_NAME", "APP_ENV", "PORT"]
    report = group_keys(keys)
    assert "DB" in report.groups
    assert "APP" in report.groups
    assert "PORT" in report.ungrouped


def test_group_keys_min_size_respected():
    # Only one key with prefix REDIS — should not form a group
    keys = ["REDIS_URL", "DB_HOST", "DB_PORT"]
    report = group_keys(keys, min_group_size=2)
    assert "REDIS" not in report.groups
    assert "REDIS_URL" in report.ungrouped


def test_group_keys_empty_input():
    report = group_keys([])
    assert not report.has_groups
    assert report.ungrouped == []
    assert report.total_keys == 0


def test_group_keys_all_ungrouped():
    keys = ["PORT", "HOST", "DEBUG"]
    report = group_keys(keys)
    assert not report.has_groups
    assert sorted(report.ungrouped) == sorted(keys)


def test_group_keys_sorted_within_group():
    keys = ["DB_PORT", "DB_HOST", "DB_NAME"]
    report = group_keys(keys)
    assert report.groups["DB"].keys == ["DB_HOST", "DB_NAME", "DB_PORT"]


def test_group_report_total_keys():
    keys = ["DB_HOST", "DB_PORT", "SECRET_KEY", "SECRET_SALT", "PORT"]
    report = group_keys(keys)
    assert report.total_keys == 5


def test_group_report_has_groups_true():
    keys = ["DB_HOST", "DB_PORT"]
    report = group_keys(keys)
    assert report.has_groups is True


# ---------------------------------------------------------------------------
# group_env
# ---------------------------------------------------------------------------

def test_group_env_uses_dict_keys():
    env = {"AWS_KEY": "abc", "AWS_SECRET": "xyz", "DEBUG": "true"}
    report = group_env(env)
    assert "AWS" in report.groups
    assert "DEBUG" in report.ungrouped


def test_key_group_count():
    kg = KeyGroup(prefix="DB", keys=["DB_HOST", "DB_PORT"])
    assert kg.count == 2
