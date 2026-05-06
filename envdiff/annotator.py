"""Annotate env file keys with metadata such as source, status, and type hints."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.masker import is_secret_key


@dataclass
class Annotation:
    key: str
    value: Optional[str]
    source: str
    is_secret: bool = False
    is_empty: bool = False
    type_hint: str = "string"
    tags: List[str] = field(default_factory=list)


def _infer_type(value: Optional[str]) -> str:
    """Infer a simple type hint from the value string."""
    if value is None:
        return "null"
    if value.lower() in ("true", "false"):
        return "boolean"
    try:
        int(value)
        return "integer"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    if "," in value:
        return "list"
    return "string"


def annotate_env(env: Dict[str, str], source: str) -> List[Annotation]:
    """Return a list of Annotation objects for each key in the env dict."""
    annotations = []
    for key, value in env.items():
        secret = is_secret_key(key)
        empty = value.strip() == ""
        type_hint = _infer_type(value)
        tags: List[str] = []
        if secret:
            tags.append("secret")
        if empty:
            tags.append("empty")
        if type_hint != "string":
            tags.append(type_hint)
        annotations.append(
            Annotation(
                key=key,
                value=value,
                source=source,
                is_secret=secret,
                is_empty=empty,
                type_hint=type_hint,
                tags=tags,
            )
        )
    return annotations


def annotate_all(
    envs: Dict[str, Dict[str, str]]
) -> Dict[str, List[Annotation]]:
    """Annotate all envs, keyed by their environment name."""
    return {name: annotate_env(env, source=name) for name, env in envs.items()}
