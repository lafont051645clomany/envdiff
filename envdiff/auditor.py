"""Audit env files for common security and hygiene issues."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.masker import is_secret_key

# Values that look like placeholders or defaults that should be replaced
_PLACEHOLDER_PATTERNS = {
    "changeme", "change_me", "todo", "fixme", "placeholder",
    "your_secret", "your_key", "example", "replace_me", "<secret>",
    "<key>", "<value>", "...", "xxx", "yyy",
}


@dataclass
class AuditIssue:
    key: str
    severity: str  # "error" | "warning" | "info"
    message: str


@dataclass
class AuditResult:
    env_name: str
    issues: List[AuditIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)


def audit_env(env: Dict[str, str], env_name: str = "env") -> AuditResult:
    """Audit a single env dict and return an AuditResult."""
    result = AuditResult(env_name=env_name)

    for key, value in env.items():
        # Secret key with empty value
        if is_secret_key(key) and value.strip() == "":
            result.issues.append(AuditIssue(
                key=key,
                severity="error",
                message=f"Secret key '{key}' has an empty value.",
            ))

        # Placeholder / default value detected
        elif value.strip().lower() in _PLACEHOLDER_PATTERNS:
            result.issues.append(AuditIssue(
                key=key,
                severity="warning",
                message=f"Key '{key}' appears to contain a placeholder value: '{value}'.",
            ))

        # Non-secret key with suspiciously long value (possible accidental secret)
        elif not is_secret_key(key) and len(value) > 128:
            result.issues.append(AuditIssue(
                key=key,
                severity="info",
                message=(
                    f"Key '{key}' has a very long value ({len(value)} chars); "
                    "consider whether it should be treated as a secret."
                ),
            ))

    return result


def audit_all(envs: Dict[str, Dict[str, str]]) -> Dict[str, AuditResult]:
    """Audit multiple named env dicts and return a mapping of results."""
    return {name: audit_env(env, env_name=name) for name, env in envs.items()}
