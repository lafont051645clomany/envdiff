"""CLI subcommand: envdiff rename — detect likely key renames between two env files."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.comparator import compare_envs
from envdiff.parser import load_env_files
from envdiff.renamer import detect_renames, format_rename_report


def add_rename_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser(
        "rename",
        help="Detect likely key renames between two .env files.",
    )
    parser.add_argument("base", help="Base .env file (old)")
    parser.add_argument("other", help="Other .env file (new)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        metavar="FLOAT",
        help="Minimum similarity score 0.0-1.0 (default: 0.70)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--fail-on-candidates",
        action="store_true",
        help="Exit with code 1 when rename candidates are found.",
    )
    parser.set_defaults(func=run_rename)


def run_rename(args: argparse.Namespace) -> int:
    """Execute the rename subcommand and return an exit code."""
    envs = load_env_files([args.base, args.other])
    base_env = envs[args.base]
    other_env = envs[args.other]

    diff = compare_envs(base_env, other_env)
    report = detect_renames(diff, threshold=args.threshold)

    if args.output_format == "json":
        payload = [
            {"old_key": c.old_key, "new_key": c.new_key, "score": round(c.score, 4)}
            for c in report.candidates
        ]
        print(json.dumps(payload, indent=2))
    else:
        print(format_rename_report(report, threshold=args.threshold))

    if args.fail_on_candidates and report.has_candidates:
        return 1
    return 0
