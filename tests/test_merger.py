"""Tests for envdiff.merger."""

import pytest

from envdiff.merger import collect_all_keys, merge_envs, merge_with_sources


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def env_base():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}


@pytest.fixture
def env_override():
    return {"DB_HOST": "prod.db", "SECRET_KEY": "abc123"}


# ---------------------------------------------------------------------------
# merge_envs
# ---------------------------------------------------------------------------

def test_merge_later_overrides_earlier(env_base, env_override):
    merged = merge_envs([env_base, env_override])
    assert merged["DB_HOST"] == "prod.db"


def test_merge_keys_from_all_envs(env_base, env_override):
    merged = merge_envs([env_base, env_override])
    assert "DB_PORT" in merged
    assert "SECRET_KEY" in merged
    assert "APP_ENV" in merged


def test_merge_single_env_unchanged(env_base):
    merged = merge_envs([env_base])
    assert merged == env_base


def test_merge_empty_list_returns_empty():
    assert merge_envs([]) == {}


def test_merge_protected_key_not_overridden(env_base, env_override):
    merged = merge_envs([env_base, env_override], protected_keys={"DB_HOST"})
    assert merged["DB_HOST"] == "localhost"


def test_merge_non_protected_key_still_overridden(env_base, env_override):
    merged = merge_envs([env_base, env_override], protected_keys={"DB_HOST"})
    # SECRET_KEY comes from env_override and should be present
    assert merged["SECRET_KEY"] == "abc123"


# ---------------------------------------------------------------------------
# merge_with_sources
# ---------------------------------------------------------------------------

def test_merge_with_sources_records_winning_label(env_base, env_override):
    result = merge_with_sources([env_base, env_override], labels=["base", "override"])
    assert result["DB_HOST"]["source"] == "override"
    assert result["DB_PORT"]["source"] == "base"


def test_merge_with_sources_default_labels(env_base, env_override):
    result = merge_with_sources([env_base, env_override])
    assert result["SECRET_KEY"]["source"] == "env1"


def test_merge_with_sources_label_length_mismatch(env_base):
    with pytest.raises(ValueError, match="labels length"):
        merge_with_sources([env_base], labels=["a", "b"])


def test_merge_with_sources_value_correct(env_base, env_override):
    result = merge_with_sources([env_base, env_override], labels=["base", "override"])
    assert result["DB_HOST"]["value"] == "prod.db"


# ---------------------------------------------------------------------------
# collect_all_keys
# ---------------------------------------------------------------------------

def test_collect_all_keys_union(env_base, env_override):
    keys = collect_all_keys([env_base, env_override])
    assert keys == {"DB_HOST", "DB_PORT", "APP_ENV", "SECRET_KEY"}


def test_collect_all_keys_empty():
    assert collect_all_keys([]) == set()
