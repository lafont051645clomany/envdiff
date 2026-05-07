"""CLI subcommand: tag env keys with auto-detected or custom labels."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from envdiff.parser import load_env_files
from envdiff.tagger import tag_env, TagReport


def add_tag_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "tag",
        help="Tag env keys by category (database, auth, network, …)",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to tag")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--show-untagged",
        action="store_true",
        help="Also list keys that could not be tagged",
    )
    parser.set_defaults(func=run_tag)


def _format_text(report: TagReport, label: str, show_untagged: bool) -> str:
    lines = [f"Tags for {label}:"]
    if not report.all_tags() and not report.untagged:
        lines.append("  (no keys)")
        return "\n".join(lines)
    for tag in report.all_tags():
        keys = report.keys_for(tag)
        lines.append(f"  [{tag}] ({len(keys)} keys)")
        for k in keys:
            lines.append(f"    - {k}")
    if show_untagged and report.untagged:
        lines.append(f"  [untagged] ({len(report.untagged)} keys)")
        for k in report.untagged:
            lines.append(f"    - {k}")
    return "\n".join(lines)


def run_tag(args: argparse.Namespace) -> None:
    try:
        envs = load_env_files(args.files)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.fmt == "json":
        output = {}
        for label, env in zip(args.files, envs.values()):
            report = tag_env(env)
            output[label] = {
                "tags": report.tags,
                "untagged": report.untagged,
            }
        print(json.dumps(output, indent=2))
    else:
        for label, env in zip(args.files, envs.values()):
            report = tag_env(env)
            print(_format_text(report, label, args.show_untagged))
            print()
