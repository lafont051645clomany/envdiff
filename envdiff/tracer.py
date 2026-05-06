"""Trace the origin of env keys across multiple named environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyTrace:
    """Tracks where a key appears and what value each environment holds."""

    key: str
    origins: Dict[str, Optional[str]] = field(default_factory=dict)

    @property
    def env_count(self) -> int:
        """Number of environments that define this key."""
        return sum(1 for v in self.origins.values() if v is not None)

    @property
    def is_consistent(self) -> bool:
        """True when all environments that define the key share the same value."""
        defined = [v for v in self.origins.values() if v is not None]
        return len(set(defined)) <= 1

    @property
    def unique_values(self) -> List[str]:
        """Distinct non-None values across environments."""
        return list({v for v in self.origins.values() if v is not None})


@dataclass
class TraceReport:
    """Full trace report for a set of environments."""

    env_names: List[str]
    traces: Dict[str, KeyTrace] = field(default_factory=dict)

    @property
    def inconsistent_keys(self) -> List[str]:
        """Keys whose values differ across environments."""
        return [k for k, t in self.traces.items() if not t.is_consistent]

    @property
    def total_keys(self) -> int:
        return len(self.traces)


def trace_key(
    key: str,
    envs: Dict[str, Dict[str, str]],
) -> KeyTrace:
    """Build a KeyTrace for a single key across named envs."""
    origins: Dict[str, Optional[str]] = {
        name: env.get(key) for name, env in envs.items()
    }
    return KeyTrace(key=key, origins=origins)


def trace_all(
    envs: Dict[str, Dict[str, str]],
) -> TraceReport:
    """Trace every key found in any environment."""
    all_keys: set[str] = set()
    for env in envs.values():
        all_keys.update(env.keys())

    traces = {key: trace_key(key, envs) for key in sorted(all_keys)}
    return TraceReport(env_names=list(envs.keys()), traces=traces)
