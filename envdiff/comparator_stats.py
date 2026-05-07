"""Statistics and metrics derived from comparison results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class ComparisonStats:
    """Aggregated statistics for a diff result."""
    total_keys: int = 0
    missing_count: int = 0
    mismatch_count: int = 0
    matching_count: int = 0
    environments: List[str] = field(default_factory=list)
    coverage: Dict[str, float] = field(default_factory=dict)

    @property
    def health_ratio(self) -> float:
        """Ratio of matching keys to total keys (0.0 – 1.0)."""
        if self.total_keys == 0:
            return 1.0
        return self.matching_count / self.total_keys

    @property
    def problem_count(self) -> int:
        return self.missing_count + self.mismatch_count


def compute_stats(diff: DiffResult, env_names: List[str]) -> ComparisonStats:
    """Compute summary statistics from a DiffResult."""
    all_keys = (
        set(diff.missing_keys)
        | set(diff.mismatched_keys)
        | set(diff.matching_keys)
    )
    total = len(all_keys)

    coverage: Dict[str, float] = {}
    for name in env_names:
        defined = sum(
            1 for k in all_keys if k not in diff.missing_keys
        )
        coverage[name] = defined / total if total else 1.0

    return ComparisonStats(
        total_keys=total,
        missing_count=len(diff.missing_keys),
        mismatch_count=len(diff.mismatched_keys),
        matching_count=len(diff.matching_keys),
        environments=list(env_names),
        coverage=coverage,
    )


def stats_to_dict(stats: ComparisonStats) -> dict:
    """Serialize ComparisonStats to a plain dictionary."""
    return {
        "total_keys": stats.total_keys,
        "missing_count": stats.missing_count,
        "mismatch_count": stats.mismatch_count,
        "matching_count": stats.matching_count,
        "health_ratio": round(stats.health_ratio, 4),
        "problem_count": stats.problem_count,
        "environments": stats.environments,
        "coverage": {k: round(v, 4) for k, v in stats.coverage.items()},
    }
