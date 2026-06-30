"""Bring the terminal window running Claude Code to the front (macOS).

Uses AppleScript via `osascript`. Given the project's working directory
(`cwd`, supplied by the Claude Code hook), it walks every iTerm session and
selects the matching tab/window. If no match is found, or the app is not
iTerm, it falls back to simply activating the app.
"""
from __future__ import annotations

import subprocess
import sys

from .config import Config


def _run_osa(script: str, timeout: int = 5) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(
            ["osascript", "-e", script],
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[cc-monitor] osascript failed: {e}\n")
        return None


def _activate_only(app: str) -> None:
    _run_osa(f'tell application "{app}" to activate')


def _focus_iterm_by_cwd(cwd: str) -> bool:
    """Select the iTerm tab whose session.path matches cwd. True if matched."""
    safe = cwd.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
    set targetPath to "{safe}"
    tell application "iTerm"
        activate
        repeat with w in windows
            repeat with t in tabs of w
                repeat with s in sessions of t
                    try
                        set sp to (variable s named "session.path")
                    on error
                        set sp to ""
                    end try
                    if sp is targetPath then
                        select t
                        select s
                        set index of w to 1
                        return "hit"
                    end if
                end repeat
            end repeat
        end repeat
    end tell
    return "miss"
    '''
    result = _run_osa(script)
    return bool(result and "hit" in (result.stdout or ""))


def focus(cwd: str | None, cfg: Config) -> bool:
    """Focus the terminal. Returns True if a precise tab match was made."""
    if not cfg.focus_enabled:
        return False

    if sys.platform != "darwin":
        sys.stderr.write("[cc-monitor] iTerm focus only supported on macOS\n")
        return False

    app = cfg.terminal_app
    if app == "iTerm" and cwd:
        if _focus_iterm_by_cwd(cwd):
            return True

    _activate_only(app)
    return False
