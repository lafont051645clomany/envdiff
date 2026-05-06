"""Scores .env file health based on audit, lint, and profile results."""

from dataclasses import dataclass, field
from typing import Dict

from envdiff.auditor import AuditResult
from envdiff.linter import LintResult
from envdiff.profiler import EnvProfile


@dataclass
class HealthScore:
    total: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    grade: str = "F"

    def __post_init__(self):
        self.grade = _grade(self.total)


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 40:
        return "D"
    return "F"


def score_from_audit(result: AuditResult, weight: float = 40.0) -> float:
    """Deduct points for audit errors and warnings."""
    errors = len(result.errors)
    warnings = len(result.warnings)
    deduction = (errors * 10) + (warnings * 3)
    return max(0.0, weight - deduction)


def score_from_lint(result: LintResult, weight: float = 30.0) -> float:
    """Deduct points for lint errors and warnings."""
    from envdiff.linter import error_count, warning_count
    errors = error_count(result)
    warnings = warning_count(result)
    deduction = (errors * 8) + (warnings * 2)
    return max(0.0, weight - deduction)


def score_from_profile(profile: EnvProfile, weight: float = 30.0) -> float:
    """Award points based on secret ratio and non-empty values."""
    if profile.total_keys == 0:
        return 0.0
    non_empty_ratio = (profile.total_keys - profile.empty_values) / profile.total_keys
    return round(weight * non_empty_ratio, 2)


def compute_health_score(
    audit: AuditResult,
    lint: LintResult,
    profile: EnvProfile,
) -> HealthScore:
    """Compute a composite health score from audit, lint, and profile data."""
    audit_score = score_from_audit(audit)
    lint_score = score_from_lint(lint)
    profile_score = score_from_profile(profile)
    total = round(audit_score + lint_score + profile_score, 2)
    return HealthScore(
        total=total,
        breakdown={
            "audit": audit_score,
            "lint": lint_score,
            "profile": profile_score,
        },
    )
