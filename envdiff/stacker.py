"""Stack multiple .env files into a layered view showing value precedence."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class LayerEntry:
    """Represents a key's value at a specific layer."""
    key: str
    value: Optional[str]
    source: str
    overridden_by: Optional[str] = None

    @property
    def is_overridden(self) -> bool:
        return self.overridden_by is not None


@dataclass
class StackReport:
    """Result of stacking multiple env files."""
    layers: List[str]
    entries: Dict[str, List[LayerEntry]] = field(default_factory=dict)

    @property
    def all_keys(self) -> List[str]:
        return sorted(self.entries.keys())

    @property
    def overridden_keys(self) -> List[str]:
        return sorted(
            key for key, entries in self.entries.items()
            if any(e.is_overridden for e in entries)
        )

    def effective_value(self, key: str) -> Optional[str]:
        """Return the winning (last non-None) value for a key."""
        entries = self.entries.get(key, [])
        for entry in reversed(entries):
            if entry.value is not None:
                return entry.value
        return None

    def effective_source(self, key: str) -> Optional[str]:
        """Return the source that provides the effective value."""
        entries = self.entries.get(key, [])
        for entry in reversed(entries):
            if entry.value is not None:
                return entry.source
        return None


def stack_envs(named_envs: List[Tuple[str, Dict[str, str]]]) -> StackReport:
    """Stack named env dicts in order; later layers override earlier ones."""
    layer_names = [name for name, _ in named_envs]
    report = StackReport(layers=layer_names)

    all_keys: set = set()
    for _, env in named_envs:
        all_keys.update(env.keys())

    for key in all_keys:
        entries: List[LayerEntry] = []
        for name, env in named_envs:
            value = env.get(key)
            entries.append(LayerEntry(key=key, value=value, source=name))

        # Mark overridden entries
        last_source = None
        for entry in reversed(entries):
            if entry.value is not None:
                last_source = entry.source
                break

        for i, entry in enumerate(entries):
            if entry.value is not None and entry.source != last_source:
                entry.overridden_by = last_source

        report.entries[key] = entries

    return report
