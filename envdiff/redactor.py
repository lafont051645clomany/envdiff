"""Redactor module: strip or replace sensitive values before sharing env data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.masker import is_secret_key

DEFAULT_REDACT_PLACEHOLDER = "[REDACTED]"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redact_count(self) -> int:
        return len(self.redacted_keys)

    @property
    def has_redactions(self) -> bool:
        return self.redact_count > 0


def redact_env(
    env: Dict[str, str],
    placeholder: str = DEFAULT_REDACT_PLACEHOLDER,
    extra_keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
) -> RedactResult:
    """Return a copy of *env* with secret values replaced by *placeholder*.

    Args:
        env: Mapping of key -> value to redact.
        placeholder: String used in place of secret values.
        extra_keys: Additional keys to treat as secret regardless of name.
        pattern: Optional regex pattern forwarded to :func:`is_secret_key`.
    """
    extra = set(extra_keys or [])
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if key in extra or is_secret_key(key, pattern=pattern):
            redacted[key] = placeholder
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
    )


def redact_all(
    envs: Dict[str, Dict[str, str]],
    placeholder: str = DEFAULT_REDACT_PLACEHOLDER,
    extra_keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
) -> Dict[str, RedactResult]:
    """Apply :func:`redact_env` to every environment in *envs*."""
    return {
        name: redact_env(env, placeholder=placeholder, extra_keys=extra_keys, pattern=pattern)
        for name, env in envs.items()
    }
