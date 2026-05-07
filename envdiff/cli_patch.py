"""CLI subcommand: envdiff patch — show patch suggestions between two env files."""

from __future__ import annotations

import argparse
import json
import sys

from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_file
from envdiff.patcher import PatchReport, build_patch, patch_to_dict


def add_patch_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "patch",
        help="Show patch suggestions to bring target in line with source.",
    )
    p.add_argument("source", help="Reference .env file (source of truth).")
    p.add_argument("target", help="Target .env file to patch.")
    p.add_argument(
        "--removals",
        action="store_true",
        default=False,
        help="Also suggest removing keys absent from source.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    p.set_defaults(func=run_patch)


def _format_text(report: PatchReport) -> str:
    if not report.has_patches:
        return "No patches needed — environments are in sync."
    lines = [
        f"Patch: {report.source_label} -> {report.target_label}",
        f"  {report.count} suggestion(s):",
        "",
    ]
    for entry in report.entries:
        lines.append(f"  {entry.label}")
    return "\n".join(lines)


def run_patch(args: argparse.Namespace) -> int:
    try:
        source_env = parse_env_file(args.source)
        target_env = parse_env_file(args.target)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    diff = compare_envs(source_env, target_env)
    report = build_patch(
        diff,
        source_label=args.source,
        target_label=args.target,
        include_removals=args.removals,
    )

    if args.fmt == "json":
        print(json.dumps(patch_to_dict(report), indent=2))
    else:
        print(_format_text(report))

    return 1 if report.has_patches else 0
