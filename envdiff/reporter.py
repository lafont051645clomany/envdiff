"""Formats and outputs diff results for human-readable or machine-readable consumption."""

from __future__ import annotations

from typing import Dict, List, Optional

from envdiff.comparator import DiffResult
from envdiff.masker import mask_env


def format_report(
    diff: DiffResult,
    env_names: List[str],
    mask_secrets: bool = False,
    raw_envs: Optional[List[Dict[str, str]]] = None,
    output_format: str = "text",
) -> str:
    """Generate a formatted report from a DiffResult.

    Args:
        diff: The DiffResult produced by compare_envs.
        env_names: Labels for each environment (e.g. ["dev", "prod"]).
        mask_secrets: If True, mask secret values in the output.
        raw_envs: The original env dicts (required when mask_secrets=True).
        output_format: "text" or "json".

    Returns:
        A formatted string report.
    """
    if output_format == "json":
        return _format_json(diff, env_names, mask_secrets, raw_envs)
    return _format_text(diff, env_names, mask_secrets, raw_envs)


def _resolve_envs(
    raw_envs: Optional[List[Dict[str, str]]],
    mask_secrets: bool,
) -> Optional[List[Dict[str, str]]]:
    if not mask_secrets or raw_envs is None:
        return raw_envs
    return [mask_env(env) for env in raw_envs]


def _format_text(
    diff: DiffResult,
    env_names: List[str],
    mask_secrets: bool,
    raw_envs: Optional[List[Dict[str, str]]],
) -> str:
    envs = _resolve_envs(raw_envs, mask_secrets)
    lines: List[str] = []

    if diff.missing_keys:
        lines.append("=== Missing Keys ===")
        for key, absent_in in sorted(diff.missing_keys.items()):
            missing_labels = [env_names[i] for i in absent_in]
            lines.append(f"  {key}: missing in [{', '.join(missing_labels)}]")

    if diff.mismatched_keys:
        lines.append("=== Mismatched Values ===")
        for key, values in sorted(diff.mismatched_keys.items()):
            parts = []
            for i, val in enumerate(values):
                display = val
                if envs is not None and i < len(envs):
                    display = envs[i].get(key, val)
                label = env_names[i] if i < len(env_names) else str(i)
                parts.append(f"{label}={display!r}")
            lines.append(f"  {key}: {', '.join(parts)}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def _format_json(
    diff: DiffResult,
    env_names: List[str],
    mask_secrets: bool,
    raw_envs: Optional[List[Dict[str, str]]],
) -> str:
    import json

    envs = _resolve_envs(raw_envs, mask_secrets)
    report: dict = {"missing_keys": {}, "mismatched_keys": {}}

    for key, absent_in in diff.missing_keys.items():
        report["missing_keys"][key] = [env_names[i] for i in absent_in]

    for key, values in diff.mismatched_keys.items():
        entry = {}
        for i, val in enumerate(values):
            display = val
            if envs is not None and i < len(envs):
                display = envs[i].get(key, val)
            label = env_names[i] if i < len(env_names) else str(i)
            entry[label] = display
        report["mismatched_keys"][key] = entry

    return json.dumps(report, indent=2)
