"""Detect deprecated or legacy keys in env files based on known patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Keys that are considered deprecated, mapped to optional replacement suggestions
DEFAULT_DEPRECATED: Dict[str, Optional[str]] = {
    "DATABASE_URL": "DB_URL",
    "SECRET_KEY": "APP_SECRET",
    "REDIS_URL": "CACHE_URL",
    "SENDGRID_API_KEY": "EMAIL_API_KEY",
    "AWS_ACCESS_KEY": "AWS_ACCESS_KEY_ID",
    "DISABLE_HTTPS": None,
    "LEGACY_MODE": None,
    "OLD_API_HOST": "API_HOST",
}


@dataclass
class DeprecationWarning_:  # noqa: N801 — avoid shadowing builtin name
    key: str
    suggestion: Optional[str] = None

    @property
    def label(self) -> str:
        if self.suggestion:
            return f"{self.key} -> use {self.suggestion} instead"
        return f"{self.key} (no replacement available)"


@dataclass
class DeprecationReport:
    warnings: List[DeprecationWarning_] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)

    @property
    def deprecated_keys(self) -> List[str]:
        return [w.key for w in self.warnings]

    def to_dict(self) -> dict:
        return {
            "deprecated_count": len(self.warnings),
            "warnings": [
                {"key": w.key, "suggestion": w.suggestion} for w in self.warnings
            ],
        }


def find_deprecated(
    env: Dict[str, str],
    deprecated_map: Optional[Dict[str, Optional[str]]] = None,
) -> DeprecationReport:
    """Return a DeprecationReport for any deprecated keys found in *env*."""
    mapping = deprecated_map if deprecated_map is not None else DEFAULT_DEPRECATED
    warnings: List[DeprecationWarning_] = []
    for key in env:
        if key in mapping:
            warnings.append(DeprecationWarning_(key=key, suggestion=mapping[key]))
    return DeprecationReport(warnings=warnings)


def find_deprecated_all(
    envs: Dict[str, Dict[str, str]],
    deprecated_map: Optional[Dict[str, Optional[str]]] = None,
) -> Dict[str, DeprecationReport]:
    """Run deprecation checks across multiple named envs."""
    return {name: find_deprecated(env, deprecated_map) for name, env in envs.items()}
