"""Additional tests verifying category classification in EnvSummary."""

import pytest

from envdiff.summarizer import summarize_env


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AUTH_TOKEN": "tok",
        "ENABLE_FEATURE_X": "true",
        "SMTP_HOST": "mail.example.com",
        "SECRET_KEY": "s3cr3t",
    }


def test_database_category_present(mixed_env):
    result = summarize_env("test", mixed_env)
    db_keys = result.categories.get("database", [])
    assert any("DB_" in k for k in db_keys)


def test_auth_category_present(mixed_env):
    result = summarize_env("test", mixed_env)
    auth_keys = result.categories.get("auth", [])
    assert any("AUTH" in k or "SECRET" in k for k in auth_keys)


def test_all_keys_accounted_in_categories(mixed_env):
    result = summarize_env("test", mixed_env)
    all_categorized = [
        k for keys in result.categories.values() for k in keys
    ]
    assert sorted(all_categorized) == sorted(mixed_env.keys())


def test_no_duplicate_keys_across_categories(mixed_env):
    result = summarize_env("test", mixed_env)
    all_categorized = [
        k for keys in result.categories.values() for k in keys
    ]
    assert len(all_categorized) == len(set(all_categorized))


def test_single_key_env_has_one_category():
    result = summarize_env("solo", {"DB_NAME": "mydb"})
    total = sum(len(v) for v in result.categories.values())
    assert total == 1
