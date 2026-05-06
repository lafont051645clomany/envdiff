"""Classify .env keys by category based on naming conventions and value patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

# Category name constants
CAT_DATABASE = "database"
CAT_AUTH = "auth"
CAT_NETWORK = "network"
CAT_FEATURE_FLAG = "feature_flag"
CAT_LOGGING = "logging"
CAT_SECRET = "secret"
CAT_OTHER = "other"

_PREFIX_MAP: Dict[str, str] = {
    "DB_": CAT_DATABASE,
    "DATABASE_": CAT_DATABASE,
    "POSTGRES_": CAT_DATABASE,
    "MYSQL_": CAT_DATABASE,
    "REDIS_": CAT_DATABASE,
    "AUTH_": CAT_AUTH,
    "JWT_": CAT_AUTH,
    "OAUTH_": CAT_AUTH,
    "SECRET_": CAT_SECRET,
    "API_KEY": CAT_SECRET,
    "TOKEN": CAT_SECRET,
    "PASSWORD": CAT_SECRET,
    "HOST": CAT_NETWORK,
    "PORT": CAT_NETWORK,
    "URL": CAT_NETWORK,
    "ENDPOINT": CAT_NETWORK,
    "LOG_": CAT_LOGGING,
    "LOGGING_": CAT_LOGGING,
    "ENABLE_": CAT_FEATURE_FLAG,
    "DISABLE_": CAT_FEATURE_FLAG,
    "FEATURE_": CAT_FEATURE_FLAG,
    "FLAG_": CAT_FEATURE_FLAG,
}


@dataclass
class ClassifyReport:
    categories: Dict[str, List[str]] = field(default_factory=dict)

    def has_category(self, name: str) -> bool:
        return name in self.categories and bool(self.categories[name])

    def all_categories(self) -> List[str]:
        return sorted(self.categories.keys())

    def keys_in(self, category: str) -> List[str]:
        return list(self.categories.get(category, []))

    def total_keys(self) -> int:
        return sum(len(v) for v in self.categories.values())


def classify_key(key: str) -> str:
    """Return the category name for a single key."""
    upper = key.upper()
    for pattern, category in _PREFIX_MAP.items():
        if upper.startswith(pattern) or pattern in upper:
            return category
    return CAT_OTHER


def classify_env(env: Dict[str, str]) -> ClassifyReport:
    """Classify all keys in an env dict and return a ClassifyReport."""
    report: Dict[str, List[str]] = {}
    for key in env:
        cat = classify_key(key)
        report.setdefault(cat, []).append(key)
    for cat in report:
        report[cat].sort()
    return ClassifyReport(categories=report)


def classify_all(envs: Dict[str, Dict[str, str]]) -> Dict[str, ClassifyReport]:
    """Classify multiple named envs, returning a report per env name."""
    return {name: classify_env(env) for name, env in envs.items()}
