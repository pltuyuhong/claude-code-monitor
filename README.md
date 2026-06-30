# claude-code-monitor

**English** · [简体中文](README.zh-CN.md)

Bring the iTerm window running [Claude Code](https://code.claude.com) to the
front the moment it needs your attention.

When Claude Code needs confirmation/input, or finishes a task, the matching
iTerm window and tab are raised to the front — even if you have many windows
open and have switched away. No more periodically checking back to see whether
Claude is waiting on you.

macOS only (uses AppleScript). No hardware required.

## Status mapping

| Action | Claude Code event |
|--------|-------------------|
| Focus the iTerm tab | `Notification` (Claude needs input / confirmation) |
| Focus the iTerm tab | `Stop` (task done) |

## Requirements

- **macOS** — focusing is done via AppleScript (`osascript`), which is macOS only.
- **[iTerm2](https://iterm2.com/)** — required for precise tab targeting.
  `cc-monitor` reads each session's working directory through iTerm's
  `session.path` AppleScript variable to find the exact tab matching Claude
  Code's `cwd`. The stock macOS **Terminal.app** does not expose per-tab working
  directories to AppleScript, so it is supported only as a fallback that brings
  the whole app forward (no specific tab) — see [Configure](#configure-optional).
- **Python 3.8+** — pure standard library, no third-party dependencies.

### Installing iTerm2

If you don't have iTerm2 yet:

```bash
brew install --cask iterm2
```

Or download it from [iterm2.com/downloads.html](https://iterm2.com/downloads.html).

Then run Claude Code from inside an iTerm2 window/tab, so `cc-monitor` has a
matching tab to bring forward.

> **Note on iTerm settings:** the working-directory match relies on iTerm
> knowing each session's current directory. This works out of the box on modern
> iTerm2; if matching ever fails, ensure shell integration is installed
> (**iTerm2 → Install Shell Integration**) so `session.path` is populated.

## Install

```bash
git clone https://github.com/pltuyuhong/claude-code-monitor.git
cd claude-code-monitor
./scripts/install.sh
```

This installs the `cc-monitor` command (pure Python, no dependencies).

## Wire into Claude Code

Merge the `hooks` block from
[`examples/settings.hooks.json`](examples/settings.hooks.json) into either:

- `~/.claude/settings.json` (applies everywhere), or
- `<project>/.claude/settings.json` (per project).

The first time it runs, macOS asks whether to allow controlling iTerm — allow
it under **System Settings → Privacy & Security → Automation**.

## Configure (optional)

Defaults work out of the box. To customise, copy the example config:

```bash
mkdir -p ~/.config/cc-monitor
cp examples/config.json ~/.config/cc-monitor/config.json
```

See [docs/configuration.md](docs/configuration.md) for all keys and the
environment-variable overrides (e.g. set `terminal_app` to `"Terminal"` to use
the built-in Terminal app instead of iTerm).

## How it works

Claude Code fires a hook on each lifecycle event and passes JSON (including the
project `cwd`) on stdin. `cc-monitor` reads that and uses AppleScript to walk
every iTerm session, selecting the tab whose working directory matches `cwd`.
If no tab matches (or the app isn't iTerm), it falls back to bringing the whole
app forward. Every path fails safe: a scripting error never blocks Claude Code.

## Test it

```bash
# Pretend a hook fired for a given project directory:
echo '{"cwd":"'"$PWD"'"}' | cc-monitor focus
```

Run that from a different window and watch the iTerm tab for `$PWD` come
forward.

## Limitations

- macOS + iTerm only. A Linux backend (wmctrl/xdotool) and `tmux` pane support
  are welcome contributions — see [CONTRIBUTING.md](CONTRIBUTING.md).
- Targeting is by working directory. If two Claude Code sessions share the same
  `cwd`, the first matching tab wins.

## License

MIT — see [LICENSE](LICENSE).
