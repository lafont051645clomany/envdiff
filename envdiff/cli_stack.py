"""CLI subcommand: stack — show layered precedence across multiple .env files."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.parser import parse_env_file
from envdiff.stacker import StackReport, stack_envs


def add_stack_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "stack",
        help="Show layered value precedence across multiple .env files.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="NAME=FILE",
        help="Named env files in order of precedence, e.g. base=.env.base app=.env",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--overridden-only",
        action="store_true",
        help="Show only keys that are overridden by a later layer.",
    )
    parser.set_defaults(func=run_stack)


def _parse_named_files(args_files: List[str]) -> List[tuple]:
    named: list = []
    for token in args_files:
        if "=" not in token:
            print(f"error: expected NAME=FILE, got '{token}'", file=sys.stderr)
            sys.exit(2)
        name, path = token.split("=", 1)
        named.append((name.strip(), path.strip()))
    return named


def _format_text(report: StackReport, overridden_only: bool) -> str:
    lines: List[str] = []
    lines.append(f"Layers: {' → '.join(report.layers)}\n")
    keys = report.overridden_keys if overridden_only else report.all_keys
    if not keys:
        lines.append("  (no keys to display)")
        return "\n".join(lines)
    for key in keys:
        effective = report.effective_value(key)
        source = report.effective_source(key)
        lines.append(f"  {key}")
        lines.append(f"    effective: {effective!r}  [from {source}]")
        for entry in report.entries[key]:
            tag = " ← overridden" if entry.is_overridden else ""
            val = repr(entry.value) if entry.value is not None else "(missing)"
            lines.append(f"    {entry.source}: {val}{tag}")
    return "\n".join(lines)


def run_stack(args: argparse.Namespace) -> None:
    named_files = _parse_named_files(args.files)
    named_envs = []
    for name, path in named_files:
        try:
            named_envs.append((name, parse_env_file(path)))
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            sys.exit(2)

    report = stack_envs(named_envs)
    overridden_only = getattr(args, "overridden_only", False)

    if args.format == "json":
        out = {
            "layers": report.layers,
            "keys": {
                key: {
                    "effective_value": report.effective_value(key),
                    "effective_source": report.effective_source(key),
                    "layers": [
                        {"source": e.source, "value": e.value, "overridden_by": e.overridden_by}
                        for e in report.entries[key]
                    ],
                }
                for key in (report.overridden_keys if overridden_only else report.all_keys)
            },
        }
        print(json.dumps(out, indent=2))
    else:
        print(_format_text(report, overridden_only))
