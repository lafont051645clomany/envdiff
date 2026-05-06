"""Detect and suggest key renames between two environments."""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from envdiff.comparator import DiffResult


@dataclass
class RenameCandidate:
    """A potential rename pair with a confidence score."""
    old_key: str
    new_key: str
    score: float  # 0.0 – 1.0

    @property
    def label(self) -> str:
        return f"{self.old_key} -> {self.new_key} ({self.score:.0%})"


@dataclass
class RenameReport:
    """Collection of rename candidates for a diff."""
    candidates: List[RenameCandidate] = field(default_factory=list)

    @property
    def has_candidates(self) -> bool:
        return bool(self.candidates)

    def above_threshold(self, threshold: float = 0.7) -> List[RenameCandidate]:
        return [c for c in self.candidates if c.score >= threshold]


def _similarity(a: str, b: str) -> float:
    """Return string similarity ratio for two key names (case-insensitive)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def detect_renames(
    diff: DiffResult,
    threshold: float = 0.6,
    max_candidates: int = 1,
) -> RenameReport:
    """Compare missing keys in *base* with extra keys in *other* to find renames.

    Args:
        diff: A DiffResult produced by compare_envs.
        threshold: Minimum similarity score to include a candidate.
        max_candidates: Maximum rename suggestions per missing key.

    Returns:
        RenameReport containing likely rename pairs.
    """
    missing: List[str] = list(diff.missing_keys)
    extra: List[str] = list(diff.extra_keys)

    candidates: List[RenameCandidate] = []

    for old_key in missing:
        scored: List[Tuple[float, str]] = [
            (_similarity(old_key, new_key), new_key) for new_key in extra
        ]
        scored.sort(reverse=True)
        for score, new_key in scored[:max_candidates]:
            if score >= threshold:
                candidates.append(RenameCandidate(old_key=old_key, new_key=new_key, score=score))

    # Sort by descending confidence
    candidates.sort(key=lambda c: c.score, reverse=True)
    return RenameReport(candidates=candidates)


def format_rename_report(report: RenameReport, threshold: float = 0.7) -> str:
    """Render a human-readable rename suggestion block."""
    strong = report.above_threshold(threshold)
    if not strong:
        return "No rename candidates detected."
    lines = ["Possible renames detected:"]
    for c in strong:
        lines.append(f"  {c.label}")
    return "\n".join(lines)
