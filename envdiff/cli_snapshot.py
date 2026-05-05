"""CLI sub-commands for snapshot management: save and diff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.snapshot import save_snapshot, diff_against_snapshot


def add_snapshot_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'snapshot' sub-command group."""
    snap_parser = subparsers.add_parser(
        "snapshot", help="Save or diff .env snapshots for drift detection."
    )
    snap_sub = snap_parser.add_subparsers(dest="snapshot_cmd", required=True)

    # snapshot save
    save_p = snap_sub.add_parser("save", help="Save current .env as a snapshot.")
    save_p.add_argument("env_file", help="Path to the .env file to snapshot.")
    save_p.add_argument("output", help="Destination snapshot JSON file.")
    save_p.add_argument("--label", default="", help="Optional label for this snapshot.")

    # snapshot diff
    diff_p = snap_sub.add_parser("diff", help="Compare a .env file against a snapshot.")
    diff_p.add_argument("env_file", help="Path to the current .env file.")
    diff_p.add_argument("snapshot", help="Path to the snapshot JSON file.")
    diff_p.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Exit with code 1 if any drift is detected.",
    )


def run_snapshot(args: argparse.Namespace) -> int:
    """Execute the snapshot sub-command; return exit code."""
    if args.snapshot_cmd == "save":
        return _run_save(args)
    if args.snapshot_cmd == "diff":
        return _run_diff(args)
    print(f"Unknown snapshot command: {args.snapshot_cmd}", file=sys.stderr)
    return 2


def _run_save(args: argparse.Namespace) -> int:
    try:
        env = parse_env_file(args.env_file)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    dest = save_snapshot(env, args.output, label=args.label)
    print(f"Snapshot saved to {dest}")
    return 0


def _run_diff(args: argparse.Namespace) -> int:
    try:
        current_env = parse_env_file(args.env_file)
    except FileNotFoundError as exc:
        print(f"Error reading env file: {exc}", file=sys.stderr)
        return 2
    try:
        changes = diff_against_snapshot(current_env, args.snapshot)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error loading snapshot: {exc}", file=sys.stderr)
        return 2

    if not changes:
        print("No drift detected.")
        return 0

    print(f"Drift detected ({len(changes)} key(s) changed):")
    for key, vals in changes.items():
        snap_val = vals["snapshot"] if vals["snapshot"] is not None else "<missing>"
        curr_val = vals["current"] if vals["current"] is not None else "<missing>"
        print(f"  {key}: snapshot={snap_val!r}  current={curr_val!r}")

    return 1 if args.fail_on_drift else 0
