"""Generate patch suggestions to reconcile differences between two .env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class PatchEntry:
    """A single suggested change to apply to a target .env file."""

    key: str
    action: str          # 'add', 'update', 'remove'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    @property
    def label(self) -> str:
        if self.action == "add":
            return f"+ {self.key}={self.new_value}"
        if self.action == "update":
            return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"
        return f"- {self.key}"


@dataclass
class PatchReport:
    """Collection of patch entries for a given target environment."""

    source_label: str
    target_label: str
    entries: List[PatchEntry] = field(default_factory=list)

    @property
    def has_patches(self) -> bool:
        return bool(self.entries)

    @property
    def count(self) -> int:
        return len(self.entries)

    def by_action(self, action: str) -> List[PatchEntry]:
        return [e for e in self.entries if e.action == action]


def build_patch(
    diff: DiffResult,
    source_label: str,
    target_label: str,
    include_removals: bool = False,
) -> PatchReport:
    """Build a PatchReport that brings *target* in line with *source*.

    Args:
        diff: A DiffResult produced by compare_envs(source, target).
        source_label: Human-readable name for the reference environment.
        target_label: Human-readable name for the environment to patch.
        include_removals: When True, also suggest removing keys that exist
            only in the target (i.e. missing from source).
    """
    entries: List[PatchEntry] = []

    # Keys present in source but missing from target -> add them
    for key in diff.missing_keys:
        entries.append(
            PatchEntry(key=key, action="add", new_value=diff.source.get(key))
        )

    # Keys with differing values -> update target
    for key, (src_val, _tgt_val) in diff.mismatched_keys.items():
        entries.append(
            PatchEntry(
                key=key,
                action="update",
                old_value=_tgt_val,
                new_value=src_val,
            )
        )

    # Keys in target but not source -> optional removal
    if include_removals:
        for key in diff.extra_keys:
            entries.append(
                PatchEntry(key=key, action="remove", old_value=diff.target.get(key))
            )

    entries.sort(key=lambda e: e.key)
    return PatchReport(
        source_label=source_label,
        target_label=target_label,
        entries=entries,
    )


def patch_to_dict(report: PatchReport) -> Dict:
    """Serialise a PatchReport to a plain dictionary."""
    return {
        "source": report.source_label,
        "target": report.target_label,
        "count": report.count,
        "entries": [
            {
                "key": e.key,
                "action": e.action,
                "old_value": e.old_value,
                "new_value": e.new_value,
            }
            for e in report.entries
        ],
    }
