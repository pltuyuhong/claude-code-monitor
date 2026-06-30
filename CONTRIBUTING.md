# Contributing

Thanks for your interest in improving claude-code-monitor!

## Development setup

```bash
git clone https://github.com/pltuyuhong/claude-code-monitor.git
cd claude-code-monitor
python3 -m pip install -e ".[dev]"
```

## Before opening a PR

```bash
ruff check src scripts        # lint
pytest                        # tests
```

Please keep the "never block Claude Code" guarantee: any scripting failure in
the hook path must result in exit code 0, never an exception that propagates
out of the CLI.

## Ideas / good first issues

- **Linux window-focus backend** (wmctrl / xdotool) to complement macOS.
- **`tmux` support** for selecting the right pane.
- **More precise session targeting** than `cwd` (e.g. a session-id handshake)
  so two sessions in the same directory can be told apart.

## Reporting bugs

Open an issue with your OS, Python version, terminal app, and the relevant
chunk of `.claude/settings.json`.
