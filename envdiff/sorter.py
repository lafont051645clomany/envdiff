"""Sorting and grouping utilities for env diff results."""

from typing import Dict, List, Tuple
from envdiff.comparator import DiffResult


def sort_keys_alphabetically(keys: List[str]) -> List[str]:
    """Return a sorted list of keys in alphabetical order."""
    return sorted(keys, key=str.lower)


def group_by_prefix(keys: List[str], delimiter: str = "_") -> Dict[str, List[str]]:
    """
    Group keys by their prefix (the part before the first delimiter).

    Keys without a delimiter are grouped under an empty string key.
    """
    groups: Dict[str, List[str]] = {}
    for key in keys:
        if delimiter in key:
            prefix = key.split(delimiter, 1)[0]
        else:
            prefix = ""
        groups.setdefault(prefix, []).append(key)
    return groups


def sort_diff_result(
    diff: DiffResult,
    alphabetical: bool = True,
) -> DiffResult:
    """
    Return a new DiffResult with missing and mismatched keys sorted.

    Args:
        diff: The original DiffResult.
        alphabetical: If True, sort keys alphabetically.

    Returns:
        A new DiffResult with sorted collections.
    """
    sort_fn = sort_keys_alphabetically if alphabetical else list

    sorted_missing: Dict[str, List[str]] = {
        env: sort_fn(keys) for env, keys in diff.missing.items()
    }
    sorted_mismatches: List[Tuple[str, str, str]] = (
        sorted(diff.mismatches, key=lambda t: t[0].lower())
        if alphabetical
        else list(diff.mismatches)
    )

    return DiffResult(
        missing=sorted_missing,
        mismatches=sorted_mismatches,
    )


def get_all_diff_keys(diff: DiffResult) -> List[str]:
    """Return a deduplicated list of all keys involved in the diff."""
    keys = set()
    for key_list in diff.missing.values():
        keys.update(key_list)
    for key, _, _ in diff.mismatches:
        keys.add(key)
    return list(keys)
