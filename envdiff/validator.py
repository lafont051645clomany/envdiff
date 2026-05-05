"""Validates .env file values against expected types or patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


BUILTIN_RULES: Dict[str, str] = {
    "url": r"^https?://.+",
    "integer": r"^-?\d+$",
    "boolean": r"^(true|false|1|0|yes|no)$",
    "email": r"^[\w.+-]+@[\w-]+\.[\w.]+$",
    "non_empty": r".+",
}


@dataclass
class ValidationError:
    key: str
    env_name: str
    value: str
    rule: str
    message: str


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, error: ValidationError) -> None:
        self.errors.append(error)


def _resolve_pattern(rule: str) -> Optional[str]:
    """Return regex pattern for a rule name or treat rule as raw regex."""
    return BUILTIN_RULES.get(rule, rule)


def validate_env(
    envs: Dict[str, Dict[str, str]],
    rules: Dict[str, str],
) -> ValidationResult:
    """Validate env values against a mapping of key -> rule.

    Args:
        envs: Mapping of env_name -> {key: value}.
        rules: Mapping of key -> rule name or regex pattern.

    Returns:
        A ValidationResult containing any errors found.
    """
    result = ValidationResult()

    for env_name, env_vars in envs.items():
        for key, rule in rules.items():
            if key not in env_vars:
                continue
            value = env_vars[key]
            pattern = _resolve_pattern(rule)
            if pattern and not re.match(pattern, value, re.IGNORECASE):
                result.add_error(
                    ValidationError(
                        key=key,
                        env_name=env_name,
                        value=value,
                        rule=rule,
                        message=(
                            f"[{env_name}] '{key}' value '{value}' "
                            f"does not match rule '{rule}'"
                        ),
                    )
                )

    return result


def format_validation_report(result: ValidationResult) -> str:
    """Return a human-readable string of validation errors."""
    if result.is_valid:
        return "All values passed validation."
    lines = [f"Validation failed with {len(result.errors)} error(s):"]
    for err in result.errors:
        lines.append(f"  - {err.message}")
    return "\n".join(lines)
