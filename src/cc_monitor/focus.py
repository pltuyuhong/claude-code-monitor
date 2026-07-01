"""Bring the terminal window running Claude Code to the front (macOS).

Given the project's working directory (`cwd`, supplied by the Claude Code
hook), this focuses the matching terminal window in two steps:

1. Bring the app to the foreground with ``open -a``. When the hook fires you
   have usually switched to another application, so `cc-monitor` runs as a
   background process. `osascript ... activate` does **not** reliably steal
   focus across applications from a background process — it often just
   reorders windows invisibly. ``open -a`` goes through LaunchServices and
   does bring the app forward.
2. Once iTerm is frontmost, select the tab/window whose ``session.path``
   matches ``cwd``. Reordering a window to the front only takes visible
   effect while the app is already active, hence the ordering.

Every path fails safe: a scripting error never propagates out.
"""
from __future__ import annotations

import subprocess
import sys
import time

from .config import Config

# Seconds to wait after `open -a` before selecting the tab, so the app has
# finished coming to the foreground (otherwise the reorder happens while it
# is still in the background and is not visible).
_FOREGROUND_DELAY = 0.5


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


def _bring_app_to_front(app: str) -> None:
    """Foreground the app reliably, even from a background hook process."""
    try:
        subprocess.run(["open", "-a", app], timeout=5,
                       capture_output=True, text=True)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[cc-monitor] open -a {app} failed: {e}\n")
        # Last resort: AppleScript activate (less reliable across apps).
        _run_osa(f'tell application "{app}" to activate')


def _select_iterm_tab_by_cwd(cwd: str) -> bool:
    """Raise the iTerm tab whose session.path matches cwd. True if matched.

    Assumes iTerm is already frontmost (see module docstring).
    """
    safe = cwd.replace("\\", "\\\\").replace('"', '\\"')
    script = f'''
    set targetPath to "{safe}"
    tell application "iTerm"
        repeat with w in windows
            repeat with t in tabs of w
                repeat with s in sessions of t
                    try
                        set sp to (variable s named "session.path")
                    on error
                        set sp to ""
                    end try
                    if sp is targetPath then
                        select s
                        select t
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

    # Step 1: bring the app forward (works from a background process and
    # across whatever app is currently frontmost).
    _bring_app_to_front(app)

    # Step 2: for iTerm, now that it is frontmost, raise the tab matching
    # cwd. Terminal.app does not expose per-tab cwd to AppleScript, so it
    # only gets the app-level focus from step 1.
    if app == "iTerm" and cwd:
        time.sleep(_FOREGROUND_DELAY)
        return _select_iterm_tab_by_cwd(cwd)

    return False
