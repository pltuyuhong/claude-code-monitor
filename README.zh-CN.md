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

## 环境要求

- **macOS** —— 聚焦通过 AppleScript（`osascript`）实现，仅支持 macOS。
- **[iTerm2](https://iterm2.com/)** —— 精确定位标签页所必需。`cc-monitor` 通过
  iTerm 的 `session.path` AppleScript 变量读取每个会话的工作目录，从而找到与
  Claude Code 的 `cwd` 匹配的那个标签页。macOS 自带的 **Terminal.app** 不会把每个
  标签页的工作目录暴露给 AppleScript，因此它只能作为降级方案使用 —— 仅把整个 App
  提到最前，不会选中具体标签页（见 [配置（可选）](#配置可选)）。
- **Python 3.8+** —— 纯标准库，无任何第三方依赖。

### 安装 iTerm2

如果你还没装 iTerm2：

```bash
brew install --cask iterm2
```

或从 [iterm2.com/downloads.html](https://iterm2.com/downloads.html) 下载。

然后在 iTerm2 的窗口/标签页里运行 Claude Code，这样 `cc-monitor` 才有对应的标签页
可以切到最前。

> **关于 iTerm 设置：** 工作目录匹配依赖 iTerm 知道每个会话的当前目录。在较新版本的
> iTerm2 上开箱即用；如果匹配偶尔失败，请确认已安装 Shell 集成
> （**iTerm2 → Install Shell Integration**），以保证 `session.path` 有值。

## 安装

```bash
git clone https://github.com/pltuyuhong/claude-code-monitor.git
cd claude-code-monitor
./scripts/install.sh
```

这会安装 `cc-monitor` 命令（纯 Python，无任何依赖）。

> **运行脚本时提示 `permission denied`？** 通过下载 ZIP 包或在某些 git 配置下，文件的
> 可执行位可能会丢失。可以直接用 bash 运行：
>
> ```bash
> bash scripts/install.sh
> ```
>
> 或先恢复可执行位 `chmod +x scripts/install.sh` 再重新运行。

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
`cwd`）。`cc-monitor` 读取它，然后分两步聚焦终端：

1. **用 `open -a` 把 App 拉到前台。** hook 触发时你通常已经切到别的 App，所以
   `cc-monitor` 是以后台进程运行的。后台进程调用 `osascript ... activate` 无法可靠地
   跨 App 抢焦点——它往往只是在后台悄悄重排了窗口；而 `open -a`（走 LaunchServices）
   能真正把 App 拉到前台。
2. **选中匹配的标签页。** 此时 iTerm 已在前台，再用 AppleScript 遍历每个 iTerm 会话，
   把工作目录与 `cwd` 匹配的那个标签页翻到最前。（窗口重排只有在 App 已激活时才会真正
   生效，所以顺序很关键。）

如果没有匹配（或当前 App 不是 iTerm），你仍会得到第 1 步的 App 级聚焦。每条路径都做了
安全兜底：脚本出错绝不会阻断 Claude Code。

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
