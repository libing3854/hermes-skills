# Agent Modification Quality & Kanban Protocol Issues (2026-06-26)

## Agent Modification Quality Comparison

**Method:** Same modification task (角色名替换+世界观红线修复) given to 3 agents in independent directories. Each agent got a copy of the same 50 chapters.

| Agent | Model | Pass Rate | Details |
|-------|-------|-----------|---------|
| agnes | Agnes 2.0 Flash | **5/5** | Fixed all character names + 西区 + 处罝 |
| shanli | LongCat 2.0 Preview | 4/5 | Fixed names but missed 西区 |
| nvlinshi | DeepSeek V4 Flash (NV) | 1/5 | Only fixed 处罝, crashed 3x |

**Conclusion:** Agnes 2.0 Flash is the most reliable for file modification tasks.

## NV DeepSeek V4 Flash Kanban Protocol Violation

**Problem:** DeepSeek V4 Flash via NVIDIA API has persistent kanban protocol violation — the worker executes the task (even modifies files correctly) but exits without calling `kanban_complete` or `kanban_block`.

**Symptoms:**
- `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation`
- Files may actually be modified correctly, but task status is blocked/crashed
- Multiple retries don't help — same error every time
- SOUL.md with explicit kanban protocol instructions doesn't fix it

**Root Cause:** DeepSeek V4 Flash via NVIDIA doesn't reliably follow kanban protocol (function calling for kanban_complete/kanban_block).

**Workaround:**
1. Check if files were actually modified (grep verification)
2. If files are correct, manually complete: `hermes kanban complete <task_id> --summary "..."`
3. Don't retry — will fail the same way

## Kanban Profiles Configuration

**Problem:** Creating a kanban task with `--assignee nvlinshi` but nvlinshi is not in the default config's `kanban.profiles` list. Task stays "ready" and never spawns.

**Fix:** Add all profiles to config:
```yaml
kanban:
  profiles: '["lili", "shanli", "nvlinshi", "shanli-agnes20flash"]'
```

**Detection:** Task shows `status: ready` with `Spawned: 0` after dispatch.

## Three-Way Review Pattern

For important novel volumes, run three independent reviews:
- **莉莉** (DeepSeek V4 Flash): 字数/禁用词/高频词
- **大莉M** (MiMo Pro): 结构/大纲匹配/伏笔回收
- **大莉D** (DeepSeek V4 Pro): 角色名一致性/跨卷矛盾/逻辑bug

Merge results, deduplicate, produce unified fix list.
