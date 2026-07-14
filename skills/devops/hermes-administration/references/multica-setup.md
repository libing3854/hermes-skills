# Multica 多Agent统一管理平台 (2026-06-26)

## 概述
Multica 是开源的 managed agents 平台，支持统一管理多个 AI coding agent。冰哥用它管理 Codex、Claude Code、Hermes、MiMo Code。

## 安装

### CLI
```bash
brew install multica-ai/tap/multica
```

### 桌面版 (macOS ARM64)
```bash
# 从 GitHub Releases 下载
curl -L -o ~/Downloads/Multica.dmg \
  "https://github.com/multica-ai/multica/releases/latest/download/multica-desktop-*-mac-arm64.dmg"
# 挂载并安装
hdiutil attach ~/Downloads/Multica.dmg -nobrowse
cp -R "/Volumes/Multica*/Multica.app" /Applications/
hdiutil detach "/Volumes/Multica*"
```

## 配置

### 登录
```bash
multica login  # 弹浏览器 OAuth 授权
```

### 启动 daemon
```bash
multica config set workspace_id <workspace-id>
multica daemon start
```

### 添加自定义 runtime（如 MiMo Code）
```bash
# 1. 创建 profile
multica runtime profile create \
  --command-name mimo \
  --display-name "MiMo Code" \
  --protocol-family opencode

# 2. 设置路径
multica runtime profile set-path <profile-id> --path ~/.mimocode/bin/mimo

# 3. 创建 agent
multica agent create --name "MiMo Code" --runtime-id <runtime-id>

# 4. 重启
multica daemon restart
```

## 常用命令
```bash
multica issue list                    # 查看任务
multica issue create --title "..." --assignee "Agent Name"  # 创建任务
multica agent list                    # 查看 agents
multica runtime list                  # 查看 runtimes
multica daemon status                 # 查看 daemon 状态
multica daemon restart                # 重启 daemon
```

## 支持的 Agent（原生）
Claude Code, Codex, OpenCode, OpenClaw, Hermes, Gemini, Cursor, Kimi, Kiro CLI, Copilot, Pi, Antigravity

## 已知坑
1. CLI 登录和桌面版登录是独立的，需要分别授权
2. 自定义 runtime 必须先创建 profile → set-path → 创建 agent → 重启 daemon
3. kanban.profiles 必须包含所有 assignee，否则任务不会 spawn
4. MiMo Code 协议族用 `opencode`（基于 OpenCode 开发），不用 `claude`
