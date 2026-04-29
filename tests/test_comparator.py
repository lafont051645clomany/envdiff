"""Tests for the envdiff.comparator module."""

import pytest
from envdiff.comparator import compare_envs, DiffResult


@pytest.fixture
def identical_envs():
    return {
        ".env.dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        ".env.prod": {"DB_HOST": "localhost", "DEBUG": "true"},
    }


@pytest.fixture
def envs_with_missing():
    return {
        ".env.dev": {"DB_HOST": "localhost", "DEBUG": "true", "EXTRA_KEY": "value"},
        ".env.prod": {"DB_HOST": "localhost", "DEBUG": "true"},
    }


@pytest.fixture
def envs_with_mismatches():
    return {
        ".env.dev": {"DB_HOST": "localhost", "DEBUG": "true"},
        ".env.prod": {"DB_HOST": "db.prod.example.com", "DEBUG": "false"},
    }


def test_identical_envs_no_diff(identical_envs):
    result = compare_envs(identical_envs)
    assert not result.has_differences
    assert result.missing_keys == {}
    assert result.mismatched_keys == {}


def test_missing_key_detected(envs_with_missing):
    result = compare_envs(envs_with_missing)
    assert result.has_differences
    assert "EXTRA_KEY" in result.missing_keys
    assert ".env.prod" in result.missing_keys["EXTRA_KEY"]
    assert ".env.dev" not in result.missing_keys.get("EXTRA_KEY", [])


def test_mismatched_values_detected(envs_with_mismatches):
    result = compare_envs(envs_with_mismatches)
    assert result.has_differences
    assert "DB_HOST" in result.mismatched_keys
    assert "DEBUG" in result.mismatched_keys
    assert result.mismatched_keys["DB_HOST"][".env.dev"] == "localhost"
    assert result.mismatched_keys["DB_HOST"][".env.prod"] == "db.prod.example.com"


def test_all_keys_collected(envs_with_missing):
    result = compare_envs(envs_with_missing)
    assert result.all_keys == {"DB_HOST", "DEBUG", "EXTRA_KEY"}


def test_files_list_preserved(identical_envs):
    result = compare_envs(identical_envs)
    assert set(result.files) == {".env.dev", ".env.prod"}


def test_single_file_no_diff():
    result = compare_envs({".env": {"KEY": "value"}})
    assert not result.has_differences


def test_empty_envs():
    result = compare_envs({".env.dev": {}, ".env.prod": {}})
    assert not result.has_differences
    assert result.all_keys == set()
