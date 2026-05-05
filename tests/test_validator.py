"""Tests for envdiff.validator module."""

import pytest
from envdiff.validator import (
    ValidationError,
    ValidationResult,
    validate_env,
    format_validation_report,
    BUILTIN_RULES,
)


@pytest.fixture
def sample_envs():
    return {
        "dev": {
            "DATABASE_URL": "postgres://localhost/dev",
            "PORT": "8080",
            "DEBUG": "true",
            "ADMIN_EMAIL": "admin@example.com",
        },
        "prod": {
            "DATABASE_URL": "https://prod.db.example.com",
            "PORT": "not_a_number",
            "DEBUG": "yes",
            "ADMIN_EMAIL": "not-an-email",
        },
    }


def test_valid_envs_no_errors(sample_envs):
    rules = {"PORT": "integer", "DEBUG": "boolean"}
    result = validate_env({"dev": sample_envs["dev"]}, rules)
    assert result.is_valid
    assert result.errors == []


def test_invalid_integer_flagged(sample_envs):
    rules = {"PORT": "integer"}
    result = validate_env({"prod": sample_envs["prod"]}, rules)
    assert not result.is_valid
    assert len(result.errors) == 1
    err = result.errors[0]
    assert err.key == "PORT"
    assert err.env_name == "prod"
    assert err.rule == "integer"


def test_invalid_email_flagged(sample_envs):
    rules = {"ADMIN_EMAIL": "email"}
    result = validate_env({"prod": sample_envs["prod"]}, rules)
    assert not result.is_valid
    assert result.errors[0].key == "ADMIN_EMAIL"


def test_missing_key_is_skipped(sample_envs):
    """Keys not present in an env should not generate errors."""
    rules = {"NONEXISTENT_KEY": "non_empty"}
    result = validate_env(sample_envs, rules)
    assert result.is_valid


def test_custom_regex_rule(sample_envs):
    rules = {"PORT": r"^\d{4}$"}
    result = validate_env({"dev": sample_envs["dev"]}, rules)
    assert result.is_valid


def test_custom_regex_rule_fails():
    envs = {"staging": {"API_KEY": "short"}}
    rules = {"API_KEY": r"^.{16,}$"}
    result = validate_env(envs, rules)
    assert not result.is_valid
    assert result.errors[0].key == "API_KEY"


def test_multiple_envs_multiple_errors(sample_envs):
    rules = {"PORT": "integer", "ADMIN_EMAIL": "email"}
    result = validate_env(sample_envs, rules)
    # dev passes both, prod fails both
    assert len(result.errors) == 2
    error_envs = {e.env_name for e in result.errors}
    assert error_envs == {"prod"}


def test_format_report_valid():
    result = ValidationResult()
    assert format_validation_report(result) == "All values passed validation."


def test_format_report_with_errors():
    result = ValidationResult()
    result.add_error(
        ValidationError(
            key="PORT",
            env_name="prod",
            value="abc",
            rule="integer",
            message="[prod] 'PORT' value 'abc' does not match rule 'integer'",
        )
    )
    report = format_validation_report(result)
    assert "1 error" in report
    assert "PORT" in report


def test_builtin_rules_exist():
    for name in ("url", "integer", "boolean", "email", "non_empty"):
        assert name in BUILTIN_RULES
