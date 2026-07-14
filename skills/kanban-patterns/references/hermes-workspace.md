# Hermes Workspace

## 概述
Hermes Workspace 是一个独立的开源 Web UI 项目，用于管理 Hermes AI Agent。
- 官网：https://hermes-workspace.com/
- 代码位置：`/Users/libing/hermes-workspace/`
- 默认端口：3000（不是 hermes dashboard 的 9119）

## 与 hermes dashboard 的区别

| 项目 | 端口 | 启动方式 | 功能 |
|------|------|---------|------|
| Hermes Workspace | 3000 | `vite dev` 或 `start.sh` | 完整 Web UI：聊天、记忆、技能、终端、文件管理 |
| hermes dashboard | 9119 | `hermes dashboard` | 配置管理、API keys、会话查看 |

## 启动方式

### 方法1：使用 start.sh（推荐）
```bash
cd /Users/libing/hermes-workspace
bash start.sh
```

### 方法2：直接启动 vite
```bash
cd /Users/libing/hermes-workspace
nohup node_modules/.bin/vite dev --host 127.0.0.1 --port 3000 &
```

### 方法3：Docker（如果安装了 Docker）
```bash
cd /Users/libing/hermes-workspace
docker compose up
```

## 检查状态
```bash
# 检查端口
lsof -i :3000

# 检查进程
ps aux | grep vite | grep -v grep
```

## 停止
```bash
# 找到进程并杀掉
lsof -ti :3000 | xargs kill
```

## 常见问题

### 1. Gateway 重启导致 Workspace 停止
Gateway 重启时，Workspace 的 vite 进程可能被意外终止。
**修复：** 重新运行 `bash /Users/libing/hermes-workspace/start.sh`

### 2. 开机自启
Workspace 没有配置开机自启。重启 Mac 后需要手动启动。

### 3. 与 hermes dashboard 混淆
用户说"web工具"或"web插件"时，可能指的是 Hermes Workspace（端口3000），不是 hermes dashboard（端口9119）。

## 配置文件
- `.env` — 环境变量（API keys、provider 配置）
- `docker-compose.yml` — Docker 部署配置
- `AGENTS.md` — Agent 配置（swarm workers）

## Chrome DevTools MCP 无头 Chrome 占用问题（2026-06-22）

**问题：** Chrome DevTools MCP 插件启动的无头 Chrome 进程（`--headless=new`）会占用浏览器配置文件目录（`~/.cache/chrome-devtools-mcp/chrome-profile`），导致正常 Chrome 无法打开。

**症状：** 双击 Chrome 图标无反应，或弹出"Chrome 被占用"提示。

**诊断：**
```bash
ps aux | grep "chrome-devtools-mcp" | grep -v grep
# 如果有输出，说明无头 Chrome 正在运行
```

**修复：**
```bash
# 杀掉 chrome-devtools-mcp 相关进程
pkill -f "chrome-devtools-mcp" 2>/dev/null
sleep 2
# 重新打开 Chrome
open -a "Google Chrome"
```

**预防：** 不使用浏览器工具时，可以停止 chrome-devtools-mcp 服务。但如果需要使用 `browser_navigate`、`browser_vision` 等工具，则需要保持无头 Chrome 运行。

**注意：** 杀掉无头 Chrome 后，当前会话的浏览器工具（browser_navigate 等）会失效，需要重新初始化浏览器会话。
