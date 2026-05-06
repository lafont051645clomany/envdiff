"""Normalize .env values for consistent comparison across environments."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class NormalizeResult:
    original: Dict[str, str]
    normalized: Dict[str, str]
    changes: Dict[str, tuple] = field(default_factory=dict)  # key -> (before, after)

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def change_count(self) -> int:
        return len(self.changes)


def normalize_value(value: str) -> str:
    """Normalize a single value: strip whitespace, lowercase booleans, unify empty."""
    value = value.strip()
    if value.lower() in ("true", "yes", "1", "on"):
        return "true"
    if value.lower() in ("false", "no", "0", "off"):
        return "false"
    if value == "":
        return ""
    return value


def normalize_env(env: Dict[str, str]) -> NormalizeResult:
    """Apply normalization to all values in an env dict."""
    normalized: Dict[str, str] = {}
    changes: Dict[str, tuple] = {}

    for key, value in env.items():
        new_value = normalize_value(value)
        normalized[key] = new_value
        if new_value != value:
            changes[key] = (value, new_value)

    return NormalizeResult(original=dict(env), normalized=normalized, changes=changes)


def normalize_all(envs: Dict[str, Dict[str, str]]) -> Dict[str, NormalizeResult]:
    """Normalize all named environments."""
    return {name: normalize_env(env) for name, env in envs.items()}


def extract_normalized(result: NormalizeResult) -> Dict[str, str]:
    """Convenience: return just the normalized dict from a NormalizeResult."""
    return result.normalized
