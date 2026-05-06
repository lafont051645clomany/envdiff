"""Groups env keys by shared prefix or namespace for structured reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class KeyGroup:
    prefix: str
    keys: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.keys)


@dataclass
class GroupReport:
    groups: Dict[str, KeyGroup] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    @property
    def has_groups(self) -> bool:
        return bool(self.groups)

    @property
    def total_keys(self) -> int:
        grouped = sum(g.count for g in self.groups.values())
        return grouped + len(self.ungrouped)


def extract_prefix(key: str, delimiter: str = "_") -> Optional[str]:
    """Return the prefix (first segment) of a key, or None if no delimiter found."""
    if delimiter not in key:
        return None
    return key.split(delimiter, 1)[0]


def group_keys(keys: List[str], delimiter: str = "_", min_group_size: int = 2) -> GroupReport:
    """Group a list of env keys by their prefix.

    Only prefixes with at least `min_group_size` keys are treated as groups;
    the rest go into `ungrouped`.
    """
    prefix_map: Dict[str, List[str]] = {}
    for key in keys:
        prefix = extract_prefix(key, delimiter)
        if prefix:
            prefix_map.setdefault(prefix, []).append(key)
        else:
            prefix_map.setdefault("__none__", []).append(key)

    report = GroupReport()
    for prefix, members in prefix_map.items():
        if prefix == "__none__" or len(members) < min_group_size:
            report.ungrouped.extend(members)
        else:
            report.groups[prefix] = KeyGroup(prefix=prefix, keys=sorted(members))

    report.ungrouped.sort()
    return report


def group_env(env: Dict[str, str], delimiter: str = "_", min_group_size: int = 2) -> GroupReport:
    """Convenience wrapper: group keys from an env dict."""
    return group_keys(list(env.keys()), delimiter=delimiter, min_group_size=min_group_size)
