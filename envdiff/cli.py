"""Command-line interface for envdiff."""

import argparse
import sys
from typing import List, Optional

from envdiff.comparator import compare_envs, has_differences
from envdiff.masker import mask_env
from envdiff.parser import load_env_files
from envdiff.reporter import format_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and flag missing or mismatched keys.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare (e.g. .env.dev .env.prod).",
    )
    parser.add_argument(
        "--mask-secrets",
        action="store_true",
        default=False,
        help="Mask secret values before displaying them.",
    )
    parser.add_argument(
        "--mask-pattern",
        metavar="PATTERN",
        default=None,
        help="Custom regex pattern to identify secret keys (overrides default).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format: 'text' (default) or 'json'.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found.",
    )
    return parser


def run(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if len(args.files) < 2:
        parser.error("At least two .env files are required for comparison.")

    try:
        envs = load_env_files(args.files)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.mask_secrets:
        envs = {
            name: mask_env(data, pattern=args.mask_pattern)
            for name, data in envs.items()
        }

    diff = compare_envs(envs)
    report = format_report(diff, envs, fmt=args.output_format)
    print(report)

    if args.exit_code and has_differences(diff):
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
