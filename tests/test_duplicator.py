"""Tests for envdiff.duplicator."""
import pytest
from envdiff.duplicator import (
    DuplicateGroup,
    DuplicateReport,
    find_duplicates,
    find_duplicates_all,
)


@pytest.fixture
def env_with_duplicates():
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",
        "APP_ENV": "production",
        "RAILS_ENV": "production",
        "NODE_ENV": "production",
        "SECRET_KEY": "abc123",
    }


@pytest.fixture
def env_no_duplicates():
    return {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}


def test_find_duplicates_detects_shared_values(env_with_duplicates):
    report = find_duplicates(env_with_duplicates, env_name="dev")
    assert report.has_duplicates


def test_find_duplicates_groups_correctly(env_with_duplicates):
    report = find_duplicates(env_with_duplicates, env_name="dev")
    values = {g.value for g in report.groups}
    assert "localhost" in values
    assert "production" in values


def test_find_duplicates_group_key_count(env_with_duplicates):
    report = find_duplicates(env_with_duplicates, env_name="dev")
    prod_group = next(g for g in report.groups if g.value == "production")
    assert prod_group.count == 3
    assert "APP_ENV" in prod_group.keys
    assert "NODE_ENV" in prod_group.keys
    assert "RAILS_ENV" in prod_group.keys


def test_find_duplicates_unique_value_excluded(env_with_duplicates):
    report = find_duplicates(env_with_duplicates, env_name="dev")
    values = {g.value for g in report.groups}
    assert "abc123" not in values


def test_find_duplicates_no_duplicates(env_no_duplicates):
    report = find_duplicates(env_no_duplicates, env_name="prod")
    assert not report.has_duplicates
    assert report.groups == []


def test_find_duplicates_total_duplicate_keys(env_with_duplicates):
    report = find_duplicates(env_with_duplicates, env_name="dev")
    # localhost (2) + production (3) = 5
    assert report.total_duplicate_keys == 5


def test_find_duplicates_empty_env():
    report = find_duplicates({}, env_name="empty")
    assert not report.has_duplicates
    assert report.total_duplicate_keys == 0


def test_find_duplicates_all_returns_per_env():
    envs = {
        "dev": {"A": "x", "B": "x"},
        "prod": {"A": "y", "B": "z"},
    }
    results = find_duplicates_all(envs)
    assert "dev" in results
    assert "prod" in results
    assert results["dev"].has_duplicates
    assert not results["prod"].has_duplicates


def test_find_duplicates_env_name_stored():
    report = find_duplicates({"K": "v"}, env_name="staging")
    assert report.env_name == "staging"


def test_duplicate_group_keys_sorted():
    env = {"Z_KEY": "same", "A_KEY": "same", "M_KEY": "same"}
    report = find_duplicates(env)
    assert report.groups[0].keys == ["A_KEY", "M_KEY", "Z_KEY"]
