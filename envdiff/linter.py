"""Lints .env files for common style and formatting issues."""

from dataclasses import dataclass, field
from typing import List, Dict
import re


@dataclass
class LintIssue:
    line_number: int
    key: str
    message: str
    severity: str = "warning"  # "warning" or "error"


@dataclass
class LintResult:
    filename: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


def lint_env_file(filepath: str) -> LintResult:
    """Read a .env file and return a LintResult with any detected issues."""
    result = LintResult(filename=filepath)

    try:
        with open(filepath, "r") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        result.issues.append(LintIssue(0, "", f"File not found: {filepath}", "error"))
        return result

    seen_keys: Dict[str, int] = {}

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip("\n")

        # Skip blank lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in line:
            result.issues.append(LintIssue(lineno, "", "Line missing '=' separator", "error"))
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        # Key naming convention: should be UPPER_SNAKE_CASE
        if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
            result.issues.append(LintIssue(lineno, key, "Key should be UPPER_SNAKE_CASE", "warning"))

        # Detect unquoted values with spaces
        if value and not value.startswith(("'", '"')) and " " in value.split("#")[0].rstrip():
            result.issues.append(LintIssue(lineno, key, "Value with spaces should be quoted", "warning"))

        # Detect duplicate keys
        if key in seen_keys:
            result.issues.append(
                LintIssue(lineno, key, f"Duplicate key (first seen on line {seen_keys[key]})", "error")
            )
        else:
            seen_keys[key] = lineno

        # Warn on empty values
        bare_value = value.strip().split("#")[0].strip()
        if bare_value == "":
            result.issues.append(LintIssue(lineno, key, "Key has an empty value", "warning"))

    return result


def lint_multiple(filepaths: List[str]) -> List[LintResult]:
    """Lint multiple .env files and return a list of results."""
    return [lint_env_file(fp) for fp in filepaths]
