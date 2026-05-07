"""Tests for envdiff.pinner."""

from __future__ import annotations

import pytest

from envdiff.pinner import DriftEntry, detect_drift, pin_env


@pytest.fixture
def base_env():
    return {
        "APP_NAME": "myapp",
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "supersecret",
        "DEBUG": "true",
    }


def test_pin_env_total_keys(base_env):
    report = pin_env(base_env, label="dev")
    assert report.total == 4


def test_pin_env_label(base_env):
    report = pin_env(base_env, label="staging")
    assert report.label == "staging"


def test_pin_env_secret_count(base_env):
    report = pin_env(base_env)
    assert report.secret_count >= 1  # SECRET_KEY should be detected


def test_pin_env_get_entry(base_env):
    report = pin_env(base_env)
    entry = report.get("APP_NAME")
    assert entry is not None
    assert entry.value == "myapp"


def test_pin_env_secret_display_value(base_env):
    report = pin_env(base_env)
    entry = report.get("SECRET_KEY")
    assert entry is not None
    assert entry.display_value == "***"


def test_pin_env_plain_display_value(base_env):
    report = pin_env(base_env)
    entry = report.get("APP_NAME")
    assert entry.display_value == "myapp"


def test_no_drift_identical(base_env):
    pin = pin_env(base_env, label="dev")
    drift = detect_drift(pin, dict(base_env))
    assert not drift.has_drift
    assert drift.count == 0


def test_drift_detects_changed_key(base_env):
    pin = pin_env(base_env)
    current = dict(base_env)
    current["DEBUG"] = "false"
    drift = detect_drift(pin, current)
    assert drift.has_drift
    keys = [e.key for e in drift.drifted]
    assert "DEBUG" in keys


def test_drift_status_changed(base_env):
    pin = pin_env(base_env)
    current = dict(base_env)
    current["APP_NAME"] = "newapp"
    drift = detect_drift(pin, current)
    entry = next(e for e in drift.drifted if e.key == "APP_NAME")
    assert entry.status == "changed"
    assert entry.pinned_value == "myapp"
    assert entry.current_value == "newapp"


def test_drift_detects_removed_key(base_env):
    pin = pin_env(base_env)
    current = {k: v for k, v in base_env.items() if k != "DEBUG"}
    drift = detect_drift(pin, current)
    removed = [e for e in drift.drifted if e.status == "removed"]
    assert any(e.key == "DEBUG" for e in removed)


def test_drift_detects_added_key(base_env):
    pin = pin_env(base_env)
    current = dict(base_env)
    current["NEW_VAR"] = "hello"
    drift = detect_drift(pin, current)
    added = [e for e in drift.drifted if e.status == "added"]
    assert any(e.key == "NEW_VAR" for e in added)


def test_drift_count_matches_changes(base_env):
    pin = pin_env(base_env)
    current = dict(base_env)
    current["DEBUG"] = "false"
    del current["APP_NAME"]
    current["EXTRA"] = "1"
    drift = detect_drift(pin, current)
    assert drift.count == 3
