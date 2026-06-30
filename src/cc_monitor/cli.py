"""Command-line entry point for cc-monitor.

Invoked by Claude Code hooks. Reads the hook's JSON payload from stdin
(for cwd) and brings the terminal window to the front.

Usage:
    cc-monitor focus            # bring the matching iTerm window forward

Typically wired to the Notification (needs input) and Stop (task done)
events. The process always exits 0 so a scripting failure never interrupts
Claude Code.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .config import Config
from .focus import focus


def _read_hook_payload() -> dict:
    """Read the hook JSON from stdin if present; return {} otherwise."""
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cc-monitor",
        description="Bring the iTerm window running Claude Code to the front.",
    )
    p.add_argument(
        "action",
        nargs="?",
        default="focus",
        choices=["focus"],
        help="Action to perform (default: focus).",
    )
    p.add_argument("--config", default=None, help="Path to a config JSON file.")
    p.add_argument("--version", action="version",
                   version=f"cc-monitor {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = Config.load(args.config)

    payload = _read_hook_payload()
    cwd = payload.get("cwd")

    focus(cwd, cfg)
    return 0


def run() -> None:
    try:
        code = main()
    except Exception as e:  # noqa: BLE001 — never block Claude Code
        sys.stderr.write(f"[cc-monitor] unexpected error: {e}\n")
        # By default we swallow the error (exit 0) so a scripting failure never
        # interrupts Claude Code. Setting never_block=false opts into surfacing
        # failures with a non-zero exit, which is handy when debugging.
        try:
            never_block = Config.load().never_block
        except Exception:  # noqa: BLE001 — config load must not block either
            never_block = True
        code = 0 if never_block else 1
    sys.exit(code)


if __name__ == "__main__":
    run()
