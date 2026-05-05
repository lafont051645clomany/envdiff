"""Export diff results to various file formats (JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.masker import mask_env

EXPORT_FORMATS = ("json", "csv", "markdown")


def export_diff(
    diff: DiffResult,
    fmt: str,
    mask_secrets: bool = False,
    custom_mask: str = "****",
) -> str:
    """Export a DiffResult to the given format string."""
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {fmt!r}. Choose from {EXPORT_FORMATS}.")

    if mask_secrets:
        diff = DiffResult(
            missing_in={
                env: mask_env(keys) for env, keys in diff.missing_in.items()
            },
            mismatches={
                key: {env: mask_env({key: val})[key] for env, val in envs.items()}
                for key, envs in diff.mismatches.items()
            },
        )

    if fmt == "json":
        return _export_json(diff)
    if fmt == "csv":
        return _export_csv(diff)
    return _export_markdown(diff)


def _export_json(diff: DiffResult) -> str:
    data = {
        "missing_in": diff.missing_in,
        "mismatches": diff.mismatches,
    }
    return json.dumps(data, indent=2)


def _export_csv(diff: DiffResult) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["type", "key", "environment", "value"])

    for env, keys in diff.missing_in.items():
        for key, value in keys.items():
            writer.writerow(["missing", key, env, value])

    for key, envs in diff.mismatches.items():
        for env, value in envs.items():
            writer.writerow(["mismatch", key, env, value])

    return output.getvalue()


def _export_markdown(diff: DiffResult) -> str:
    lines = ["# Env Diff Report", ""]

    if diff.missing_in:
        lines.append("## Missing Keys")
        lines.append("| Key | Missing In |")
        lines.append("|-----|-----------|")
        for env, keys in diff.missing_in.items():
            for key in keys:
                lines.append(f"| `{key}` | `{env}` |")
        lines.append("")

    if diff.mismatches:
        lines.append("## Mismatched Values")
        lines.append("| Key | Environment | Value |")
        lines.append("|-----|------------|-------|")
        for key, envs in diff.mismatches.items():
            for env, value in envs.items():
                lines.append(f"| `{key}` | `{env}` | `{value}` |")
        lines.append("")

    if not diff.missing_in and not diff.mismatches:
        lines.append("_No differences found._")

    return "\n".join(lines)
