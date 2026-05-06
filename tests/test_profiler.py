"""Tests for envdiff.profiler."""

import pytest

from envdiff.profiler import EnvProfile, compare_profiles, profile_all, profile_env


@pytest.fixture()
def simple_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "DB_HOST": "localhost",
        "API_SECRET_KEY": "abc123",
        "DEBUG": "",
    }


def test_profile_total_keys(simple_env):
    prof = profile_env("dev", simple_env)
    assert prof.total_keys == 5


def test_profile_empty_values(simple_env):
    prof = profile_env("dev", simple_env)
    assert prof.empty_values == 1


def test_profile_secret_keys(simple_env):
    prof = profile_env("dev", simple_env)
    # DB_PASSWORD and API_SECRET_KEY should be detected as secrets
    assert prof.secret_keys >= 2


def test_profile_plain_keys_consistent(simple_env):
    prof = profile_env("dev", simple_env)
    assert prof.plain_keys == prof.total_keys - prof.secret_keys


def test_secret_ratio_range(simple_env):
    prof = profile_env("dev", simple_env)
    assert 0.0 <= prof.secret_ratio <= 1.0


def test_secret_ratio_empty_env():
    prof = profile_env("empty", {})
    assert prof.secret_ratio == 0.0


def test_prefix_groups_populated(simple_env):
    prof = profile_env("dev", simple_env)
    # DB_PASSWORD and DB_HOST share the DB_ prefix
    assert "DB" in prof.prefix_groups
    assert len(prof.prefix_groups["DB"]) == 2


def test_summary_contains_name(simple_env):
    prof = profile_env("staging", simple_env)
    assert "staging" in prof.summary()


def test_profile_all_returns_all_names():
    envs = {
        "dev": {"KEY": "val"},
        "prod": {"KEY": "val", "SECRET_TOKEN": "x"},
    }
    profiles = profile_all(envs)
    assert set(profiles.keys()) == {"dev", "prod"}


def test_compare_profiles_most_and_fewest():
    envs = {
        "dev": {"A": "1"},
        "prod": {"A": "1", "B": "2", "C": "3"},
    }
    profiles = profile_all(envs)
    result = compare_profiles(profiles)
    assert result["most_keys"] == "prod"
    assert result["fewest_keys"] == "dev"


def test_compare_profiles_empty():
    assert compare_profiles({}) == {}
