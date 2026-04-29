"""Parser module for reading and parsing .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_PATTERN = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)
COMMENT_PATTERN = re.compile(r'^\s*#')


def parse_env_file(filepath: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dictionary of key-value pairs.

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping environment variable names to their values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid lines.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {filepath}")

    env_vars: Dict[str, str] = {}

    with path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped or COMMENT_PATTERN.match(stripped):
                continue
            match = ENV_LINE_PATTERN.match(stripped)
            if not match:
                raise ValueError(
                    f"Invalid syntax at {filepath}:{lineno}: {line.rstrip()!r}"
                )
            key = match.group("key")
            value = _strip_quotes(match.group("value"))
            env_vars[key] = value

    return env_vars


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2:
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
    return value


def load_env_files(
    *filepaths: str | Path,
) -> Dict[str, Dict[str, str]]:
    """Load multiple .env files and return a mapping of filename to parsed vars.

    Args:
        *filepaths: One or more paths to .env files.

    Returns:
        Dictionary mapping file names to their parsed key-value pairs.
    """
    result: Dict[str, Dict[str, str]] = {}
    for fp in filepaths:
        name = Path(fp).name
        result[name] = parse_env_file(fp)
    return result
