# Multica多Agent管理平台集成指南

## 概述
Multica是开源的多Agent管理平台，可与Hermes kanban并存。支持Claude Code、Codex、OpenCode、Hermes、Gemini等13个agent。

## 安装
```bash
brew install multica-ai/tap/multica  # CLI v0.3.30
# 桌面版：从 GitHub Releases 下载 DMG（arm64约214MB）
# 下载地址：https://github.com/multica-ai/multica/releases/download/v0.3.30/multica-desktop-0.3.30-mac-arm64.dmg
```

## 配置流程
1. `multica login` → 浏览器OAuth授权
2. `multica config set workspace_id <id>` → 设置workspace
3. `multica daemon start` → 启动daemon（自动扫描PATH中的agent工具）
4. 查看检测到的agent：`multica runtime list`
5. 创建agent：`multica agent create --name "Name" --runtime-id <id>`
6. 创建任务：`multica issue create --title "任务" --assignee "AgentName"`

## 自定义Runtime（如MiMo Code）
MiMo Code不在Multica原生支持列表中，需要手动添加：

```bash
# 1. 确保mimo在PATH中
ln -sf ~/.mimocode/bin/mimo /usr/local/bin/mimo

# 2. 创建自定义runtime profile
# MiMo Code基于OpenCode开发，用opencode协议族
multica runtime profile create \
  --command-name mimo \
  --display-name "MiMo Code" \
  --protocol-family opencode \
  --description "小米AI编程助手"

# 3. 设置可执行路径
multica runtime profile set-path <profile-id> --path ~/.mimocode/bin/mimo

# 4. 重启daemon
multica daemon restart

# 5. 创建agent绑定runtime
multica agent create --name "MiMo Code" --runtime-id <runtime-id>
```

### 协议族选择
| Agent | 协议族 |
|-------|--------|
| Claude Code | claude |
| Codex | codex |
| OpenCode | opencode |
| MiMo Code | opencode（基于OpenCode） |
| Gemini | gemini |

## 常用命令
```bash
multica runtime list          # 查看所有runtime
multica agent list            # 查看所有agent
multica issue list            # 查看所有任务
multica issue create ...      # 创建任务
multica daemon status         # daemon状态
multica daemon restart        # 重启daemon
```

## 注意事项
- 协议族一旦创建不可修改，需删了重建（`multica runtime profile delete <id>`）
- 自定义runtime需先创建agent
- kanban和Multica可并存
- MiMo Code配置：`~/.config/mimocode/mimocode.json`中model字段必须是字符串格式
