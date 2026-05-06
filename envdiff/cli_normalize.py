"""CLI subcommand: normalize — show normalized values for one or more .env files."""

import argparse
import json
from typing import List

from envdiff.parser import load_env_files
from envdiff.normalizer import normalize_all


def add_normalize_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "normalize",
        help="Show normalized values for .env files and report changed keys.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to normalize.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--only-changes",
        action="store_true",
        help="Only show keys whose values were changed by normalization.",
    )
    parser.set_defaults(func=run_normalize)


def run_normalize(args: argparse.Namespace) -> int:
    envs = load_env_files(args.files)
    results = normalize_all(envs)

    if args.fmt == "json":
        output = {}
        for name, result in results.items():
            if args.only_changes:
                output[name] = {
                    k: {"before": v[0], "after": v[1]}
                    for k, v in result.changes.items()
                }
            else:
                output[name] = result.normalized
        print(json.dumps(output, indent=2))
        return 0

    # Text format
    for name, result in results.items():
        print(f"[{name}]")
        if args.only_changes:
            if not result.has_changes:
                print("  (no changes)")
            else:
                for key, (before, after) in sorted(result.changes.items()):
                    print(f"  {key}: {before!r} -> {after!r}")
        else:
            for key, value in sorted(result.normalized.items()):
                marker = "*" if key in result.changes else " "
                print(f"  {marker} {key}={value}")
        print()

    return 0
