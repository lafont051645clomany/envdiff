"""Tests for envdiff.auditor."""

import pytest

from envdiff.auditor import AuditIssue, AuditResult, audit_all, audit_env


@pytest.fixture
def clean_env():
    return {"APP_NAME": "myapp", "PORT": "8080", "DEBUG": "false"}


@pytest.fixture
def problematic_env():
    return {
        "SECRET_KEY": "",           # empty secret  -> error
        "DB_PASSWORD": "changeme",  # placeholder   -> warning
        "APP_NAME": "myapp",        # fine
        "BLOB": "x" * 200,          # long non-secret -> info
    }


# ---------------------------------------------------------------------------
# audit_env
# ---------------------------------------------------------------------------

def test_clean_env_no_issues(clean_env):
    result = audit_env(clean_env, "dev")
    assert not result.has_issues
    assert result.errors == []
    assert result.warnings == []


def test_empty_secret_is_error(problematic_env):
    result = audit_env(problematic_env, "prod")
    errors = result.errors
    assert any(i.key == "SECRET_KEY" for i in errors)


def test_placeholder_value_is_warning(problematic_env):
    result = audit_env(problematic_env, "prod")
    warnings = result.warnings
    assert any(i.key == "DB_PASSWORD" for i in warnings)


def test_long_non_secret_is_info(problematic_env):
    result = audit_env(problematic_env, "prod")
    infos = [i for i in result.issues if i.severity == "info"]
    assert any(i.key == "BLOB" for i in infos)


def test_env_name_stored_in_result(clean_env):
    result = audit_env(clean_env, "staging")
    assert result.env_name == "staging"


def test_has_issues_false_when_clean(clean_env):
    result = audit_env(clean_env)
    assert result.has_issues is False


def test_has_issues_true_when_problems(problematic_env):
    result = audit_env(problematic_env)
    assert result.has_issues is True


def test_placeholder_variants_detected():
    env = {"API_KEY": "todo", "DB_URL": "xxx", "HOST": "localhost"}
    result = audit_env(env)
    warning_keys = {i.key for i in result.warnings}
    assert "API_KEY" in warning_keys
    assert "DB_URL" in warning_keys
    assert "HOST" not in warning_keys


# ---------------------------------------------------------------------------
# audit_all
# ---------------------------------------------------------------------------

def test_audit_all_returns_all_names(clean_env, problematic_env):
    results = audit_all({"dev": clean_env, "prod": problematic_env})
    assert set(results.keys()) == {"dev", "prod"}


def test_audit_all_dev_clean_prod_issues(clean_env, problematic_env):
    results = audit_all({"dev": clean_env, "prod": problematic_env})
    assert not results["dev"].has_issues
    assert results["prod"].has_issues


def test_audit_all_empty_input():
    results = audit_all({})
    assert results == {}
