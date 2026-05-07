"""Pin current env values as a baseline for drift detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.masker import is_secret_key


@dataclass
class PinEntry:
    key: str
    value: str
    is_secret: bool = False

    @property
    def display_value(self) -> str:
        return "***" if self.is_secret else self.value


@dataclass
class PinReport:
    label: str
    pins: Dict[str, PinEntry] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.pins)

    @property
    def secret_count(self) -> int:
        return sum(1 for e in self.pins.values() if e.is_secret)

    def get(self, key: str) -> Optional[PinEntry]:
        return self.pins.get(key)


@dataclass
class DriftEntry:
    key: str
    pinned_value: str
    current_value: Optional[str]
    status: str  # "changed", "removed", "added"


@dataclass
class DriftReport:
    label: str
    drifted: List[DriftEntry] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return len(self.drifted) > 0

    @property
    def count(self) -> int:
        return len(self.drifted)


def pin_env(env: Dict[str, str], label: str = "pinned") -> PinReport:
    """Create a PinReport capturing the current state of an env."""
    report = PinReport(label=label)
    for key, value in env.items():
        report.pins[key] = PinEntry(
            key=key,
            value=value,
            is_secret=is_secret_key(key),
        )
    return report


def detect_drift(pin: PinReport, current: Dict[str, str]) -> DriftReport:
    """Compare a pinned baseline against a current env dict."""
    report = DriftReport(label=pin.label)

    for key, entry in pin.pins.items():
        if key not in current:
            report.drifted.append(
                DriftEntry(key=key, pinned_value=entry.value, current_value=None, status="removed")
            )
        elif current[key] != entry.value:
            report.drifted.append(
                DriftEntry(key=key, pinned_value=entry.value, current_value=current[key], status="changed")
            )

    for key, value in current.items():
        if key not in pin.pins:
            report.drifted.append(
                DriftEntry(key=key, pinned_value="", current_value=value, status="added")
            )

    return report
