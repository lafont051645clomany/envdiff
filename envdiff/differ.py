"""Unified diff output for .env file comparisons.

Provides a human-readable, line-by-line diff view between two env files,
similar in style to `diff` or `git diff`.
"""

from typing import Dict, List, Tuple


DIFF_ADDED = "added"
DIFF_REMOVED = "removed"
DIFF_CHANGED = "changed"
DIFF_UNCHANGED = "unchanged"


def build_unified_diff(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
    label_a: str = "a",
    label_b: str = "b",
) -> List[str]:
    """Return a list of unified-diff-style lines comparing env_a to env_b."""
    lines: List[str] = []
    lines.append(f"--- {label_a}")
    lines.append(f"+++ {label_b}")

    all_keys = sorted(set(env_a) | set(env_b))
    for key in all_keys:
        if key in env_a and key not in env_b:
            lines.append(f"-{key}={env_a[key]}")
        elif key not in env_a and key in env_b:
            lines.append(f"+{key}={env_b[key]}")
        elif env_a[key] != env_b[key]:
            lines.append(f"-{key}={env_a[key]}")
            lines.append(f"+{key}={env_b[key]}")
        else:
            lines.append(f" {key}={env_a[key]}")
    return lines


def classify_keys(
    env_a: Dict[str, str],
    env_b: Dict[str, str],
) -> Dict[str, str]:
    """Return a mapping of key -> diff status for all keys across both envs."""
    result: Dict[str, str] = {}
    all_keys = set(env_a) | set(env_b)
    for key in all_keys:
        if key in env_a and key not in env_b:
            result[key] = DIFF_REMOVED
        elif key not in env_a and key in env_b:
            result[key] = DIFF_ADDED
        elif env_a[key] != env_b[key]:
            result[key] = DIFF_CHANGED
        else:
            result[key] = DIFF_UNCHANGED
    return result


def count_by_status(classification: Dict[str, str]) -> Dict[str, int]:
    """Return counts of keys grouped by their diff status."""
    counts: Dict[str, int] = {
        DIFF_ADDED: 0,
        DIFF_REMOVED: 0,
        DIFF_CHANGED: 0,
        DIFF_UNCHANGED: 0,
    }
    for status in classification.values():
        if status in counts:
            counts[status] += 1
    return counts
