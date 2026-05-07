"""Tests for envdiff.tagger."""
import pytest
from envdiff.tagger import (
    TagReport,
    _auto_tag_key,
    tag_env,
    tag_all,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "JWT_SECRET": "abc123",
        "APP_PORT": "8080",
        "LOG_LEVEL": "info",
        "FEATURE_DARK_MODE": "true",
        "APP_NAME": "myapp",
    }


def test_auto_tag_key_database():
    assert _auto_tag_key("DB_HOST", None) is None  # rules=None falls back gracefully


def test_auto_tag_key_with_rules():
    from envdiff.tagger import _DEFAULT_RULES
    assert _auto_tag_key("DB_HOST", _DEFAULT_RULES) == "database"
    assert _auto_tag_key("JWT_SECRET", _DEFAULT_RULES) == "auth"
    assert _auto_tag_key("APP_PORT", _DEFAULT_RULES) == "network"
    assert _auto_tag_key("LOG_LEVEL", _DEFAULT_RULES) == "logging"
    assert _auto_tag_key("FEATURE_X", _DEFAULT_RULES) == "feature"
    assert _auto_tag_key("APP_NAME", _DEFAULT_RULES) is None


def test_tag_env_returns_tag_report(sample_env):
    report = tag_env(sample_env)
    assert isinstance(report, TagReport)


def test_tag_env_database_keys(sample_env):
    report = tag_env(sample_env)
    assert report.has_tag("database")
    assert "DB_HOST" in report.keys_for("database")


def test_tag_env_auth_keys(sample_env):
    report = tag_env(sample_env)
    assert report.has_tag("auth")
    db_pass_or_jwt = report.keys_for("auth")
    assert any(k in db_pass_or_jwt for k in ["DB_PASSWORD", "JWT_SECRET"])


def test_tag_env_untagged_keys(sample_env):
    report = tag_env(sample_env)
    assert "APP_NAME" in report.untagged


def test_tag_env_all_tags_sorted(sample_env):
    report = tag_env(sample_env)
    tags = report.all_tags()
    assert tags == sorted(tags)


def test_tag_env_total_tagged(sample_env):
    report = tag_env(sample_env)
    assert report.total_tagged() > 0
    assert report.total_tagged() + len(report.untagged) == len(sample_env)


def test_tag_env_custom_tags_override(sample_env):
    custom = {"custom": ["APP_NAME"]}
    report = tag_env(sample_env, custom_tags=custom)
    assert "APP_NAME" not in report.untagged
    assert "APP_NAME" in report.keys_for("custom")


def test_tag_env_empty_env():
    report = tag_env({})
    assert report.total_tagged() == 0
    assert report.untagged == []


def test_tag_all_returns_per_env():
    envs = {
        "dev": {"DB_HOST": "localhost", "APP_NAME": "app"},
        "prod": {"DB_HOST": "prod-db", "LOG_LEVEL": "warn"},
    }
    reports = tag_all(envs)
    assert set(reports.keys()) == {"dev", "prod"}
    assert reports["dev"].has_tag("database")
    assert reports["prod"].has_tag("logging")


def test_keys_for_missing_tag(sample_env):
    report = tag_env(sample_env)
    assert report.keys_for("nonexistent") == []
    assert not report.has_tag("nonexistent")
