"""Secret masking utilities for envdiff."""

import re
from typing import Dict, Set

# Default patterns that indicate a value should be treated as a secret
DEFAULT_SECRET_PATTERNS = [
    re.compile(r".*SECRET.*", re.IGNORECASE),
    re.compile(r".*PASSWORD.*", re.IGNORECASE),
    re.compile(r".*PASSWD.*", re.IGNORECASE),
    re.compile(r".*TOKEN.*", re.IGNORECASE),
    re.compile(r".*API_KEY.*", re.IGNORECASE),
    re.compile(r".*PRIVATE_KEY.*", re.IGNORECASE),
    re.compile(r".*AUTH.*", re.IGNORECASE),
    re.compile(r".*CREDENTIAL.*", re.IGNORECASE),
]

MASK_VALUE = "***"


def is_secret_key(key: str, patterns: list = None) -> bool:
    """Return True if the key name matches any secret pattern."""
    patterns = patterns if patterns is not None else DEFAULT_SECRET_PATTERNS
    return any(pattern.match(key) for pattern in patterns)


def mask_value(value: str, mask: str = MASK_VALUE) -> str:
    """Return the mask string in place of the real value."""
    return mask


def mask_env(env: Dict[str, str], patterns: list = None, mask: str = MASK_VALUE) -> Dict[str, str]:
    """Return a copy of the env dict with secret values replaced by the mask."""
    return {
        key: (mask_value(value, mask) if is_secret_key(key, patterns) else value)
        for key, value in env.items()
    }


def get_secret_keys(env: Dict[str, str], patterns: list = None) -> Set[str]:
    """Return the set of keys in env that are considered secrets."""
    return {key for key in env if is_secret_key(key, patterns)}
