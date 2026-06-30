# Configuration

`cc-monitor` reads settings from (highest priority first):

1. Environment variables
2. A config file (JSON)
3. Built-in defaults

Defaults work without any config file.

## Config file

Looked up in this order:

1. Path given by `--config` or `$CC_MONITOR_CONFIG`
2. `~/.config/cc-monitor/config.json`
3. `~/.cc-monitor.json`

Example (see [`examples/config.json`](../examples/config.json)):

```json
{
  "focus_enabled": true,
  "terminal_app": "iTerm",
  "never_block": true
}
```

## Keys

| Key | Default | Meaning |
|-----|---------|---------|
| `focus_enabled` | `true` | Bring the terminal to the front on hook events. |
| `terminal_app` | `iTerm` | App to focus (`iTerm` or `Terminal`). |
| `never_block` | `true` | Always exit 0 so failures don't block Claude Code. |

## Environment variables

These override the file:

| Variable | Maps to |
|----------|---------|
| `CC_MONITOR_CONFIG` | config file path |
| `CC_MONITOR_FOCUS_ENABLED` | `focus_enabled` |
| `CC_MONITOR_TERMINAL_APP` | `terminal_app` |
| `CC_MONITOR_NEVER_BLOCK` | `never_block` |

Boolean env values accept `1/true/yes/on` (case-insensitive).

## Notes

- Precise tab targeting (matching `cwd`) only applies when `terminal_app` is
  `iTerm`. With `Terminal`, the app is brought forward but a specific tab is
  not selected.
