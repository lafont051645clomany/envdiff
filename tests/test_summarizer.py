"""Tests for envdiff.summarizer."""

import pytest

from envdiff.summarizer import EnvSummary, summarize_env, summarize_all


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret123",
        "API_KEY": "abc",
        "DEBUG": "true",
        "EMPTY_VAR": "",
    }


def test_summarize_total_keys(sample_env):
    result = summarize_env("dev", sample_env)
    assert result.total_keys == 5


def test_summarize_label(sample_env):
    result = summarize_env("staging", sample_env)
    assert result.label == "staging"


def test_summarize_empty_keys(sample_env):
    result = summarize_env("dev", sample_env)
    assert "EMPTY_VAR" in result.empty_keys
    assert result.empty_count == 1


def test_summarize_secret_keys(sample_env):
    result = summarize_env("dev", sample_env)
    assert "DB_PASSWORD" in result.secret_keys
    assert "API_KEY" in result.secret_keys


def test_summarize_plain_count(sample_env):
    result = summarize_env("dev", sample_env)
    assert result.plain_count == result.total_keys - result.secret_count


def test_summarize_categories_populated(sample_env):
    result = summarize_env("dev", sample_env)
    assert isinstance(result.categories, dict)
    assert len(result.categories) > 0


def test_summarize_empty_env():
    result = summarize_env("empty", {})
    assert result.total_keys == 0
    assert result.empty_count == 0
    assert result.secret_count == 0
    assert result.plain_count == 0


def test_summarize_all_returns_list(sample_env):
    named = {"dev": sample_env, "prod": {"DB_HOST": "prod-host"}}
    results = summarize_all(named)
    assert len(results) == 2
    labels = [r.label for r in results]
    assert "dev" in labels
    assert "prod" in labels


def test_summarize_all_empty():
    results = summarize_all({})
    assert results == []
