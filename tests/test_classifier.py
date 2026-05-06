"""Tests for envdiff.classifier."""

import pytest
from envdiff.classifier import (
    ClassifyReport,
    CAT_DATABASE,
    CAT_AUTH,
    CAT_NETWORK,
    CAT_SECRET,
    CAT_FEATURE_FLAG,
    CAT_LOGGING,
    CAT_OTHER,
    classify_key,
    classify_env,
    classify_all,
)


# ---------------------------------------------------------------------------
# classify_key
# ---------------------------------------------------------------------------

def test_classify_key_database():
    assert classify_key("DB_HOST") == CAT_DATABASE
    assert classify_key("POSTGRES_USER") == CAT_DATABASE


def test_classify_key_auth():
    assert classify_key("JWT_SECRET") == CAT_AUTH
    assert classify_key("AUTH_TOKEN") == CAT_AUTH


def test_classify_key_network():
    assert classify_key("APP_HOST") == CAT_NETWORK
    assert classify_key("SERVER_PORT") == CAT_NETWORK
    assert classify_key("API_URL") == CAT_NETWORK


def test_classify_key_secret():
    assert classify_key("SECRET_KEY") == CAT_SECRET
    assert classify_key("APP_PASSWORD") == CAT_SECRET
    assert classify_key("GITHUB_TOKEN") == CAT_SECRET


def test_classify_key_feature_flag():
    assert classify_key("ENABLE_DARK_MODE") == CAT_FEATURE_FLAG
    assert classify_key("FEATURE_BETA") == CAT_FEATURE_FLAG
    assert classify_key("FLAG_ROLLOUT") == CAT_FEATURE_FLAG


def test_classify_key_logging():
    assert classify_key("LOG_LEVEL") == CAT_LOGGING
    assert classify_key("LOGGING_FORMAT") == CAT_LOGGING


def test_classify_key_other():
    assert classify_key("APP_ENV") == CAT_OTHER
    assert classify_key("NODE_ENV") == CAT_OTHER
    assert classify_key("TIMEZONE") == CAT_OTHER


# ---------------------------------------------------------------------------
# classify_env
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "JWT_SECRET": "abc123",
        "APP_HOST": "0.0.0.0",
        "LOG_LEVEL": "debug",
        "ENABLE_BETA": "true",
        "TIMEZONE": "UTC",
    }


def test_classify_env_returns_report(sample_env):
    report = classify_env(sample_env)
    assert isinstance(report, ClassifyReport)


def test_classify_env_groups_database_keys(sample_env):
    report = classify_env(sample_env)
    assert report.has_category(CAT_DATABASE)
    assert "DB_HOST" in report.keys_in(CAT_DATABASE)
    assert "DB_PORT" in report.keys_in(CAT_DATABASE)


def test_classify_env_total_keys(sample_env):
    report = classify_env(sample_env)
    assert report.total_keys() == len(sample_env)


def test_classify_env_other_bucket(sample_env):
    report = classify_env(sample_env)
    assert "TIMEZONE" in report.keys_in(CAT_OTHER)


def test_classify_env_empty():
    report = classify_env({})
    assert report.total_keys() == 0
    assert report.all_categories() == []


def test_all_categories_sorted(sample_env):
    report = classify_env(sample_env)
    cats = report.all_categories()
    assert cats == sorted(cats)


# ---------------------------------------------------------------------------
# classify_all
# ---------------------------------------------------------------------------

def test_classify_all_returns_per_env():
    envs = {
        "dev": {"DB_HOST": "localhost", "APP_ENV": "dev"},
        "prod": {"DB_HOST": "prod-db", "LOG_LEVEL": "warn"},
    }
    result = classify_all(envs)
    assert set(result.keys()) == {"dev", "prod"}
    assert result["dev"].has_category(CAT_DATABASE)
    assert result["prod"].has_category(CAT_LOGGING)
