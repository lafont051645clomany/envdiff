"""High-level pipeline combining filter, sort, and mask for diff processing."""

from typing import Dict, List, Optional

from envdiff.comparator import DiffResult, compare_envs
from envdiff.filter import filter_diff_by_pattern
from envdiff.masker import mask_env
from envdiff.sorter import sort_diff_result


def process_diff(
    envs: Dict[str, Dict[str, str]],
    *,
    filter_pattern: Optional[str] = None,
    invert_filter: bool = False,
    mask_secrets: bool = False,
    secret_pattern: Optional[str] = None,
    sort: bool = True,
) -> DiffResult:
    """
    Run the full envdiff pipeline: compare, filter, sort.

    Args:
        envs: Mapping of env name -> key/value pairs.
        filter_pattern: Optional regex to filter diff keys.
        invert_filter: Invert the filter (exclude matching keys).
        mask_secrets: Whether to mask secret values before comparison.
        secret_pattern: Custom regex for identifying secret keys.
        sort: Whether to sort the resulting diff alphabetically.

    Returns:
        Processed DiffResult.

    Raises:
        ValueError: If fewer than two environments are provided.
    """
    if len(envs) < 2:
        raise ValueError(
            f"At least two environments are required for a diff, got {len(envs)}."
        )

    processed_envs = envs
    if mask_secrets:
        processed_envs = {
            name: mask_env(env, pattern=secret_pattern)
            for name, env in envs.items()
        }

    env_names = list(processed_envs.keys())
    env_values = list(processed_envs.values())
    diff = compare_envs(env_names, env_values)

    if filter_pattern:
        diff = filter_diff_by_pattern(diff, filter_pattern, invert=invert_filter)

    if sort:
        diff = sort_diff_result(diff, alphabetical=True)

    return diff


def summarize_diff(diff: DiffResult) -> Dict[str, int]:
    """
    Return a summary count of missing keys per env and total mismatches.

    Args:
        diff: A DiffResult instance.

    Returns:
        Dict with counts for each env's missing keys and total mismatches.
    """
    summary: Dict[str, int] = {
        f"missing_in_{env}": len(keys)
        for env, keys in diff.missing.items()
    }
    summary["mismatches"] = len(diff.mismatches)
    return summary
