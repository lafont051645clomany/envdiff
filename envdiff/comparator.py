"""Comparator module for diffing parsed .env file contents."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two or more .env files."""

    files: List[str]
    missing_keys: Dict[str, List[str]] = field(default_factory=dict)
    # key -> {file: value}
    mismatched_keys: Dict[str, Dict[str, str]] = field(default_factory=dict)
    all_keys: Set[str] = field(default_factory=set)

    @property
    def has_differences(self) -> bool:
        return bool(self.missing_keys or self.mismatched_keys)


def compare_envs(
    env_map: Dict[str, Dict[str, str]],
) -> DiffResult:
    """Compare multiple parsed .env dictionaries.

    Args:
        env_map: Mapping of filename -> {key: value}.

    Returns:
        DiffResult with missing and mismatched key information.
    """
    files = list(env_map.keys())
    all_keys: Set[str] = set()
    for vars_dict in env_map.values():
        all_keys.update(vars_dict.keys())

    missing_keys: Dict[str, List[str]] = {}
    mismatched_keys: Dict[str, Dict[str, str]] = {}

    for key in sorted(all_keys):
        present_in = [f for f in files if key in env_map[f]]
        absent_in = [f for f in files if key not in env_map[f]]

        if absent_in:
            missing_keys[key] = absent_in

        if len(present_in) > 1:
            values = {f: env_map[f][key] for f in present_in}
            unique_values = set(values.values())
            if len(unique_values) > 1:
                mismatched_keys[key] = values

    return DiffResult(
        files=files,
        missing_keys=missing_keys,
        mismatched_keys=mismatched_keys,
        all_keys=all_keys,
    )
