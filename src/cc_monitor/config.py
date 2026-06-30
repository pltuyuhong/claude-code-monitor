"""Configuration loading for cc_monitor.

Resolution order (highest priority first):
  1. Environment variables (CC_MONITOR_*)
  2. Config file (JSON), located via CC_MONITOR_CONFIG or default paths
  3. Built-in defaults

The config file is optional; everything has a sensible default.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_PATHS = [
    Path.home() / ".config" / "cc-monitor" / "config.json",
    Path.home() / ".cc-monitor.json",
]


@dataclass
class Config:
    # Whether to bring the terminal to the front at all.
    focus_enabled: bool = True
    # Which app to focus: "iTerm" or "Terminal".
    terminal_app: str = "iTerm"
    # If True, failures never raise (the CLI always exits 0). Recommended.
    never_block: bool = True

    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | os.PathLike | None = None) -> "Config":
        data: dict[str, Any] = {}

        candidate = None
        if path:
            candidate = Path(path)
        elif os.environ.get("CC_MONITOR_CONFIG"):
            candidate = Path(os.environ["CC_MONITOR_CONFIG"])
        else:
            for p in DEFAULT_CONFIG_PATHS:
                if p.is_file():
                    candidate = p
                    break

        if candidate and candidate.is_file():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                data = {}

        cfg = cls(raw=data)
        cfg.focus_enabled = bool(data.get("focus_enabled", cfg.focus_enabled))
        cfg.terminal_app = str(data.get("terminal_app", cfg.terminal_app))
        cfg.never_block = bool(data.get("never_block", cfg.never_block))

        env = os.environ
        if "CC_MONITOR_FOCUS_ENABLED" in env:
            cfg.focus_enabled = _as_bool(env["CC_MONITOR_FOCUS_ENABLED"])
        if "CC_MONITOR_TERMINAL_APP" in env:
            cfg.terminal_app = env["CC_MONITOR_TERMINAL_APP"]
        if "CC_MONITOR_NEVER_BLOCK" in env:
            cfg.never_block = _as_bool(env["CC_MONITOR_NEVER_BLOCK"])

        return cfg


def _as_bool(val: str) -> bool:
    return str(val).strip().lower() in {"1", "true", "yes", "on"}
