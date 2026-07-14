# 对照实验：多模型并行修改对比

## 场景

同一章节交给不同模型修改，对比哪个改得好，选优采用。

## 工作流

```
1. 莉莉审核 → 出审核报告（P1-P4优先级）
2. 同时派发：
   - 闪莉（shanli）改第N章
   - nvlinshi 改第N章（⚠️ 限速，每次1章）
3. 两份修改稿对比 → 选优采用
```

## 并发策略

| 模型 | 并发限制 | 原因 |
|------|---------|------|
| 闪莉（LongCat/DeepSeek） | 可并发多章 | 无特殊限制 |
| nvlinshi（NVIDIA NIM） | **每次1章** | API限速，高并发会429 |

## 派发示例

```bash
# 闪莉：可批量
hermes kanban create "闪莉改379章" --assignee shanli --workspace "dir:$(pwd)" ...

# nvlinshi：必须串行
hermes kanban create "nv改379章" --assignee nvlinshi --workspace "dir:$(pwd)" ...
hermes kanban dispatch --max 1  # 一次只派1个
```

## 对比维度

| 维度 | 权重 |
|------|------|
| P1 字数达标 | 必须 |
| P2 无跨章重复 | 必须 |
| P3 角色/世界观一致 | 必须 |
| P4 AI味程度 | 参考 |
| 文笔自然度 | 主观 |

## 注意事项

- nvlinshi的model是qwen/qwen3.5-122b-a10b（128K上下文，NVIDIA NIM）
- 如果NV返回429/限速错误，等待60s后重试
- 对比结果记录到fact_store，供后续决策参考

## 实战经验（2026-06-26 验证）

### nvlinshi模型变更
- **旧模型**：meta/llama-4-maverick-17b-128e-instruct（已下线）
- **过渡模型**：qwen/qwen3.5-122b-a10b（kanban协议不稳定，连续6次protocol_violation）
- **当前模型**：deepseek-ai/deepseek-v4-flash（NVIDIA NIM，1M上下文，kanban协议间歇性可用）
- **SOUL.md**：必须包含kanban协议说明（kanban_complete/kanban_block）

### ⚠️ NV模型kanban协议问题（关键陷阱）
**问题**：NV模型执行完kanban任务后，可能不调用`kanban_complete`或`kanban_block`，直接退出。
**症状**：
- 任务状态卡在running，最终标记为protocol_violation
- 但文件实际上已经被修改了！（检查mtime和内容可确认）
- worker exit code=0（正常退出），但没走kanban协议

**根因**：NV模型对kanban工具协议的理解不稳定，SOUL.md中的指令有帮助但不能完全消除问题。

**解决方案**：
1. 在nvlinshi的SOUL.md中加入kanban协议说明
2. 派发任务后，主动检查文件是否被修改（`stat -f "%Sm" file` + 内容验证）
3. 如果文件已修改但任务卡住，手动完成：
   ```bash
   hermes kanban complete <task_id> --summary "修改已完成（手动确认）"
   ```
4. 不要等nvlinshi自己调用kanban_complete——它可能不会

### 对比结果（2026-06-26 更新）
| 模型 | 任务完成 | 修改速度 | 修改质量 | kanban协议 | 稳定性 |
|------|---------|---------|---------|-----------|--------|
| 闪莉（shanli） | ✅ 成功 | ⚡ ~1分钟 | ⭐⭐⭐⭐⭐ | ✅ 正常调用 | ✅ 稳定 |
| nvlinshi（DeepSeek V4 Flash） | ⚠️ 需重试/手动完成 | 🐢 ~2-10分钟 | ✅ 修改正确 | ⚠️ 间歇性 | ⚠️ 可用但需监控 |
| nvlinshi（Qwen3.5 122B） | ❌ 协议全失败 | — | 修改正确但不可控 | ❌ 从不调用kanban_complete | ❌ 已弃用 |

### 建议
- **日常修改用闪莉**：稳定可靠，协议完整
- **对照实验/特殊场景用nvlinshi**：能干活但需要手动完成任务
- **优先用DeepSeek V4 Flash**：比Qwen3.5在kanban协议上表现好

### nvlinshi SOUL.md kanban协议模板（2026-06-26 验证有效）
更新nvlinshi的SOUL.md后，协议违规率显著降低。关键内容：
```markdown
## ⚠️ kanban协议（必须遵守）
完成任务后必须调用：kanban_complete(summary="简短说明")
无法完成时必须调用：kanban_block(reason="说明原因")
绝对不要在没有调用这两个工具的情况下结束对话。
```
