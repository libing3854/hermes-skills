# Workflow Comparison: 原始 skill-creator vs Hermes 适配版（灵匠）

本文档对比 Anthropic 官方 `skill-creator`（Claude Code 版）和本 `hermes-skill-creator`（Hermes Agent 版）的主要差异。

---

## 核心架构差异

| 维度 | 原始 skill-creator | Hermes 适配版 |
|------|-------------------|---------------|
| **目标平台** | Claude Code CLI | Hermes Agent（tool-based） |
| **技能存储** | `~/.claude/commands/<name>.md` | `~/.hermes/skills/<category>/<name>/SKILL.md` |
| **技能发现** | `available_skills` 列表 | `skill_view()` / `skills_list()` |
| **技能管理** | 手动文件操作 | `skill_manage` 工具（create/edit/patch/delete） |
| **运行测试** | `claude -p "prompt"` | `delegate_task(tasks=[...])` |
| **子代理** | 原生 Claude Code 子进程 | `delegate_task` API |
| **Viewer** | 启动本地 HTTP server | 生成静态 HTML 文件 |
| **打包** | `.skill` zip 文件 | 目录结构（直接使用） |

---

## 移除的功能

原始 skill-creator 中有但 Hermes 版移除的部分：

### 1. `run_loop.py` / `run_eval.py` 自动描述优化

**原因**：这些脚本使用 `claude -p` 子进程来批量测试触发率。Hermes Agent 没有 `claude` CLI，也没有等价的子进程 API。

**替代方案**：在 SKILL.md 中提供"Description Optimization"节，改为人工引导 + LLM 辅助的手动优化流程。

### 2. `package_skill.py` 打包

**原因**：Hermes Agent 使用目录结构管理技能（`~/.hermes/skills/<category>/<name>/`），不需要打包为 `.skill` 文件。

**替代方案**：直接使用 `skill_manage(action='create')` 或 `write_file` 创建目录结构即可。

### 3. `eval-viewer/generate_review.py` 浏览器 Viewer

**原因**：原 viewer 是一个 Flask 风格的 HTTP 服务，需要在浏览器中打开。Hermes Agent 是 CLI 环境，没有图形界面。

**替代方案**：使用 `--static` 模式生成静态 HTML 报告文件，用户可以在浏览器中打开查看。

### 4. Blind Comparison 系统

**原因**：盲对比（A/B 对比）依赖复杂的三方子代理协调，对大多数用户来说过于重量级。

**替代方案**：保留 `agents/comparator.md` 作为 reference，需要时可在 `delegate_task` 中手动实现。

---

## 新增/改进的特性

### 1. 完整的中文支持

所有文档使用中文编写，包括描述、指令、注释。

### 2. Hermes 工具映射表

在主 SKILL.md 中提供完整的工具映射对照表，帮助从 Claude Code 迁移的用户快速上手。

### 3. `quick_validate.py` 适配

原脚本依赖 `yaml` 库。适配版保持了同样的功能，但路径处理更贴近 Hermes 的文件布局。

### 4. `aggregate_benchmark.py` 保留

该脚本不依赖 Claude Code，可以直接在 Hermes 环境中运行，用于聚合测试结果。

---

## 工作流差异细节

### 创建技能

| 步骤 | 原始 | Hermes 版 |
|------|------|-----------|
| 创建 SKILL.md | `touch skills/x/SKILL.md && edit` | `skill_manage(action='create')` |
| 写入文件 | 终端编辑器 | `write_file(path, content)` |
| 编辑内容 | 终端编辑器 | `patch(path, old, new)` 或 `write_file` |

### 运行测试

| 步骤 | 原始 | Hermes 版 |
|------|------|-----------|
| 启动 with-skill | `claude -p "task" --skill path` | `delegate_task({goal: "...", toolsets: [...]})` |
| 启动 baseline | `claude -p "task"` | `delegate_task({goal: "...", toolsets: [...]})` |
| 并行执行 | 异步子进程 | `delegate_task(tasks=[...])` 自动并行 |
| 捕获耗时 | 子进程返回数据 | 从 `delegate_task` 返回的 `duration_ms` 中获取 |

### 评分与聚合

| 步骤 | 原始 | Hermes 版 |
|------|------|-----------|
| 评分 | `delegate_task` 子代理 | 同左（功能相同） |
| 聚合 | `python aggregate_benchmark.py` | 同左（脚本完全相同） |
| 审查 | `generate_review.py` HTTP viewer | 手动或静态 HTML |

---

## 迁移指南

如果你熟悉原始 skill-creator 但想使用 Hermes 版：

1. **停止使用 `claude` CLI** → 改为 `delegate_task`
2. **停止手动管理 `.claude/commands/`** → 改为 `skill_manage` 工具
3. **停止使用 `.skill` 打包** → Hermes Agent 直接读取目录
4. **开始使用 `write_file`/`patch`/`read_file`** 替代文本编辑器
5. **开始使用 `skill_view`/`skills_list`** 替代 `ls ~/.claude/commands/`

---

## 版本对照表

| 发布 | 原始 skill-creator | hermes-skill-creator |
|------|-------------------|---------------------|
| 作者 | Anthropic | Lily (Hermes Agent) |
| 版本 | v1 (持续更新) | v1.0.0 |
| 主要语言 | 英文 | 中文 |
| 平台 | Claude Code | Hermes Agent |
