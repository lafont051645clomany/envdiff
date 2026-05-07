"""Summarizes .env file contents into human-readable statistics and insights."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.masker import is_secret_key
from envdiff.classifier import classify_key


@dataclass
class EnvSummary:
    """Holds summary statistics for a single .env file."""

    label: str
    total_keys: int
    empty_keys: List[str] = field(default_factory=list)
    secret_keys: List[str] = field(default_factory=list)
    categories: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def empty_count(self) -> int:
        return len(self.empty_keys)

    @property
    def secret_count(self) -> int:
        return len(self.secret_keys)

    @property
    def plain_count(self) -> int:
        return self.total_keys - self.secret_count


def summarize_env(label: str, env: Dict[str, str]) -> EnvSummary:
    """Produce an EnvSummary for a single parsed environment dict."""
    empty_keys = [k for k, v in env.items() if v == ""]
    secret_keys = [k for k in env if is_secret_key(k)]

    categories: Dict[str, List[str]] = {}
    for key in env:
        cat = classify_key(key)
        categories.setdefault(cat, []).append(key)

    return EnvSummary(
        label=label,
        total_keys=len(env),
        empty_keys=empty_keys,
        secret_keys=secret_keys,
        categories=categories,
    )


def summarize_all(named_envs: Dict[str, Dict[str, str]]) -> List[EnvSummary]:
    """Summarize multiple named environments."""
    return [summarize_env(label, env) for label, env in named_envs.items()]
