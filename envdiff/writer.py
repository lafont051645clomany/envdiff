"""Write exported diff content to files or stdout."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult
from envdiff.exporter import export_diff

_EXTENSIONS = {
    "json": ".json",
    "csv": ".csv",
    "markdown": ".md",
}


def write_diff(
    diff: DiffResult,
    fmt: str,
    output_path: Optional[str] = None,
    mask_secrets: bool = False,
    custom_mask: str = "****",
) -> None:
    """Export diff and write to *output_path* or stdout.

    Parameters
    ----------
    diff:
        The DiffResult to export.
    fmt:
        Export format — one of ``json``, ``csv``, ``markdown``.
    output_path:
        Destination file path. If *None* the content is written to stdout.
    mask_secrets:
        Whether to mask secret-looking values before writing.
    custom_mask:
        Replacement string used when masking.
    """
    content = export_diff(diff, fmt, mask_secrets=mask_secrets, custom_mask=custom_mask)

    if output_path is None:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
        return

    path = Path(output_path)
    _ensure_parent(path)
    path.write_text(content, encoding="utf-8")


def suggest_filename(base: str, fmt: str) -> str:
    """Return a suggested output filename for *base* and *fmt*.

    >>> suggest_filename("report", "json")
    'report.json'
    """
    ext = _EXTENSIONS.get(fmt, f".{fmt}")
    return f"{base}{ext}"


def _ensure_parent(path: Path) -> None:
    """Create parent directories for *path* if they do not exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
