"""CLI subcommand for computing the health score of a .env file."""

import argparse
import json
import sys

from envdiff.auditor import audit_env
from envdiff.linter import lint_file
from envdiff.parser import parse_env_file
from envdiff.profiler import profile_env
from envdiff.scorer import compute_health_score


def add_score_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "score",
        help="Compute a health score for a .env file.",
    )
    parser.add_argument("env_file", help="Path to the .env file to score.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--fail-under",
        type=float,
        default=0.0,
        metavar="SCORE",
        help="Exit with code 1 if total score is below this threshold.",
    )
    parser.set_defaults(func=run_score)


def run_score(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.env_file}", file=sys.stderr)
        return 2

    audit = audit_env(env)
    lint = lint_file(args.env_file)
    profile = profile_env(env)
    health = compute_health_score(audit, lint, profile)

    if args.output_format == "json":
        output = {
            "file": args.env_file,
            "total": health.total,
            "grade": health.grade,
            "breakdown": health.breakdown,
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Health Score for: {args.env_file}")
        print(f"  Total : {health.total:.1f} / 100  [{health.grade}]")
        print(f"  Audit : {health.breakdown.get('audit', 0):.1f} / 40")
        print(f"  Lint  : {health.breakdown.get('lint', 0):.1f} / 30")
        print(f"  Profile: {health.breakdown.get('profile', 0):.1f} / 30")

    if health.total < args.fail_under:
        return 1
    return 0
