"""Tests for envdiff.tracer."""
import pytest

from envdiff.tracer import (
    KeyTrace,
    TraceReport,
    trace_all,
    trace_key,
)


@pytest.fixture()
def named_envs():
    return {
        "dev": {"APP_NAME": "myapp", "DEBUG": "true", "DB_HOST": "localhost"},
        "staging": {"APP_NAME": "myapp", "DEBUG": "false", "DB_HOST": "staging-db"},
        "prod": {"APP_NAME": "myapp", "DB_HOST": "prod-db", "SECRET_KEY": "s3cr3t"},
    }


# --- KeyTrace ---

def test_env_count_counts_defined_values():
    t = KeyTrace(key="FOO", origins={"dev": "bar", "prod": None})
    assert t.env_count == 1


def test_is_consistent_same_values():
    t = KeyTrace(key="APP", origins={"dev": "myapp", "prod": "myapp"})
    assert t.is_consistent is True


def test_is_consistent_different_values():
    t = KeyTrace(key="DEBUG", origins={"dev": "true", "prod": "false"})
    assert t.is_consistent is False


def test_is_consistent_with_missing_env():
    # Key present in one env only — still consistent (only one value)
    t = KeyTrace(key="SECRET", origins={"dev": None, "prod": "abc"})
    assert t.is_consistent is True


def test_unique_values_excludes_none():
    t = KeyTrace(key="X", origins={"dev": "1", "prod": None, "staging": "2"})
    assert set(t.unique_values) == {"1", "2"}


# --- trace_key ---

def test_trace_key_captures_all_envs(named_envs):
    result = trace_key("DEBUG", named_envs)
    assert result.key == "DEBUG"
    assert result.origins["dev"] == "true"
    assert result.origins["staging"] == "false"
    assert result.origins["prod"] is None  # prod has no DEBUG


def test_trace_key_missing_everywhere():
    result = trace_key("NONEXISTENT", {"dev": {}, "prod": {}})
    assert result.env_count == 0
    assert result.is_consistent is True  # no values → vacuously consistent


# --- trace_all ---

def test_trace_all_includes_all_keys(named_envs):
    report = trace_all(named_envs)
    assert "APP_NAME" in report.traces
    assert "DEBUG" in report.traces
    assert "SECRET_KEY" in report.traces


def test_trace_all_env_names(named_envs):
    report = trace_all(named_envs)
    assert set(report.env_names) == {"dev", "staging", "prod"}


def test_trace_all_total_keys(named_envs):
    report = trace_all(named_envs)
    # APP_NAME, DEBUG, DB_HOST, SECRET_KEY
    assert report.total_keys == 4


def test_trace_all_inconsistent_keys(named_envs):
    report = trace_all(named_envs)
    inconsistent = report.inconsistent_keys
    assert "DEBUG" in inconsistent
    assert "DB_HOST" in inconsistent
    assert "APP_NAME" not in inconsistent


def test_trace_all_empty_envs():
    report = trace_all({"a": {}, "b": {}})
    assert report.total_keys == 0
    assert report.inconsistent_keys == []
