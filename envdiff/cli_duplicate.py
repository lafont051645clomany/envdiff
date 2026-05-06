"""CLI subcommand: detect duplicate values in env files."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.duplicator import find_duplicates_all
from envdiff.parser import load_env_files


def add_duplicate_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "duplicates",
        help="Detect keys that share the same value within each env file.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env files to scan")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on-duplicates",
        action="store_true",
        help="Exit with code 1 if any duplicates are found",
    )
    parser.set_defaults(func=run_duplicate)


def run_duplicate(args: argparse.Namespace) -> int:
    envs = load_env_files(args.files)
    reports = find_duplicates_all(envs)

    any_duplicates = any(r.has_duplicates for r in reports.values())

    if args.fmt == "json":
        output = {
            name: [
                {"value": g.value, "keys": g.keys}
                for g in report.groups
            ]
            for name, report in reports.items()
        }
        print(json.dumps(output, indent=2))
    else:
        for name, report in reports.items():
            if not report.has_duplicates:
                print(f"[{name}] No duplicate values found.")
                continue
            print(f"[{name}] {report.total_duplicate_keys} keys share duplicate values:")
            for group in report.groups:
                keys_str = ", ".join(group.keys)
                masked = group.value[:4] + "..." if len(group.value) > 4 else "..."
                print(f"  value={masked!r:>12}  keys: {keys_str}")

    if args.fail_on_duplicates and any_duplicates:
        return 1
    return 0
