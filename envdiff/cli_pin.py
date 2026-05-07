"""CLI subcommand: pin and drift detection."""

from __future__ import annotations

import argparse
import json
import sys

from envdiff.parser import parse_env_file
from envdiff.pinner import detect_drift, pin_env


def add_pin_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("pin", help="Detect drift against a pinned env baseline")
    parser.add_argument("baseline", help="Baseline .env file (the pinned reference)")
    parser.add_argument("current", help="Current .env file to compare against the pin")
    parser.add_argument("--label", default="baseline", help="Label for the pin report")
    parser.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    parser.add_argument("--exit-code", action="store_true", help="Exit 1 if drift is detected")


def _format_text(report) -> str:
    lines = [f"Drift report for: {report.label}"]
    if not report.has_drift:
        lines.append("  No drift detected.")
        return "\n".join(lines)

    for entry in sorted(report.drifted, key=lambda e: e.key):
        if entry.status == "changed":
            lines.append(f"  ~ {entry.key}  (pinned: {entry.pinned_value!r} -> now: {entry.current_value!r})")
        elif entry.status == "removed":
            lines.append(f"  - {entry.key}  (removed since pin)")
        elif entry.status == "added":
            lines.append(f"  + {entry.key}  (added since pin)")
    return "\n".join(lines)


def run_pin(args: argparse.Namespace) -> None:
    try:
        baseline_env = parse_env_file(args.baseline)
        current_env = parse_env_file(args.current)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    pin = pin_env(baseline_env, label=args.label)
    drift = detect_drift(pin, current_env)

    if args.fmt == "json":
        data = {
            "label": drift.label,
            "has_drift": drift.has_drift,
            "count": drift.count,
            "drifted": [
                {"key": e.key, "status": e.status, "pinned": e.pinned_value, "current": e.current_value}
                for e in drift.drifted
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(_format_text(drift))

    if args.exit_code and drift.has_drift:
        sys.exit(1)
