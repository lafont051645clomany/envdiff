"""Prune unused or redundant keys from an env dict based on a reference set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class PruneReport:
    label: str
    original: Dict[str, str]
    pruned: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)
    reason: Dict[str, str] = field(default_factory=dict)

    @property
    def has_removals(self) -> bool:
        return len(self.removed_keys) > 0

    @property
    def removal_count(self) -> int:
        return len(self.removed_keys)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "removal_count": self.removal_count,
            "removed_keys": sorted(self.removed_keys),
            "pruned_env": self.pruned,
        }


def prune_keys(
    env: Dict[str, str],
    reference: Set[str],
    *,
    label: str = "env",
    prune_empty: bool = False,
) -> PruneReport:
    """Remove keys from *env* that are absent from *reference*.

    If *prune_empty* is True, also remove keys whose value is an empty string.
    """
    removed: List[str] = []
    reason: Dict[str, str] = {}
    pruned: Dict[str, str] = {}

    for key, value in env.items():
        if key not in reference:
            removed.append(key)
            reason[key] = "not_in_reference"
        elif prune_empty and value == "":
            removed.append(key)
            reason[key] = "empty_value"
        else:
            pruned[key] = value

    return PruneReport(
        label=label,
        original=dict(env),
        pruned=pruned,
        removed_keys=sorted(removed),
        reason=reason,
    )


def prune_all(
    envs: Dict[str, Dict[str, str]],
    reference: Optional[Set[str]] = None,
    *,
    prune_empty: bool = False,
) -> Dict[str, PruneReport]:
    """Prune multiple envs.  If *reference* is None, the union of all keys is used."""
    if reference is None:
        reference = set().union(*envs.values())

    return {
        label: prune_keys(env, reference, label=label, prune_empty=prune_empty)
        for label, env in envs.items()
    }
