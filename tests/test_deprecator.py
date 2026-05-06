"""Tests for envdiff.deprecator."""

import pytest

from envdiff.deprecator import (
    DEFAULT_DEPRECATED,
    DeprecationReport,
    DeprecationWarning_,
    find_deprecated,
    find_deprecated_all,
)


@pytest.fixture()
def env_with_deprecated():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "APP_NAME": "myapp",
        "LEGACY_MODE": "true",
        "PORT": "8080",
    }


@pytest.fixture()
def clean_env():
    return {"APP_NAME": "myapp", "PORT": "8080", "LOG_LEVEL": "info"}


def test_find_deprecated_detects_known_keys(env_with_deprecated):
    report = find_deprecated(env_with_deprecated)
    assert report.has_warnings
    assert "DATABASE_URL" in report.deprecated_keys
    assert "LEGACY_MODE" in report.deprecated_keys


def test_find_deprecated_ignores_clean_keys(clean_env):
    report = find_deprecated(clean_env)
    assert not report.has_warnings
    assert report.deprecated_keys == []


def test_deprecation_warning_label_with_suggestion():
    w = DeprecationWarning_(key="DATABASE_URL", suggestion="DB_URL")
    assert "DATABASE_URL" in w.label
    assert "DB_URL" in w.label


def test_deprecation_warning_label_no_suggestion():
    w = DeprecationWarning_(key="LEGACY_MODE", suggestion=None)
    assert "LEGACY_MODE" in w.label
    assert "no replacement" in w.label


def test_custom_deprecated_map():
    env = {"MY_OLD_KEY": "value", "NEW_KEY": "value"}
    custom = {"MY_OLD_KEY": "MY_NEW_KEY"}
    report = find_deprecated(env, deprecated_map=custom)
    assert report.has_warnings
    assert "MY_OLD_KEY" in report.deprecated_keys
    assert "NEW_KEY" not in report.deprecated_keys


def test_to_dict_structure(env_with_deprecated):
    report = find_deprecated(env_with_deprecated)
    d = report.to_dict()
    assert "deprecated_count" in d
    assert "warnings" in d
    assert d["deprecated_count"] == len(report.warnings)
    for entry in d["warnings"]:
        assert "key" in entry
        assert "suggestion" in entry


def test_find_deprecated_all_returns_per_env():
    envs = {
        "dev": {"DATABASE_URL": "postgres://dev/db", "PORT": "5432"},
        "prod": {"PORT": "5432", "LOG_LEVEL": "warn"},
    }
    reports = find_deprecated_all(envs)
    assert "dev" in reports
    assert "prod" in reports
    assert reports["dev"].has_warnings
    assert not reports["prod"].has_warnings


def test_empty_env_no_warnings():
    report = find_deprecated({})
    assert not report.has_warnings
    assert report.deprecated_keys == []


def test_default_deprecated_map_is_dict():
    assert isinstance(DEFAULT_DEPRECATED, dict)
    assert len(DEFAULT_DEPRECATED) > 0
