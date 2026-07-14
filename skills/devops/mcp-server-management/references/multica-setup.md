# Multica 多Agent管理平台

## 安装
```bash
brew install multica-ai/tap/multica
```

## 配置流程
1. `multica login` — 浏览器OAuth授权
2. `multica config set workspace_id <id>` — 设置workspace
3. `multica daemon start` — 启动本地daemon

## 添加自定义Runtime（如MiMo Code）
MiMo Code不在Multica原生支持的12个工具里，需要手动创建：
```bash
# 创建自定义runtime profile
multica runtime profile create \
  --command-name mimo \
  --display-name "MiMo Code" \
  --description "小米AI编程助手" \
  --protocol-family opencode  # MiMo Code基于OpenCode

# 设置可执行路径
multica runtime profile set-path <profile-id> \
  --path /Users/libing/.mimocode/bin/mimo

# 创建Agent
multica agent create \
  --name "MiMo Code" \
  --runtime-id <runtime-id>

# 重启daemon
multica daemon restart
```

## 创建Issue分配给Agent
```bash
# 通过文件传参（避免shell转义问题）
multica issue create \
  --title "任务标题" \
  --assignee "Agent名称" \
  --description-file /tmp/task.md
```

## 桌面版
```bash
# 下载DMG
curl -L -o ~/Downloads/Multica.dmg "https://github.com/multica-ai/multica/releases/latest/download/multica-desktop-*-mac-arm64.dmg"
# 安装
hdiutil attach ~/Downloads/Multica.dmg
cp -R "/Volumes/Multica*/Multica.app" /Applications/
hdiutil detach "/Volumes/Multica*"
```

## CLI常用命令
```bash
multica issue list          # 查看任务
multica agent list          # 查看agents
multica runtime list        # 查看runtimes
multica daemon status       # 查看daemon状态
multica daemon restart      # 重启daemon
```

## 支持的原生Runtime
Antigravity, Claude Code, Codex, Cursor, Copilot, Gemini, Hermes, Kimi, Kiro CLI, OpenCode, OpenClaw, Pi
