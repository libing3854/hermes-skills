# 真实审查案例：open-world-project/model-router

审查日期：2026-05-26

## 项目概况
- 仓库：https://github.com/open-world-project/model-router
- 类型：Hermes Agent 自动成本感知模型路由插件
- 作者：Jakub Misiak + "archer"
- 代码量：install.py 2257 行 + __init__.py 946 行 = ~3200 行
- 项目年龄：仅 17 天，4 次 commit（2026-05-09 首次发布）
- 许可：MIT

## 五维度审查

### 来源 🟡
- 极新项目（17天），仅 4 次 commit
- 无社区验证，单点维护风险
- 作者接受 Buy Me a Coffee 捐赠

### 代码 🟡
- **修改 Hermes 核心文件**：commands.py（注入 6 个 CommandDef）、cli.py（注入 4 个代码块）
- **替换启动器**：`~/.local/bin/hermes` 被替换为 wrapper 脚本，每次执行先经过 model-router 验证
- **注入代码透明可审计**：无后门，无混淆
- **修改前创建时间戳备份**：`xxx.bak.model-router.YYYYMMDD_HHMMSS`
- **分类器使用 Hermes 已有 API 通道**，通过 `auxiliary.triage_specifier` 配置
- **无远程自更新**：修复仅使用本地 install.py

### 依赖 🟢
- 零新增外部依赖（全部使用 Hermes 已有包 + Python stdlib）
- 无需 pip install

### 许可 🟢
- MIT License — 最宽松许可，无使用限制

### 权限 🟡
- 🔴 **替换 ~/.local/bin/hermes 启动器** — 最高风险点
- 修改 ~/.hermes/hermes-agent/hermes_cli/commands.py 和 cli.py
- 写入 ~/.hermes/model_router.yaml, skill_routing.md, SOUL.md
- 可选：修改 hermes-webui 的 6 个文件（api/routes.py, static/ui.js 等）
- 不需要 sudo/root

## 结论：🟡 谨慎安装
功能有价值（自动模型路由），但启动器替换风险高。
冰哥已有闪莉 Ping 动态选模系统，功能重叠，建议不装。

## 代码借鉴亮点（已应用到 model_selector.py）
- 轻量分类器做复杂度判定
- Fast-path 正则检测极短 ACK
- Session 状态管理（pin/unpin/escalation）
- 中环 self-escalation 自动升级
- .bak 时间戳备份机制
