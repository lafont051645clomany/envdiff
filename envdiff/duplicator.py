"""Detect duplicate values across keys in one or more env files."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateGroup:
    """A set of keys that share the same value."""

    value: str
    keys: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.keys)


@dataclass
class DuplicateReport:
    """Result of a duplicate-value scan."""

    env_name: str
    groups: List[DuplicateGroup] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.groups) > 0

    @property
    def total_duplicate_keys(self) -> int:
        return sum(g.count for g in self.groups)


def find_duplicates(env: Dict[str, str], env_name: str = "env") -> DuplicateReport:
    """Return a DuplicateReport for keys that share the same value."""
    value_map: Dict[str, List[str]] = defaultdict(list)
    for key, value in env.items():
        value_map[value].append(key)

    groups = [
        DuplicateGroup(value=val, keys=sorted(keys))
        for val, keys in value_map.items()
        if len(keys) > 1
    ]
    groups.sort(key=lambda g: g.keys[0])
    return DuplicateReport(env_name=env_name, groups=groups)


def find_duplicates_all(
    envs: Dict[str, Dict[str, str]]
) -> Dict[str, DuplicateReport]:
    """Run duplicate detection across multiple named envs."""
    return {name: find_duplicates(env, env_name=name) for name, env in envs.items()}
