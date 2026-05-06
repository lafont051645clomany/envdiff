"""CLI subcommand: generate .env.example from an env file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.templater import generate_example


def add_template_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "template",
        help="Generate a .env.example template from an env file.",
    )
    parser.add_argument(
        "env_file",
        help="Path to the source .env file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    parser.add_argument(
        "--no-comments",
        action="store_true",
        help="Omit inline comments (e.g. '# secret') from the output.",
    )
    parser.set_defaults(func=run_template)


def run_template(args: argparse.Namespace) -> int:
    env_path = Path(args.env_file)
    if not env_path.exists():
        print(f"Error: file not found: {env_path}", file=sys.stderr)
        return 1

    try:
        env = parse_env_file(env_path)
    except Exception as exc:  # noqa: BLE001
        print(f"Error parsing {env_path}: {exc}", file=sys.stderr)
        return 1

    include_comments = not args.no_comments
    rendered = generate_example(env, include_comments=include_comments)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"Template written to {out_path}")
    else:
        print(rendered, end="")

    return 0
