"""Profile .env files for statistical insights: key counts, secret ratios, prefix groups."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.masker import is_secret_key
from envdiff.sorter import group_by_prefix


@dataclass
class EnvProfile:
    """Statistical profile of a single .env file."""

    name: str
    total_keys: int = 0
    secret_keys: int = 0
    plain_keys: int = 0
    empty_values: int = 0
    prefix_groups: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def secret_ratio(self) -> float:
        """Fraction of keys considered secrets (0.0–1.0)."""
        if self.total_keys == 0:
            return 0.0
        return self.secret_keys / self.total_keys

    def summary(self) -> str:
        """Return a human-readable one-line summary."""
        return (
            f"{self.name}: {self.total_keys} keys, "
            f"{self.secret_keys} secret ({self.secret_ratio:.0%}), "
            f"{len(self.prefix_groups)} prefix group(s), "
            f"{self.empty_values} empty value(s)"
        )


def profile_env(name: str, env: Dict[str, str]) -> EnvProfile:
    """Build an EnvProfile from an env mapping."""
    prof = EnvProfile(name=name)
    prof.total_keys = len(env)
    prof.empty_values = sum(1 for v in env.values() if v == "")
    prof.secret_keys = sum(1 for k in env if is_secret_key(k))
    prof.plain_keys = prof.total_keys - prof.secret_keys
    prof.prefix_groups = group_by_prefix(list(env.keys()))
    return prof


def profile_all(envs: Dict[str, Dict[str, str]]) -> Dict[str, EnvProfile]:
    """Profile every environment in *envs* and return a mapping of name → profile."""
    return {name: profile_env(name, env) for name, env in envs.items()}


def compare_profiles(profiles: Dict[str, EnvProfile]) -> Dict[str, object]:
    """Return a lightweight comparison dict across profiles."""
    if not profiles:
        return {}
    totals = {name: p.total_keys for name, p in profiles.items()}
    max_name = max(totals, key=totals.__getitem__)
    min_name = min(totals, key=totals.__getitem__)
    return {
        "profiles": {name: p.summary() for name, p in profiles.items()},
        "most_keys": max_name,
        "fewest_keys": min_name,
        "key_counts": totals,
    }
