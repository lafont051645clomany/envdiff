"""Tests for envdiff.masker module."""

import pytest
from envdiff.masker import (
    is_secret_key,
    mask_value,
    mask_env,
    get_secret_keys,
    MASK_VALUE,
    DEFAULT_SECRET_PATTERNS,
)


@pytest.mark.parametrize(
    "key,expected",
    [
        ("DB_PASSWORD", True),
        ("API_KEY", True),
        ("SECRET_KEY", True),
        ("AUTH_TOKEN", True),
        ("PRIVATE_KEY", True),
        ("APP_TOKEN", True),
        ("DB_HOST", False),
        ("PORT", False),
        ("DEBUG", False),
        ("DATABASE_URL", False),
    ],
)
def test_is_secret_key(key, expected):
    assert is_secret_key(key) == expected


def test_is_secret_key_custom_pattern():
    import re
    patterns = [re.compile(r".*CUSTOM.*", re.IGNORECASE)]
    assert is_secret_key("MY_CUSTOM_VAR", patterns) is True
    assert is_secret_key("DB_PASSWORD", patterns) is False


def test_mask_value_default():
    assert mask_value("super_secret_123") == MASK_VALUE


def test_mask_value_custom_mask():
    assert mask_value("super_secret_123", mask="[REDACTED]") == "[REDACTED]"


def test_mask_env_masks_secrets():
    env = {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123",
        "PORT": "5432",
    }
    masked = mask_env(env)
    assert masked["DB_HOST"] == "localhost"
    assert masked["PORT"] == "5432"
    assert masked["DB_PASSWORD"] == MASK_VALUE
    assert masked["API_KEY"] == MASK_VALUE


def test_mask_env_does_not_mutate_original():
    env = {"SECRET_KEY": "topsecret", "APP_NAME": "myapp"}
    masked = mask_env(env)
    assert env["SECRET_KEY"] == "topsecret"
    assert masked["SECRET_KEY"] == MASK_VALUE


def test_mask_env_custom_mask_string():
    env = {"DB_PASSWORD": "pass123", "HOST": "example.com"}
    masked = mask_env(env, mask="<hidden>")
    assert masked["DB_PASSWORD"] == "<hidden>"
    assert masked["HOST"] == "example.com"


def test_get_secret_keys():
    env = {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "API_KEY": "key",
        "DEBUG": "true",
    }
    secrets = get_secret_keys(env)
    assert secrets == {"DB_PASSWORD", "API_KEY"}


def test_get_secret_keys_empty_env():
    assert get_secret_keys({}) == set()
