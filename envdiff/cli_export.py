"""CLI helpers for the ``envdiff export`` sub-command."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envdiff.comparator import compare_envs
from envdiff.exporter import EXPORT_FORMATS
from envdiff.parser import load_env_files
from envdiff.writer import suggest_filename, write_diff


def add_export_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *export* subcommand on *subparsers*."""
    parser = subparsers.add_parser(
        "export",
        help="Export diff results to a file or stdout.",
    )
    parser.add_argument(
        "envfiles",
        nargs="+",
        metavar="FILE",
        help="Two or more .env files to compare.",
    )
    parser.add_argument(
        "--format",
        "-f",
        dest="fmt",
        choices=EXPORT_FORMATS,
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        default=None,
        metavar="PATH",
        help="Destination file. Omit to write to stdout.",
    )
    parser.add_argument(
        "--mask-secrets",
        action="store_true",
        default=False,
        help="Mask secret-looking values in the export.",
    )
    parser.add_argument(
        "--suggest-filename",
        action="store_true",
        default=False,
        help="Print a suggested output filename and exit.",
    )
    parser.set_defaults(func=run_export)


def run_export(args: argparse.Namespace) -> int:
    """Execute the export subcommand. Returns an exit code."""
    if args.suggest_filename:
        print(suggest_filename("envdiff_report", args.fmt))
        return 0

    if len(args.envfiles) < 2:
        print("error: at least two env files are required.", file=sys.stderr)
        return 2

    try:
        envs = load_env_files(args.envfiles)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    diff = compare_envs(envs)

    try:
        write_diff(
            diff,
            fmt=args.fmt,
            output_path=args.output,
            mask_secrets=args.mask_secrets,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0
