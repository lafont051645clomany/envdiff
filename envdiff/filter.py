"""Filtering utilities for env diff results."""

import re
from typing import List, Optional
from envdiff.comparator import DiffResult


def filter_keys_by_pattern(
    keys: List[str], pattern: str, invert: bool = False
) -> List[str]:
    """
    Filter a list of keys using a regex pattern.

    Args:
        keys: List of environment variable names.
        pattern: Regex pattern to match against.
        invert: If True, return keys that do NOT match.

    Returns:
        Filtered list of keys.
    """
    compiled = re.compile(pattern, re.IGNORECASE)
    if invert:
        return [k for k in keys if not compiled.search(k)]
    return [k for k in keys if compiled.search(k)]


def filter_diff_by_pattern(
    diff: DiffResult,
    pattern: Optional[str],
    invert: bool = False,
) -> DiffResult:
    """
    Return a new DiffResult containing only entries whose keys match the pattern.

    Args:
        diff: Original DiffResult.
        pattern: Regex pattern string. If None, returns the diff unchanged.
        invert: If True, exclude matching keys instead.

    Returns:
        Filtered DiffResult.
    """
    if pattern is None:
        return diff

    filtered_missing = {
        env: filter_keys_by_pattern(keys, pattern, invert=invert)
        for env, keys in diff.missing.items()
    }
    # Remove empty env entries
    filtered_missing = {env: keys for env, keys in filtered_missing.items() if keys}

    filtered_mismatches = [
        (key, val_a, val_b)
        for key, val_a, val_b in diff.mismatches
        if (
            re.search(pattern, key, re.IGNORECASE) is not None
        ) != invert
    ]

    return DiffResult(
        missing=filtered_missing,
        mismatches=filtered_mismatches,
    )
