"""Detects and resolves variable interpolation in .env files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_refs: Dict[str, List[str]] = field(default_factory=dict)
    original: Dict[str, str] = field(default_factory=dict)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved_refs)

    @property
    def changed_keys(self) -> List[str]:
        return [
            k for k, v in self.resolved.items()
            if v != self.original.get(k, v)
        ]


def find_references(value: str) -> List[str]:
    """Return all variable names referenced in a value string."""
    matches = _REF_PATTERN.findall(value)
    return [m[0] or m[1] for m in matches]


def _resolve_value(
    key: str,
    value: str,
    env: Dict[str, str],
    seen: Optional[set] = None,
) -> tuple[str, List[str]]:
    """Recursively resolve a single value; return (resolved, unresolved_refs)."""
    if seen is None:
        seen = set()
    if key in seen:
        return value, []  # circular reference guard
    seen = seen | {key}

    refs = find_references(value)
    if not refs:
        return value, []

    unresolved: List[str] = []
    result = value

    for ref in refs:
        if ref in env:
            sub, sub_unresolved = _resolve_value(ref, env[ref], env, seen)
            result = re.sub(r"\$\{" + ref + r"\}|\$" + ref + r"(?![A-Z0-9_])", sub, result)
            unresolved.extend(sub_unresolved)
        else:
            unresolved.append(ref)

    return result, unresolved


def interpolate_env(env: Dict[str, str]) -> InterpolationResult:
    """Resolve all variable references within an env dict."""
    result = InterpolationResult(original=dict(env))

    for key, value in env.items():
        resolved_value, missing = _resolve_value(key, value, env)
        result.resolved[key] = resolved_value
        if missing:
            result.unresolved_refs[key] = missing

    return result
