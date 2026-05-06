"""CLI sub-command: group — display env keys organised by prefix namespace."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.grouper import group_env
from envdiff.parser import load_env_files


def add_group_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "group",
        help="Group env keys by prefix namespace.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to analyse")
    parser.add_argument(
        "--delimiter",
        default="_",
        help="Key segment delimiter (default: '_')",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=2,
        dest="min_size",
        help="Minimum keys to form a group (default: 2)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.set_defaults(func=run_group)


def run_group(args: argparse.Namespace) -> int:
    envs = load_env_files(args.files)
    merged: dict[str, str] = {}
    for env in envs.values():
        merged.update(env)

    report = group_env(merged, delimiter=args.delimiter, min_group_size=args.min_size)

    if args.fmt == "json":
        data = {
            "groups": {
                prefix: group.keys for prefix, group in sorted(report.groups.items())
            },
            "ungrouped": report.ungrouped,
            "total_keys": report.total_keys,
        }
        print(json.dumps(data, indent=2))
        return 0

    # --- text output ---
    if not report.has_groups and not report.ungrouped:
        print("No keys found.")
        return 0

    for prefix, group in sorted(report.groups.items()):
        print(f"[{prefix}]  ({group.count} keys)")
        for key in group.keys:
            print(f"  {key}")

    if report.ungrouped:
        print("[ungrouped]")
        for key in report.ungrouped:
            print(f"  {key}")

    return 0
