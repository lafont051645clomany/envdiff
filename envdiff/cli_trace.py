"""CLI subcommand: trace — show where each key originates across environments."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from envdiff.parser import load_env_files
from envdiff.tracer import TraceReport, trace_all


def add_trace_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "trace",
        help="Trace where each key comes from across multiple .env files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Named env files (name=path)")
    p.add_argument(
        "--inconsistent-only",
        action="store_true",
        help="Show only keys whose values differ across environments.",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    p.set_defaults(func=run_trace)


def _parse_named_files(raw: List[str]) -> dict[str, str]:
    """Parse 'name=path' pairs into a mapping."""
    result: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            print(f"error: expected name=path, got '{item}'", file=sys.stderr)
            sys.exit(2)
        name, _, path = item.partition("=")
        result[name.strip()] = path.strip()
    return result


def _text_output(report: TraceReport, inconsistent_only: bool) -> str:
    lines: List[str] = []
    keys = report.inconsistent_keys if inconsistent_only else sorted(report.traces)
    for key in keys:
        trace = report.traces[key]
        status = "DIFF" if not trace.is_consistent else "OK  "
        lines.append(f"[{status}] {key}")
        for env_name in report.env_names:
            val = trace.origins.get(env_name)
            display = repr(val) if val is not None else "<missing>"
            lines.append(f"       {env_name}: {display}")
    return "\n".join(lines)


def _json_output(report: TraceReport, inconsistent_only: bool) -> str:
    keys = report.inconsistent_keys if inconsistent_only else sorted(report.traces)
    data = {
        "env_names": report.env_names,
        "keys": {
            k: {
                "consistent": report.traces[k].is_consistent,
                "origins": report.traces[k].origins,
            }
            for k in keys
        },
    }
    return json.dumps(data, indent=2)


def run_trace(args: argparse.Namespace) -> None:
    named = _parse_named_files(args.files)
    paths = list(named.values())
    labels = list(named.keys())

    raw_envs = load_env_files(paths)
    envs = dict(zip(labels, raw_envs))

    report = trace_all(envs)

    if args.format == "json":
        print(_json_output(report, args.inconsistent_only))
    else:
        output = _text_output(report, args.inconsistent_only)
        print(output if output else "All keys are consistent across environments.")
