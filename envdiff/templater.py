"""Generate .env.example templates from existing env files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.masker import is_secret_key


@dataclass
class TemplateEntry:
    key: str
    placeholder: str
    comment: Optional[str] = None
    is_secret: bool = False


@dataclass
class EnvTemplate:
    entries: List[TemplateEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, str]:
        return {e.key: e.placeholder for e in self.entries}


def _make_placeholder(key: str, is_secret: bool) -> str:
    """Return a placeholder string appropriate for the key."""
    if is_secret:
        return "<secret>"
    return f"<{key.lower()}>"


def build_template(
    env: Dict[str, str],
    include_comments: bool = True,
) -> EnvTemplate:
    """Build a template from a parsed env dict, replacing values with placeholders."""
    entries: List[TemplateEntry] = []
    for key, _value in sorted(env.items()):
        secret = is_secret_key(key)
        placeholder = _make_placeholder(key, secret)
        comment = "# secret" if (include_comments and secret) else None
        entries.append(
            TemplateEntry(key=key, placeholder=placeholder, comment=comment, is_secret=secret)
        )
    return EnvTemplate(entries=entries)


def render_template(template: EnvTemplate) -> str:
    """Render an EnvTemplate to a .env.example string."""
    lines: List[str] = []
    for entry in template.entries:
        if entry.comment:
            lines.append(entry.comment)
        lines.append(f"{entry.key}={entry.placeholder}")
    return "\n".join(lines) + "\n" if lines else ""


def generate_example(
    env: Dict[str, str],
    include_comments: bool = True,
) -> str:
    """Convenience: build and render a template in one step."""
    template = build_template(env, include_comments=include_comments)
    return render_template(template)
