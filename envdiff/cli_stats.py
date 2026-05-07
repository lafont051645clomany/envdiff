"""CLI sub-command: envdiff stats — show comparison statistics."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.comparator import compare_envs
from envdiff.comparator_stats import compute_stats, stats_to_dict
from envdiff.parser import load_env_files


def add_stats_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "stats",
        help="Print comparison statistics for two or more .env files.",
    )
    p.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help=".env files to compare (at least two).",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    p.add_argument(
        "--fail-below",
        type=float,
        default=None,
        metavar="RATIO",
        help="Exit with code 1 if health_ratio is below this threshold (0–1).",
    )
    p.set_defaults(func=run_stats)


def run_stats(args: argparse.Namespace) -> None:
    if len(args.files) < 2:
        print("error: at least two files are required.", file=sys.stderr)
        sys.exit(2)

    envs = load_env_files(args.files)
    env_names = args.files

    # Compare first env against merged union of all others
    base_name, *rest_names = env_names
    base_env = envs[base_name]

    # Merge remaining envs for comparison
    merged: dict = {}
    for name in rest_names:
        merged.update(envs[name])

    diff = compare_envs(base_env, merged)
    stats = compute_stats(diff, env_names)
    d = stats_to_dict(stats)

    if args.fmt == "json":
        print(json.dumps(d, indent=2))
    else:
        _print_text(d)

    if args.fail_below is not None and stats.health_ratio < args.fail_below:
        sys.exit(1)


def _print_text(d: dict) -> None:
    print(f"Total keys   : {d['total_keys']}")
    print(f"Matching     : {d['matching_count']}")
    print(f"Missing      : {d['missing_count']}")
    print(f"Mismatched   : {d['mismatch_count']}")
    print(f"Health ratio : {d['health_ratio']:.2%}")
    print(f"Environments : {', '.join(d['environments'])}")
