"""Tests that don't require a GUI."""
import json

import pytest

from cc_monitor import cli
from cc_monitor.cli import build_parser, main
from cc_monitor.config import Config


def test_config_defaults(monkeypatch, tmp_path):
    monkeypatch.delenv("CC_MONITOR_CONFIG", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = Config.load()
    assert cfg.focus_enabled is True
    assert cfg.terminal_app == "iTerm"


def test_config_file_and_env_override(monkeypatch, tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(json.dumps({"terminal_app": "Terminal"}))
    monkeypatch.setenv("CC_MONITOR_CONFIG", str(cfg_path))
    cfg = Config.load()
    assert cfg.terminal_app == "Terminal"

    monkeypatch.setenv("CC_MONITOR_TERMINAL_APP", "iTerm")
    cfg = Config.load()
    assert cfg.terminal_app == "iTerm"


def test_focus_disabled(monkeypatch, tmp_path):
    monkeypatch.setenv("CC_MONITOR_FOCUS_ENABLED", "false")
    cfg = Config.load()
    assert cfg.focus_enabled is False


def test_parser_defaults_to_focus():
    ns = build_parser().parse_args([])
    assert ns.action == "focus"


def test_main_never_raises(monkeypatch, tmp_path):
    # Disable focus so no AppleScript runs; main should return 0 cleanly.
    monkeypatch.setenv("CC_MONITOR_FOCUS_ENABLED", "false")
    monkeypatch.delenv("CC_MONITOR_CONFIG", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert main(["focus"]) == 0
    assert main([]) == 0


def test_never_block_env_override(monkeypatch):
    monkeypatch.setenv("CC_MONITOR_NEVER_BLOCK", "false")
    assert Config.load().never_block is False
    monkeypatch.setenv("CC_MONITOR_NEVER_BLOCK", "true")
    assert Config.load().never_block is True


def test_run_swallows_errors_by_default(monkeypatch):
    monkeypatch.delenv("CC_MONITOR_NEVER_BLOCK", raising=False)
    monkeypatch.delenv("CC_MONITOR_CONFIG", raising=False)
    monkeypatch.setattr(cli, "main", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(SystemExit) as exc:
        cli.run()
    assert exc.value.code == 0


def test_run_surfaces_errors_when_never_block_false(monkeypatch):
    monkeypatch.setenv("CC_MONITOR_NEVER_BLOCK", "false")
    monkeypatch.setattr(cli, "main", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(SystemExit) as exc:
        cli.run()
    assert exc.value.code == 1
