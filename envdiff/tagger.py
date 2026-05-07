"""Tag env keys with user-defined or auto-detected labels."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Default auto-tag rules: (tag_name, substring_patterns)
_DEFAULT_RULES: List[tuple[str, List[str]]] = [
    ("database", ["DB_", "DATABASE_", "POSTGRES", "MYSQL", "MONGO", "REDIS"]),
    ("auth", ["AUTH_", "JWT_", "TOKEN", "SECRET", "PASSWORD", "PASSWD"]),
    ("network", ["HOST", "PORT", "URL", "URI", "ENDPOINT", "ADDR"]),
    ("feature", ["FEATURE_", "FLAG_", "ENABLE_", "DISABLE_"]),
    ("logging", ["LOG_", "LOGGING_", "DEBUG", "VERBOSE"]),
]


@dataclass
class TagReport:
    """Mapping of tag -> list of matching keys."""
    tags: Dict[str, List[str]] = field(default_factory=dict)
    untagged: List[str] = field(default_factory=list)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags and len(self.tags[tag]) > 0

    def all_tags(self) -> List[str]:
        return sorted(self.tags.keys())

    def keys_for(self, tag: str) -> List[str]:
        return self.tags.get(tag, [])

    def total_tagged(self) -> int:
        return sum(len(v) for v in self.tags.values())


def _auto_tag_key(key: str, rules: List[tuple]) -> Optional[str]:
    """Return the first matching tag for a key, or None."""
    upper = key.upper()
    for tag, patterns in rules:
        if any(p in upper for p in patterns):
            return tag
    return None


def tag_env(
    env: Dict[str, str],
    custom_tags: Optional[Dict[str, List[str]]] = None,
    rules: Optional[List[tuple]] = None,
) -> TagReport:
    """Tag all keys in env using rules and optional custom tag overrides.

    Args:
        env: Parsed environment dict.
        custom_tags: Explicit {tag: [key, ...]} overrides applied first.
        rules: Auto-tag rules; defaults to _DEFAULT_RULES.
    """
    active_rules = rules if rules is not None else _DEFAULT_RULES
    report = TagReport()

    # Build reverse map from custom_tags: key -> tag
    explicit: Dict[str, str] = {}
    if custom_tags:
        for tag, keys in custom_tags.items():
            for k in keys:
                explicit[k] = tag

    for key in env:
        tag = explicit.get(key) or _auto_tag_key(key, active_rules)
        if tag:
            report.tags.setdefault(tag, []).append(key)
        else:
            report.untagged.append(key)

    # Sort keys within each tag for determinism
    for tag in report.tags:
        report.tags[tag].sort()
    report.untagged.sort()
    return report


def tag_all(
    envs: Dict[str, Dict[str, str]],
    custom_tags: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, TagReport]:
    """Apply tag_env to multiple named environments."""
    return {name: tag_env(env, custom_tags=custom_tags) for name, env in envs.items()}
