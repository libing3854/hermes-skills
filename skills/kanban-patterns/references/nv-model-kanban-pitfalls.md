# NV Models in Kanban: Pitfalls & Workarounds

## Problem: Protocol Violation

NV-hosted models (Qwen3.5 122B, DeepSeek V4 Flash via NVIDIA NIM) frequently crash kanban tasks with "protocol violation" — the worker exits cleanly (rc=0) without calling `kanban_complete` or `kanban_block`.

### Symptoms
- Task status goes from `running` → `blocked` after worker exits
- Events show: `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation`
- File modifications may have actually succeeded despite the protocol crash

### Root Cause
NV models don't reliably understand the kanban tool-calling protocol. They execute the task (read files, modify files) but exit without calling the completion function.

### Affected Models (tested 2026-06-26)
| Model | Simple Tasks | Complex File Tasks | Protocol Compliance |
|-------|-------------|-------------------|-------------------|
| Qwen3.5 122B | ❌ Crashes | ❌ Crashes | Never calls kanban_complete |
| DeepSeek V4 Flash | ✅ Works (3rd try) | ❌ Protocol crash | Intermittent |

### Workaround: Manual Completion Check

After NV task crashes with protocol_violation:

```bash
# 1. Check if file was actually modified (compare mtime)
stat -f "%Sm" /path/to/chapter.md

# 2. Verify the fix was applied
grep -c "问题词" /path/to/chapter.md

# 3. If file was modified correctly, manually complete the task
hermes kanban complete <task_id> --summary "修改已生效（手动确认）"

# 4. If file was NOT modified, re-dispatch or cancel
hermes kanban cancel <task_id>
```

### SOUL.md Template for NV Profiles

Add kanban protocol instructions to SOUL.md:

```markdown
## ⚠️ kanban协议（必须遵守）

完成任务后必须调用工具：
kanban_complete(summary="简短说明完成了什么")

如果任务无法完成，必须调用：
kanban_block(reason="说明为什么无法完成")

**绝对不要**在没有调用kanban_complete或kanban_block的情况下结束对话。
```

**Effectiveness**: Reduces protocol violations but does not eliminate them. Works better on simple tasks than complex file-modification tasks.

### Dispatch Strategy

For NV model tasks:
1. **Simple tasks** (text reply, basic file edit): Dispatch directly, expect ~50% first-try success
2. **Complex tasks** (multi-file modification, novel chapter editing): Dispatch in parallel batches of 3, plan to manually complete ~50% of crashed tasks
3. **Always verify file modification** via mtime before marking task complete
4. **Set `--max 3`** on dispatch to limit concurrent NV tasks

### Config Requirements

NV profiles must include:
- `kanban.profiles` list includes the profile name (e.g. `["lili", "shanli", "nvlinshi"]`)
- Model in `models` list under the provider
- `model.default` set to the full model ID (e.g. `deepseek-ai/deepseek-v4-flash`)

### DeepSeek V4 Flash on NVIDIA NIM

- **Model ID**: `deepseek-ai/deepseek-v4-flash`
- **Endpoint**: `https://integrate.api.nvidia.com/v1`
- **Key env**: `NVIDIA_API_KEY`
- **Context**: 1M tokens
- **Free tier**: Up to 40 RPM
