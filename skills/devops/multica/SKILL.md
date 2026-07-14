---
name: multica
description: Multica多Agent管理平台 — CLI+桌面版，统一管理Claude Code/Codex/Hermes/MiMo Code等coding agents。创建Issue分配给agent，自动执行跟踪进度。
tags: [multica, multi-agent, management, dashboard, cli]
version: 1.0.0
last_updated: 2026-06-26
---

# Multica 多Agent管理平台

## 概述
Multica是开源的managed agents平台，把coding agents变成真正的队友。支持CLI+桌面版（macOS/Windows/Linux）。

## 安装
```bash
# CLI（已装）
brew install multica-ai/tap/multica

# 桌面版（已装）
open /Applications/Multica.app
```

## 配置
- 配置文件：~/.multica/config.json
- Workspace：莉莉丝的小组 (ad9fd941-01a4-4bf1-baca-7073b6d626df)
- 登录：`multica login`（OAuth浏览器授权）

## 常用命令

### Agent管理
```bash
multica agent list                    # 查看所有agent
multica agent create --name "Name" --runtime-id <id>  # 创建agent
multica agent tasks <agent-id>        # 查看agent的任务
```

### Runtime管理
```bash
multica runtime list                  # 查看所有runtime（含状态）
multica runtime profile list          # 查看自定义profile
multica runtime profile create \      # 创建自定义runtime
  --command-name mimo \
  --display-name "MiMo Code" \
  --protocol-family opencode
multica runtime profile set-path <id> --path /path/to/binary  # 设置可执行路径
```

### Issue管理
```bash
multica issue list                    # 查看所有任务
multica issue create \                # 创建任务
  --title "任务标题" \
  --assignee "Agent Name" \
  --description-file /path/to/desc.md
multica issue view <issue-key>        # 查看任务详情
```

### Daemon管理
```bash
multica daemon start                  # 启动daemon
multica daemon restart                # 重启daemon
multica daemon status                 # 查看状态
multica daemon logs                   # 查看日志
```

## 当前Runtime配置

| Agent | Runtime Provider | 状态 | 说明 |
|-------|-----------------|------|------|
| Claude | claude | 🟢 | Claude Code |
| Codex | codex | 🟢 | OpenAI Codex |
| Openclaw | openclaw | 🟢 | OpenClaw |
| Hermes | hermes | 🟢 | Hermes Agent |
| MiMo Code | opencode | 🟢 | 小米MiMo Code（自定义profile） |

## 已知问题

### MiMo Code自定义Runtime（完整流程）
1. MiMo Code不在Multica原生支持列表（13个），需创建custom runtime profile
2. **协议族必须用`opencode`**（MiMo Code基于OpenCode开发，不能用claude）
3. 创建profile后必须`runtime profile set-path`设置可执行路径：`/Users/libing/.mimocode/bin/mimo`
4. `daemon restart`后runtime才会online
5. MiMo Code只支持小米模型，`~/.config/mimocode/mimocode.json`的model必须是`mimo/mimo-auto`
6. 创建agent时需先有runtime，用`agent create --runtime-id <runtime-id>`关联

```bash
# 完整流程
multica runtime profile create --command-name mimo --display-name "MiMo Code" --protocol-family opencode
multica runtime profile set-path <profile-id> --path /Users/libing/.mimocode/bin/mimo
multica daemon restart
multica agent create --name "MiMo Code" --runtime-id <runtime-id>
```

**⚠️ 坑：protocol_family不能改**
- 创建后`protocol_family`不可变（immutable），选错了必须删了重建
- 删除用`multica runtime profile delete <profile-id>`（位置参数，不是--id flag）

### nvlinshi kanban协议违规
- nvlinshi（DeepSeek V4 Flash via NVIDIA）执行完任务不调用kanban_complete
- 修改任务不建议用nvlinshi，优先用agnes或闪莉

### Daemon不自动启动runtime
- 自定义runtime profile创建后，需`daemon restart`才能检测
- Runtime显示offline时需检查路径配置是否正确

### Issue分配不到Agent
- `multica issue create --assignee "名字"` 必须匹配agent的name（含空格）
- 如果报`no member, agent, or squad found`，先`multica agent list`确认agent是否存在
- 创建agent用`multica agent create --name "Name" --runtime-id <id>`
- runtime和agent是两个概念：runtime=可执行程序，agent=带人格/指令的任务执行者

### Kanban profiles与Multica独立
- Multica的profiles（~/.hermes/config.yaml kanban.profiles）和Multica无关
- Multica有自己的agent系统，不依赖Hermes kanban
- 但可以同时使用：Hermes kanban管内部任务，Multica管跨agent协作

## 使用场景
1. **分配任务给agent**：创建Issue → assignee选agent → agent自动执行
2. **监控进度**：`multica issue list`看状态，桌面版可视化
3. **跨agent协作**：同一项目分配给不同agent，各司其职
4. **对照实验**：同一任务分配给多个agent，对比结果质量（2026-06-26验证有效）

### 对照实验工作流
同一任务同时分配给多个agent，结果放到独立文件夹对比：
1. 为每个agent创建独立工作目录（避免文件冲突）
2. 用`hermes kanban create`同时派发相同任务
3. 比较输出质量、速度、完整性
4. 实测结果：闪莉(LongCat) 4/5、闪莉agnes(Agnes 2.0) 5/5、nvlinshi 1/5（kanban协议问题）

## 参考文件
- `references/firecrawl-setup.md` — Firecrawl网页抓取工具安装和配置
