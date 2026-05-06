"""Tests for envdiff.normalizer."""

import pytest
from envdiff.normalizer import (
    normalize_value,
    normalize_env,
    normalize_all,
    extract_normalized,
    NormalizeResult,
)


# --- normalize_value ---

@pytest.mark.parametrize("raw,expected", [
    ("true", "true"),
    ("True", "true"),
    ("TRUE", "true"),
    ("yes", "true"),
    ("1", "true"),
    ("on", "true"),
    ("false", "false"),
    ("False", "false"),
    ("no", "false"),
    ("0", "false"),
    ("off", "false"),
])
def test_normalize_value_booleans(raw, expected):
    assert normalize_value(raw) == expected


def test_normalize_value_strips_whitespace():
    assert normalize_value("  hello  ") == "hello"


def test_normalize_value_empty_string():
    assert normalize_value("") == ""
    assert normalize_value("   ") == ""


def test_normalize_value_plain_string_unchanged():
    assert normalize_value("my-secret-value") == "my-secret-value"


# --- normalize_env ---

def test_normalize_env_detects_changes():
    env = {"DEBUG": "True", "PORT": "8080", "ACTIVE": "yes"}
    result = normalize_env(env)
    assert result.normalized["DEBUG"] == "true"
    assert result.normalized["ACTIVE"] == "true"
    assert result.normalized["PORT"] == "8080"
    assert "DEBUG" in result.changes
    assert "ACTIVE" in result.changes
    assert "PORT" not in result.changes


def test_normalize_env_no_changes():
    env = {"NAME": "alice", "HOST": "localhost"}
    result = normalize_env(env)
    assert not result.has_changes
    assert result.change_count == 0


def test_normalize_env_preserves_original():
    env = {"FLAG": "YES"}
    result = normalize_env(env)
    assert result.original["FLAG"] == "YES"
    assert result.normalized["FLAG"] == "true"


def test_normalize_env_change_tuple_format():
    env = {"ENABLED": "On"}
    result = normalize_env(env)
    before, after = result.changes["ENABLED"]
    assert before == "On"
    assert after == "true"


# --- normalize_all ---

def test_normalize_all_returns_all_envs():
    envs = {
        "dev": {"DEBUG": "True"},
        "prod": {"DEBUG": "false"},
    }
    results = normalize_all(envs)
    assert set(results.keys()) == {"dev", "prod"}
    assert isinstance(results["dev"], NormalizeResult)


def test_normalize_all_empty():
    assert normalize_all({}) == {}


# --- extract_normalized ---

def test_extract_normalized_returns_dict():
    env = {"X": "YES", "Y": "hello"}
    result = normalize_env(env)
    extracted = extract_normalized(result)
    assert extracted == {"X": "true", "Y": "hello"}
