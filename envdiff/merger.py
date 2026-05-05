"""Merge multiple .env files into a single unified environment dict.

Later files take precedence over earlier ones unless a key is marked
as protected, in which case the first-seen value wins.
"""

from typing import Dict, List, Optional, Set

EnvDict = Dict[str, str]


def merge_envs(
    envs: List[EnvDict],
    protected_keys: Optional[Set[str]] = None,
) -> EnvDict:
    """Merge a list of env dicts left-to-right.

    Args:
        envs: Ordered list of env dicts.  Later entries override earlier ones.
        protected_keys: Keys whose first-seen value is preserved (no override).

    Returns:
        A single merged env dict.
    """
    if protected_keys is None:
        protected_keys = set()

    merged: EnvDict = {}
    for env in envs:
        for key, value in env.items():
            if key in protected_keys and key in merged:
                continue
            merged[key] = value
    return merged


def merge_with_sources(
    envs: List[EnvDict],
    labels: Optional[List[str]] = None,
) -> Dict[str, Dict[str, str]]:
    """Return a mapping of key -> {value, source} showing where each key came from.

    When multiple envs define the same key the last one wins (same semantics as
    :func:`merge_envs`).  The *source* field records the label of the winning env.

    Args:
        envs: Ordered list of env dicts.
        labels: Optional human-readable labels for each env (e.g. filenames).

    Returns:
        Dict mapping each key to a dict with ``value`` and ``source``.
    """
    if labels is None:
        labels = [f"env{i}" for i in range(len(envs))]

    if len(labels) != len(envs):
        raise ValueError("labels length must match envs length")

    result: Dict[str, Dict[str, str]] = {}
    for label, env in zip(labels, envs):
        for key, value in env.items():
            result[key] = {"value": value, "source": label}
    return result


def collect_all_keys(envs: List[EnvDict]) -> Set[str]:
    """Return the union of all keys across every env dict."""
    keys: Set[str] = set()
    for env in envs:
        keys.update(env.keys())
    return keys
