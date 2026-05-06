"""CLI subcommand: classify — show key categories for one or more .env files."""

from __future__ import annotations

import argparse
import json
from typing import List

from envdiff.parser import load_env_files
from envdiff.classifier import classify_all, ClassifyReport


def add_classify_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "classify",
        help="Classify .env keys by category (database, auth, network, …)",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to classify",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--category",
        metavar="CAT",
        default=None,
        help="Only show keys belonging to this category",
    )
    parser.set_defaults(func=run_classify)


def _format_text(name: str, report: ClassifyReport, only_cat: str | None) -> str:
    lines: List[str] = [f"=== {name} ==="]
    cats = [only_cat] if only_cat else report.all_categories()
    for cat in cats:
        keys = report.keys_in(cat)
        if not keys:
            continue
        lines.append(f"  [{cat}]")
        for k in keys:
            lines.append(f"    {k}")
    return "\n".join(lines)


def run_classify(args: argparse.Namespace) -> None:
    envs = load_env_files(args.files)
    reports = classify_all(envs)

    if args.fmt == "json":
        out = {}
        for name, report in reports.items():
            if args.category:
                out[name] = {args.category: report.keys_in(args.category)}
            else:
                out[name] = {cat: report.keys_in(cat) for cat in report.all_categories()}
        print(json.dumps(out, indent=2))
    else:
        for name, report in reports.items():
            print(_format_text(name, report, args.category))
            print()
