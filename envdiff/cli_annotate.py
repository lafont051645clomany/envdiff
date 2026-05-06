"""CLI subcommand: annotate — display key annotations for one or more env files."""

import argparse
import json
from typing import List

from envdiff.annotator import annotate_all, Annotation
from envdiff.parser import load_env_files


def add_annotate_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "annotate",
        help="Annotate env file keys with type, secret, and empty metadata.",
    )
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to annotate.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="output_format",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--secrets-only",
        action="store_true",
        help="Show only keys flagged as secrets.",
    )
    parser.set_defaults(func=run_annotate)


def _format_text(annotations: dict, secrets_only: bool) -> str:
    lines: List[str] = []
    for source, anns in annotations.items():
        lines.append(f"[{source}]")
        filtered = [a for a in anns if not secrets_only or a.is_secret]
        if not filtered:
            lines.append("  (no matching keys)")
        for a in filtered:
            tags = ", ".join(a.tags) if a.tags else "—"
            lines.append(f"  {a.key:<30} type={a.type_hint:<10} tags=[{tags}]")
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_json(annotations: dict, secrets_only: bool) -> str:
    output = {}
    for source, anns in annotations.items():
        filtered = [a for a in anns if not secrets_only or a.is_secret]
        output[source] = [
            {
                "key": a.key,
                "type": a.type_hint,
                "is_secret": a.is_secret,
                "is_empty": a.is_empty,
                "tags": a.tags,
            }
            for a in filtered
        ]
    return json.dumps(output, indent=2)


def run_annotate(args: argparse.Namespace) -> int:
    try:
        envs = load_env_files(args.files)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1

    annotations = annotate_all(envs)

    if args.output_format == "json":
        print(_format_json(annotations, args.secrets_only))
    else:
        print(_format_text(annotations, args.secrets_only))

    return 0
