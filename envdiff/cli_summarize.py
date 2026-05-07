"""CLI subcommand: summarize — show statistics for one or more .env files."""

from __future__ import annotations

import argparse
import json
from typing import List

from envdiff.parser import load_env_files
from envdiff.summarizer import summarize_all, EnvSummary


def add_summarize_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "summarize",
        help="Display statistics for one or more .env files.",
    )
    parser.add_argument("files", nargs="+", help=".env files to summarize")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.set_defaults(func=run_summarize)


def _format_text(summaries: List[EnvSummary]) -> str:
    lines = []
    for s in summaries:
        lines.append(f"=== {s.label} ===")
        lines.append(f"  Total keys : {s.total_keys}")
        lines.append(f"  Secret keys: {s.secret_count}")
        lines.append(f"  Empty keys : {s.empty_count}")
        lines.append(f"  Plain keys : {s.plain_count}")
        if s.categories:
            lines.append("  Categories:")
            for cat, keys in sorted(s.categories.items()):
                lines.append(f"    {cat}: {len(keys)}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_json(summaries: List[EnvSummary]) -> str:
    data = [
        {
            "label": s.label,
            "total_keys": s.total_keys,
            "secret_count": s.secret_count,
            "empty_count": s.empty_count,
            "plain_count": s.plain_count,
            "categories": {k: len(v) for k, v in s.categories.items()},
        }
        for s in summaries
    ]
    return json.dumps(data, indent=2)


def run_summarize(args: argparse.Namespace) -> None:
    named_envs = load_env_files(args.files)
    summaries = summarize_all(named_envs)

    if args.fmt == "json":
        print(_format_json(summaries))
    else:
        print(_format_text(summaries))
