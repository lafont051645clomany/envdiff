"""Tests for envdiff.redactor."""

from __future__ import annotations

import pytest

from envdiff.redactor import (
    DEFAULT_REDACT_PLACEHOLDER,
    RedactResult,
    redact_all,
    redact_env,
)


@pytest.fixture()
def sample_env() -> dict:
    return {
        "APP_NAME": "myapp",
        "DATABASE_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "DEBUG": "true",
        "SECRET_TOKEN": "tok_xyz",
    }


def test_redact_env_returns_redact_result(sample_env):
    result = redact_env(sample_env)
    assert isinstance(result, RedactResult)


def test_non_secret_keys_unchanged(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["DEBUG"] == "true"


def test_secret_keys_replaced(sample_env):
    result = redact_env(sample_env)
    assert result.redacted["DATABASE_PASSWORD"] == DEFAULT_REDACT_PLACEHOLDER
    assert result.redacted["API_KEY"] == DEFAULT_REDACT_PLACEHOLDER
    assert result.redacted["SECRET_TOKEN"] == DEFAULT_REDACT_PLACEHOLDER


def test_redact_count_matches(sample_env):
    result = redact_env(sample_env)
    assert result.redact_count == 3


def test_has_redactions_true(sample_env):
    result = redact_env(sample_env)
    assert result.has_redactions is True


def test_has_redactions_false():
    result = redact_env({"APP_NAME": "myapp", "DEBUG": "true"})
    assert result.has_redactions is False


def test_custom_placeholder(sample_env):
    result = redact_env(sample_env, placeholder="***")
    assert result.redacted["API_KEY"] == "***"


def test_extra_keys_are_redacted(sample_env):
    result = redact_env(sample_env, extra_keys=["APP_NAME"])
    assert result.redacted["APP_NAME"] == DEFAULT_REDACT_PLACEHOLDER
    assert "APP_NAME" in result.redacted_keys


def test_original_env_preserved(sample_env):
    result = redact_env(sample_env)
    assert result.original["DATABASE_PASSWORD"] == "s3cr3t"


def test_redacted_keys_sorted(sample_env):
    result = redact_env(sample_env)
    assert result.redacted_keys == sorted(result.redacted_keys)


def test_redact_all_applies_to_all_envs(sample_env):
    envs = {"dev": sample_env, "prod": {"API_KEY": "prod_key", "HOST": "localhost"}}
    results = redact_all(envs)
    assert results["dev"].redacted["API_KEY"] == DEFAULT_REDACT_PLACEHOLDER
    assert results["prod"].redacted["API_KEY"] == DEFAULT_REDACT_PLACEHOLDER
    assert results["prod"].redacted["HOST"] == "localhost"


def test_redact_all_returns_dict_of_redact_results(sample_env):
    results = redact_all({"dev": sample_env})
    assert all(isinstance(v, RedactResult) for v in results.values())
