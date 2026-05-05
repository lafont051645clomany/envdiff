"""CLI subcommand: `envdiff diff` — show a unified diff between two env files."""

import argparse
import sys
from typing import List, Optional

from envdiff.parser import parse_env_file
from envdiff.masker import mask_env, get_secret_keys
from envdiff.differ import build_unified_diff, classify_keys, count_by_status


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"


def add_diff_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the `diff` subcommand onto an existing subparsers group."""
    parser = subparsers.add_parser(
        "diff",
        help="Show a unified diff between two .env files",
    )
    parser.add_argument("file_a", help="First .env file (base)")
    parser.add_argument("file_b", help="Second .env file (compare)")
    parser.add_argument(
        "--mask-secrets",
        action="store_true",
        default=False,
        help="Mask secret values before displaying",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    parser.set_defaults(func=run_diff)


def _colorize(line: str, no_color: bool) -> str:
    if no_color or not line:
        return line
    if line.startswith("+") and not line.startswith("++"):
        return f"{ANSI_GREEN}{line}{ANSI_RESET}"
    if line.startswith("-") and not line.startswith("--"):
        return f"{ANSI_RED}{line}{ANSI_RESET}"
    return line


def run_diff(args: argparse.Namespace) -> int:
    """Execute the diff subcommand. Returns an exit code."""
    try:
        env_a = parse_env_file(args.file_a)
        env_b = parse_env_file(args.file_b)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.mask_secrets:
        env_a = mask_env(env_a)
        env_b = mask_env(env_b)

    lines = build_unified_diff(
        env_a, env_b, label_a=args.file_a, label_b=args.file_b
    )
    for line in lines:
        print(_colorize(line, no_color=args.no_color))

    counts = count_by_status(classify_keys(env_a, env_b))
    summary = (
        f"\nSummary: +{counts['added']} added, "
        f"-{counts['removed']} removed, "
        f"~{counts['changed']} changed, "
        f"{counts['unchanged']} unchanged"
    )
    print(summary)

    has_diff = any(counts[k] > 0 for k in ("added", "removed", "changed"))
    return 1 if has_diff else 0
