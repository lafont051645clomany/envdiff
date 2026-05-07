"""Tests for envdiff.stacker."""
from __future__ import annotations

import pytest

from envdiff.stacker import LayerEntry, StackReport, stack_envs


@pytest.fixture
def base_env() -> dict:
    return {"APP_NAME": "myapp", "DEBUG": "false", "DB_HOST": "localhost"}


@pytest.fixture
def override_env() -> dict:
    return {"DEBUG": "true", "DB_HOST": "prod-db.example.com", "SECRET_KEY": "s3cr3t"}


@pytest.fixture
def report(base_env, override_env) -> StackReport:
    return stack_envs([("base", base_env), ("prod", override_env)])


def test_layers_recorded(report):
    assert report.layers == ["base", "prod"]


def test_all_keys_includes_both_sources(report):
    assert "APP_NAME" in report.all_keys
    assert "SECRET_KEY" in report.all_keys
    assert "DEBUG" in report.all_keys


def test_effective_value_uses_last_layer(report):
    assert report.effective_value("DEBUG") == "true"
    assert report.effective_value("DB_HOST") == "prod-db.example.com"


def test_effective_value_only_in_base(report):
    assert report.effective_value("APP_NAME") == "myapp"


def test_effective_source_correct(report):
    assert report.effective_source("APP_NAME") == "base"
    assert report.effective_source("SECRET_KEY") == "prod"
    assert report.effective_source("DEBUG") == "prod"


def test_overridden_keys_detected(report):
    assert "DEBUG" in report.overridden_keys
    assert "DB_HOST" in report.overridden_keys


def test_app_name_not_overridden(report):
    assert "APP_NAME" not in report.overridden_keys


def test_missing_key_in_layer_is_none(report):
    entries = report.entries["SECRET_KEY"]
    base_entry = next(e for e in entries if e.source == "base")
    assert base_entry.value is None


def test_layer_entry_is_overridden_flag():
    entry = LayerEntry(key="X", value="old", source="base", overridden_by="prod")
    assert entry.is_overridden is True


def test_layer_entry_not_overridden_flag():
    entry = LayerEntry(key="X", value="new", source="prod")
    assert entry.is_overridden is False


def test_single_env_no_overrides():
    report = stack_envs([("only", {"KEY": "val"})])
    assert report.overridden_keys == []
    assert report.effective_value("KEY") == "val"


def test_empty_envs_empty_report():
    report = stack_envs([("a", {}), ("b", {})])
    assert report.all_keys == []
    assert report.overridden_keys == []


def test_three_layer_precedence():
    report = stack_envs([
        ("a", {"X": "1"}),
        ("b", {"X": "2"}),
        ("c", {"X": "3"}),
    ])
    assert report.effective_value("X") == "3"
    assert report.effective_source("X") == "c"
    assert "X" in report.overridden_keys
