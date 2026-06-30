# claude-code-monitor

[English](README.md) · **简体中文**

当运行 [Claude Code](https://code.claude.com) 的 iTerm 窗口需要你关注时，第一时间
把它切到最前面。

每当 Claude Code 需要确认/输入，或者任务完成时，对应的 iTerm 窗口和标签页会被自动
提到最前 —— 即使你开了一大堆窗口、早就切走了也没关系。再也不用时不时切回去看
Claude 是不是在等你了。

仅支持 macOS（基于 AppleScript），无需任何硬件。

## 状态映射

| 动作 | Claude Code 事件 |
|------|------------------|
| 聚焦对应的 iTerm 标签页 | `Notification`（Claude 需要输入 / 确认） |
| 聚焦对应的 iTerm 标签页 | `Stop`（任务完成） |

## 安装

```bash
git clone https://github.com/pltuyuhong/claude-code-monitor.git
cd claude-code-monitor
./scripts/install.sh
```

这会安装 `cc-monitor` 命令（纯 Python，无任何依赖）。

## 接入 Claude Code

把 [`examples/settings.hooks.json`](examples/settings.hooks.json) 里的 `hooks` 块
合并到下面任一文件中：

- `~/.claude/settings.json`（全局生效），或
- `<项目>/.claude/settings.json`（按项目生效）。

首次运行时，macOS 会询问是否允许控制 iTerm —— 在 **系统设置 → 隐私与安全性 → 辅助
功能 / 自动化** 中允许它。

## 配置（可选）

默认配置开箱即用。如需自定义，复制示例配置文件：

```bash
mkdir -p ~/.config/cc-monitor
cp examples/config.json ~/.config/cc-monitor/config.json
```

完整的配置项和环境变量覆盖说明见 [docs/configuration.md](docs/configuration.md)
（例如把 `terminal_app` 设为 `"Terminal"`，即可使用系统自带的"终端"而非 iTerm）。

## 工作原理

Claude Code 在每个生命周期事件触发一个 hook，并通过 stdin 传入 JSON（包含项目的
`cwd`）。`cc-monitor` 读取它，再用 AppleScript 遍历每一个 iTerm 会话，选中工作目录
与 `cwd` 匹配的那个标签页。如果没有匹配（或当前 App 不是 iTerm），则退而把整个 App
提到最前。每条路径都做了安全兜底：脚本出错绝不会阻断 Claude Code。

## 测试

```bash
# 模拟某个项目目录触发了 hook：
echo '{"cwd":"'"$PWD"'"}' | cc-monitor focus
```

在另一个窗口里运行上面这行，观察 `$PWD` 对应的 iTerm 标签页被切到最前。

## 已知限制

- 仅支持 macOS + iTerm。欢迎贡献 Linux 后端（wmctrl/xdotool）和 `tmux` 窗格支持
  —— 详见 [CONTRIBUTING.md](CONTRIBUTING.md)。
- 按工作目录定位。如果两个 Claude Code 会话共用同一个 `cwd`，则第一个匹配到的标签页
  胜出。

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
