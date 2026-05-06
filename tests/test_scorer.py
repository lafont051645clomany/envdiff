"""Tests for envdiff.scorer."""

import pytest

from envdiff.auditor import AuditIssue, AuditResult
from envdiff.linter import LintIssue, LintResult
from envdiff.profiler import EnvProfile
from envdiff.scorer import (
    HealthScore,
    _grade,
    compute_health_score,
    score_from_audit,
    score_from_lint,
    score_from_profile,
)


@pytest.fixture
def clean_audit() -> AuditResult:
    return AuditResult(issues=[])


@pytest.fixture
def clean_lint() -> LintResult:
    return LintResult(issues=[])


@pytest.fixture
def healthy_profile() -> EnvProfile:
    return EnvProfile(
        total_keys=10,
        empty_values=0,
        secret_keys=3,
        plain_keys=7,
    )


def test_grade_boundaries():
    assert _grade(95) == "A"
    assert _grade(80) == "B"
    assert _grade(65) == "C"
    assert _grade(45) == "D"
    assert _grade(30) == "F"


def test_score_from_audit_no_issues(clean_audit):
    score = score_from_audit(clean_audit)
    assert score == 40.0


def test_score_from_audit_with_errors():
    result = AuditResult(issues=[AuditIssue(key="SECRET", message="empty", severity="error")])
    score = score_from_audit(result)
    assert score == 30.0


def test_score_from_audit_clamped_at_zero():
    issues = [AuditIssue(key=f"K{i}", message="err", severity="error") for i in range(10)]
    result = AuditResult(issues=issues)
    assert score_from_audit(result) == 0.0


def test_score_from_lint_no_issues(clean_lint):
    assert score_from_lint(clean_lint) == 30.0


def test_score_from_lint_with_warning():
    result = LintResult(issues=[LintIssue(key="db_host", message="lowercase", severity="warning")])
    score = score_from_lint(result)
    assert score == 28.0


def test_score_from_profile_full(healthy_profile):
    score = score_from_profile(healthy_profile)
    assert score == 30.0


def test_score_from_profile_with_empty_values():
    profile = EnvProfile(total_keys=10, empty_values=5, secret_keys=2, plain_keys=8)
    score = score_from_profile(profile)
    assert score == 15.0


def test_score_from_profile_no_keys():
    profile = EnvProfile(total_keys=0, empty_values=0, secret_keys=0, plain_keys=0)
    assert score_from_profile(profile) == 0.0


def test_compute_health_score_perfect(clean_audit, clean_lint, healthy_profile):
    result = compute_health_score(clean_audit, clean_lint, healthy_profile)
    assert result.total == 100.0
    assert result.grade == "A"
    assert "audit" in result.breakdown
    assert "lint" in result.breakdown
    assert "profile" in result.breakdown


def test_compute_health_score_degraded():
    audit = AuditResult(issues=[AuditIssue(key="X", message="empty secret", severity="error")])
    lint = LintResult(issues=[LintIssue(key="y", message="lowercase", severity="warning")])
    profile = EnvProfile(total_keys=4, empty_values=2, secret_keys=1, plain_keys=3)
    result = compute_health_score(audit, lint, profile)
    assert result.total < 100.0
    assert isinstance(result.grade, str)
