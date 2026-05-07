"""Tests for envdiff.stripper."""

import pytest

from envdiff.stripper import (
    StripReport,
    reference_from_envs,
    strip_all,
    strip_keys,
)


@pytest.fixture()
def base_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DB_HOST": "localhost",
        "LEGACY_KEY": "old",
        "SECRET_TOKEN": "abc123",
    }


@pytest.fixture()
def reference() -> set:
    return {"APP_NAME", "DB_HOST", "SECRET_TOKEN"}


# ---------------------------------------------------------------------------
# strip_keys
# ---------------------------------------------------------------------------


def test_strip_keys_removes_stale_key(base_env, reference):
    report = strip_keys(base_env, reference, label="dev")
    assert "LEGACY_KEY" in report.removed_keys


def test_strip_keys_retains_valid_keys(base_env, reference):
    report = strip_keys(base_env, reference, label="dev")
    assert "APP_NAME" in report.stripped
    assert "DB_HOST" in report.stripped
    assert "SECRET_TOKEN" in report.stripped


def test_strip_keys_removed_keys_sorted(base_env):
    ref = {"APP_NAME"}
    report = strip_keys(base_env, ref)
    assert report.removed_keys == sorted(report.removed_keys)


def test_strip_keys_no_removals_when_all_valid(base_env, reference):
    env = {"APP_NAME": "x", "DB_HOST": "y", "SECRET_TOKEN": "z"}
    report = strip_keys(env, reference)
    assert not report.has_removals
    assert report.removal_count == 0


def test_strip_keys_empty_env():
    report = strip_keys({}, {"APP_NAME"})
    assert report.stripped == {}
    assert report.removed_keys == []


def test_strip_keys_label_stored(base_env, reference):
    report = strip_keys(base_env, reference, label="staging")
    assert report.label == "staging"


def test_strip_keys_original_unchanged(base_env, reference):
    report = strip_keys(base_env, reference)
    assert report.original == base_env


# ---------------------------------------------------------------------------
# to_dict
# ---------------------------------------------------------------------------


def test_to_dict_contains_expected_keys(base_env, reference):
    report = strip_keys(base_env, reference, label="prod")
    d = report.to_dict()
    assert "label" in d
    assert "removed_keys" in d
    assert "removal_count" in d
    assert "has_removals" in d
    assert "stripped" in d


# ---------------------------------------------------------------------------
# strip_all
# ---------------------------------------------------------------------------


def test_strip_all_returns_report_per_env():
    envs = {
        "dev": {"A": "1", "B": "2", "STALE": "x"},
        "prod": {"A": "1", "B": "2"},
    }
    reports = strip_all(envs, reference={"A", "B"})
    assert set(reports.keys()) == {"dev", "prod"}


def test_strip_all_dev_has_removal():
    envs = {
        "dev": {"A": "1", "STALE": "x"},
        "prod": {"A": "1"},
    }
    reports = strip_all(envs, reference={"A"})
    assert reports["dev"].has_removals
    assert not reports["prod"].has_removals


# ---------------------------------------------------------------------------
# reference_from_envs
# ---------------------------------------------------------------------------


def test_reference_from_envs_intersection():
    envs = {
        "dev": {"A": "1", "B": "2", "C": "3"},
        "prod": {"A": "1", "B": "2"},
    }
    ref = reference_from_envs(envs)
    assert ref == {"A", "B"}


def test_reference_from_envs_empty():
    assert reference_from_envs({}) == set()


def test_reference_from_envs_single_env():
    envs = {"dev": {"X": "1", "Y": "2"}}
    ref = reference_from_envs(envs)
    assert ref == {"X", "Y"}
