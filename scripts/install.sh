#!/usr/bin/env bash
#
# install.sh — set up claude-code-monitor (software, macOS)
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "==> Installing cc-monitor from $REPO_DIR"

PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
    echo "error: python3 not found. Install Python 3.8+ first." >&2
    exit 1
fi

"$PY" -m pip install -e .

echo
echo "==> Installed. The 'cc-monitor' command is now available:"
command -v cc-monitor || echo "   (restart your shell if 'cc-monitor' isn't found)"

echo
echo "Next steps:"
echo "  1. (Optional) Copy examples/config.json to"
echo "     ~/.config/cc-monitor/config.json to customise behaviour."
echo "  2. Merge examples/settings.hooks.json into ~/.claude/settings.json"
echo "     (or your project's .claude/settings.json)."
echo "  3. The first run triggers a macOS automation prompt — allow it under"
echo "     System Settings -> Privacy & Security -> Automation."
echo
echo "See README.md for full instructions."
