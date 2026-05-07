"""Strip unused or stale keys from an env file based on a reference template."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class StripReport:
    """Result of stripping keys from an env dict."""

    label: str
    original: Dict[str, str]
    stripped: Dict[str, str]
    removed_keys: List[str] = field(default_factory=list)

    @property
    def has_removals(self) -> bool:
        return len(self.removed_keys) > 0

    @property
    def removal_count(self) -> int:
        return len(self.removed_keys)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "removed_keys": self.removed_keys,
            "removal_count": self.removal_count,
            "has_removals": self.has_removals,
            "stripped": self.stripped,
        }


def strip_keys(env: Dict[str, str], reference: Set[str], label: str = "") -> StripReport:
    """Remove keys from *env* that are not present in *reference*.

    Args:
        env: The environment dict to strip.
        reference: Set of keys considered valid / in-use.
        label: Optional human-readable label for the source env.

    Returns:
        A StripReport describing what was removed.
    """
    removed = [k for k in env if k not in reference]
    stripped = {k: v for k, v in env.items() if k in reference}
    return StripReport(
        label=label,
        original=dict(env),
        stripped=stripped,
        removed_keys=sorted(removed),
    )


def strip_all(
    envs: Dict[str, Dict[str, str]], reference: Set[str]
) -> Dict[str, StripReport]:
    """Apply strip_keys to every env in *envs* using the same *reference* set.

    Args:
        envs: Mapping of label -> env dict.
        reference: Keys that should be retained.

    Returns:
        Mapping of label -> StripReport.
    """
    return {label: strip_keys(env, reference, label=label) for label, env in envs.items()}


def reference_from_envs(envs: Dict[str, Dict[str, str]]) -> Set[str]:
    """Build a reference set as the *intersection* of all env keys.

    Keys that appear in every env are considered canonical; anything present
    in only a subset is a candidate for stripping.
    """
    if not envs:
        return set()
    sets = [set(e.keys()) for e in envs.values()]
    result: Set[str] = sets[0]
    for s in sets[1:]:
        result = result & s
    return result
