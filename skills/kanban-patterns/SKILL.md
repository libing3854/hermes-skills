---
name: kanban-patterns
description: Kanban task management patterns — workspace configuration, task decomposition, and user confirmation workflows. Use when creating kanban tasks that produce files, managing complex multi-step kanban workflows, or when user corrects task execution approach.
tags: [kanban, workflow, patterns, file-management]
---

# Kanban Task Management Patterns

## Core Patterns

### 1. Workspace Configuration (Critical)

**Problem:** `scratch` workspace is ephemeral — files are deleted when task completes.

**Solution:** Always use `--workspace dir:/path` for tasks that produce persistent files.

```bash
# ❌ WRONG — files will be lost
hermes kanban create "Task" --assignee shanli

# ✅ CORRECT — files persist
hermes kanban create "Task" --assignee shanli --workspace "dir:/Users/libing/Desktop/项目目录"
```

**When to use each workspace type:**
| Workspace | Use Case | File Persistence |
|-----------|----------|------------------|
| `scratch` (default) | Temporary analysis, no file output | ❌ Deleted |
| `dir:/path` | File production (writing, code generation) | ✅ Permanent |
| `worktree:/path` | Git-based projects needing branch isolation | ✅ Permanent |

**Pitfall:** Tasks writing to absolute paths (e.g., `--workspace dir:/Users/.../正文/`) should use relative paths in the task body (e.g., "保存到：正文/ 目录下") to avoid path confusion.

### 2. Task Decomposition for Complex Modifications

**Problem:** Complex modification tasks exceed iteration budget (90/90 turns).

**Solution:** Decompose into smaller, focused tasks (2-3 chapters per task).

**Decomposition Strategy:**
1. **Writing tasks (LongCat/闪莉):** 8 chapters per batch (works well)
2. **Writing tasks (Gemini/shanliG via script):** 2 chapters per batch（Gemini字数膨胀严重，8章迭代预算容易耗尽）
3. **Modification tasks:** 4 chapters per task (must decompose; 1-2 is too few, wastes overhead)
4. **Review tasks:** Full batch OK (review is fast)

**Example decomposition:**
```
❌ ONE TASK: "修改全部8章的所有问题"
✅ FOUR TASKS:
  1. "修改第164-166章（两稿拼接修复）"
  2. "修改第169-170章（两稿拼接修复）"
  3. "模板化结尾去重+AI高频词压缩"
  4. "角色设定修复"
```

**Rule of thumb:** If the task body exceeds ~500 words or involves 4+ distinct operations, decompose it.

### 2a. Parallel Dispatch for Independent Chapters (2026-06-24 verified)

**问题：** 写作任务通常需要顺序执行（后一批需要读前一批的输出）。但如果章节来自不同情节点，且前驱章节已存在，就可以并行dispatch。

**判断规则：** 第N章能并行写，当且仅当第N-1章文件已存在。

**实测案例：** 第七卷扩写，同时派发8章（348/351/356/361/365/367/372/374），因为它们的前驱章节（347/350/355/360/364/366/371/373）都已存在。

```bash
# 并行派发多章
for ch in 348 351 356 361 365 367 372 374; do
  # 检查前驱章节是否存在
  prev=$((ch - 1))
  ls 第${prev}章_*.md >/dev/null 2>&1 || continue
  
  TASK_OUT=$(hermes kanban create "第七卷扩写${ch}章" --assignee shanli ...)
  # ...订阅+dispatch
done
hermes kanban dispatch --max 10
```

**速度提升：** 从串行（每批2章×12批=24批任务）→ 并行（2轮×8章=16个任务），时间缩短60%+。

**⚠️ 注意：** 同一情节点内的章节仍需串行（因为需要前一章的结尾做衔接）。只有不同情节点的章节才能并行。

### 2c. 大纲合规性——每个情节点的章节数（2026-06-24 冰哥纠正）

**问题：** 写作任务只给了剧情摘要，没有明确每个情节点需要几章。闪莉把每个情节点压缩到1-2章，而大纲规划每个情节点3-4章。结果45章的卷只写了21章。

**冰哥原话：** "为什么每次都20写完没按大纲走"

**解决方案：** 写作任务body中必须明确每个情节点的章节数：

```
## 情节点分配（严格遵守）
| 情节点 | 规划章数 | 章节编号 | 内容概要 |
|--------|---------|---------|---------|
| 一 | 3-4章 | 334-337 | 尤娜来访+徽章+团队讨论 |
| 二 | 4章 | 338-341 | 西尔薇娅历史课 |
| ... | ... | ... | ... |
```

**验证：** 写完后检查每个情节点实际写了几章 vs 大纲规划：
```bash
grep "章节参考" 大纲.md | head -12  # 大纲规划
ls 第*章_*.md | wc -l               # 实际章数
```

**如果发现压缩：** 需要重编号+补写（见35g节）。

### 2b. Sequential Task Dependencies

**Problem:** Batch 2 depends on batch 1's output (e.g., writing chapters 296-300 requires chapters 290-295 to be written first). But kanban dispatches all ready tasks simultaneously.

**Solution:** Only dispatch batch 1 first. Batch 2 and 3 are created but stay in "ready" state until batch 1 completes.

**Workflow:**
```
1. Create all tasks (T1, T2, T3)
2. Subscribe all to notifier
3. Dispatch only T1: hermes kanban dispatch --max 1
4. When T1 completes → dispatch T2
5. When T2 completes → dispatch T3
```

**Why not dispatch all at once:**
- Worker needs to read batch 1's output files
- Parallel writes to same directory cause conflicts
- Sequential ensures quality chain (each batch builds on previous)

**Pattern for 3-batch rewrite:**
```bash
# Create all 3 tasks
T1=$(hermes kanban create "重写290-295章" --assignee shanli ... | grep -o 't_[a-f0-9]*')
T2=$(hermes kanban create "重写296-300章" --assignee shanli ... | grep -o 't_[a-f0-9]*')
T3=$(hermes kanban create "重写301-304章" --assignee shanli ... | grep -o 't_[a-f0-9]*')

# Subscribe all
for tid in $T1 $T2 $T3; do sqlite3 ...; done

# Dispatch only batch 1
hermes kanban dispatch --max 1
# T2 and T3 stay in "ready" state, will be dispatched later
```

### 3. User Confirmation Before File Modification

**Problem:** User corrected agent for modifying files without explicit confirmation.

**User's correction:** "是让你分析一下不是让你改改回去改不改我决定"

**Solution:**
- **Analysis tasks:** Report findings, do NOT modify files
- **Modification tasks:** Only modify after user explicitly confirms
- **Default behavior:** Show analysis → wait for "改" or "修改" → then execute

**Workflow:**
```
1. Read and analyze file
2. Present findings (problems, suggestions)
3. Wait for user decision
4. If user says "改" or confirms → execute modifications
5. If user says "不改" or "不用" → leave as-is
```

**Exception:** User explicitly says "直接改" or "改掉" in the original task description.

### 3b. Always Use Kanban for File Modifications (Critical)

**Problem:** Agent ran `delegate_task` directly for file modification work instead of creating kanban tasks. User corrected: "停，为什么不是看板"

**User's correction:** All file-producing work (writing, modification, cleanup, refinement) MUST go through kanban, even when it seems faster to do it directly. Kanban provides: task tracking, completion notifications, audit trail, and proper workspace isolation.

**When to use kanban vs direct execution:**
| Task Type | Kanban Required? | Reason |
|-----------|-----------------|--------|
| File modification (any) | ✅ YES | Tracking, notifications, audit |
| Text refinement/cleanup | ✅ YES | Produces persistent files |
| Analysis only (no file output) | ❌ No | No files produced |
| Single quick fix (<2 min) | ⚠️ User decides | Ask first |
| Complex multi-step work | ✅ YES | Decompose into kanban tasks |

**Workflow:**
```
1. Analyze the problem (direct execution OK)
2. Present findings to user
3. User says "改" → create kanban task with detailed body
4. Dispatch task → monitor → report results
```

**Never:** Run `delegate_task` or `execute_code` to modify project files directly. Always create a kanban task first.

### 4. Profile Configuration for Kanban Workers

**Pattern:** Different agent roles need different model configurations.

**Example setup:**
```yaml
# profiles/shanli/config.yaml (writing tasks)
model:
  provider: longcat
  default: LongCat-2.0-Preview

# profiles/lili/config.yaml (review tasks)
model:
  provider: deepseek
  default: deepseek-v4-flash
```

**⚠️ Profile 命名规则：** 名称必须匹配 `[a-z0-9][a-z0-9_-]{0,63}`。不能包含中文、大写字母、点号(`.`)或特殊符号。中文或点号名称会导致 `spawn_failed: Invalid profile name`。例如 `shanli-agnes2.0flash`（含点号）❌ → `shanli-agnes20flash` ✅。

**⚠️ 称呼规则（冰哥纠正）：** 提到任务角色时必须用 **profile名**，不用模型名。
| Profile | 模型 | 用途 |
|---------|------|------|
| lili | DeepSeek V4 Flash | 审核 |
| shanli | LongCat 2.0 Preview | 写作 |
| shanliG | Gemini 3.5 Flash（本地反代） | 写作备用 |
| shanli-agnes20flash | Agnes | 修改 |

❌ "让DeepSeek审核" → ✅ "让lili审核"
❌ "用MiMo写" → ✅ "用shanli写"
❌ "Gemini写" → ✅ "用shanliG写"

**Kanban config:**
```yaml
kanban:
  profiles:
  - lili      # reviewer
  - shanli    # writer
  - shanliG   # writer (Gemini backup)
```

**Usage:**
```bash
# Writing task → shanli (LongCat)
hermes kanban create "写作任务" --assignee shanli

# Review task → lili (deepseek-v4-flash)
hermes kanban create "审核任务" --assignee lili

# Backup writing → shanliG (Gemini)
hermes kanban create "写作任务" --assignee shanliG
```

## Task Creation Template

**⚠️ Title is a POSITIONAL argument, NOT a flag.** `--title` does not exist and will error.

```bash
# ✅ CORRECT — title is the first positional arg
hermes kanban create "任务标题" \
  --assignee <profile> \
  --workspace "dir:/path/to/project" \
  --body "任务描述..."

# ❌ WRONG — --title is not a valid flag
hermes kanban create --title "任务标题" --assignee shanli
# → error: unrecognized arguments: --title
```

**Workspace must use `dir:` prefix** for absolute paths:
```bash
# ✅ CORRECT
--workspace "dir:/Users/libing/Desktop/项目目录"

# ❌ WRONG — bare path fails
--workspace "/Users/libing/Desktop/项目目录"
# → error: unknown --workspace value
```

### 14. Auto-Subscribe Kanban Notifications on Task Creation (Mandatory)

**Rule:** Every time a kanban task is created or dispatched, IMMEDIATELY subscribe it to the native Gateway notifier so the user gets instant notifications on QQ.

**After creating/dispatching a task, run:**
```bash
TASK_ID="<task_id_from_create_output>"
sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs (task_id, platform, chat_id, thread_id, user_id, notifier_profile, created_at, last_event_id) VALUES ('${TASK_ID}', 'qqbot', '54D8D2AB6A48EE35127DD0F86081146A', '', 'binge', 'default', strftime('%s','now'), (SELECT COALESCE(MAX(id),0) FROM task_events));"
```

**Why mandatory:** Without this subscription, the Gateway native notifier won't push task completion to QQ.

**Platform/Chat targets (current):**
| Platform | Chat ID | User |
|----------|---------|------|
| qqbot | 54D8D2AB6A48EE35127DD0F86081146A | binge |

**If delivery target changes:** Update the `chat_id` value in the INSERT above.

### 15. Gateway Native Notifier — How It Actually Works (2026-06-13 verified)

The native notifier is an asyncio task (`_kanban_notifier_watcher`) inside the Gateway process. It polls `kanban_notify_subs` → `task_events` every 5 seconds and delivers terminal events (completed/blocked/gave_up/crashed/timed_out) to the subscribed platform.

**Architecture:**
```
Gateway process
  └─ _kanban_notifier_watcher (asyncio task, 5s interval)
       ├─ claim_unseen_events_for_sub() — atomic cursor advance
       ├─ adapter.send() — push to QQ/Telegram/Discord
       └─ auto-remove subscription when task reaches terminal state
```

**Key behaviors:**
- Cursor is advanced BEFORE send (atomic claim). If send fails, `_kanban_rewind()` rolls back.
- After MAX_SEND_FAILURES=3 consecutive failures, subscription is dropped.
- Subscription auto-removed when task reaches `done` or `archived` status.
- `gateway_notify_interval` in config.yaml (default 600s) is for a DIFFERENT interval — the notifier itself ticks every 5s.

**Pitfalls discovered (2026-06-13):**

1. **Subscriptions cleared on Gateway restart** — The `kanban_notify_subs` table may be cleared when the Gateway process restarts (WAL checkpoint or DB re-init). After any restart, re-verify subscriptions exist:
   ```bash
   sqlite3 ~/.hermes/kanban.db "SELECT * FROM kanban_notify_subs;"
   ```
   If empty, re-insert subscriptions for active tasks.

2. **Default Gateway crash loop** — If `~/.hermes/active_profile` contains a profile name (e.g., "shanli"), the default Gateway overrides HERMES_HOME to that profile's directory, colliding with the shanli Gateway's PID/lock files. Fix: add `--profile default` to `~/Library/LaunchAgents/ai.hermes.gateway.plist` ProgramArguments. See `references/two-gateway-architecture.md`.

3. **send() return value bug** — `adapter.send()` returns `SendResult(success=False)` on failure instead of raising. The notifier only caught exceptions, so failed sends were silently ignored. Fixed in `gateway/kanban_watchers.py` ~line 306: now checks `send_result.success` and raises `RuntimeError` to trigger rewind+retry.

**Diagnostic checklist:**
```bash
# 1. Check subscriptions exist
sqlite3 ~/.hermes/kanban.db "SELECT task_id, last_event_id FROM kanban_notify_subs;"

# 2. Check task has terminal event
sqlite3 ~/.hermes/kanban.db "SELECT id, kind FROM task_events WHERE task_id='t_xxx' AND kind IN ('completed','blocked','gave_up','crashed','timed_out');"

# 3. Verify both gateways running
ps aux | grep "hermes_cli.main" | grep -v grep

# 4. Check for crash loop errors
grep "Another gateway instance" ~/.hermes/logs/gateway.error.log | tail -5

# 5. Check notifier is active (look for dispatcher log)
grep "kanban dispatcher" ~/.hermes/logs/gateway.log | tail -3
```

**Also clean up done/blocked tasks:** After subscribing active tasks, remove subscriptions for completed tasks that no longer need monitoring. See `references/kanban-notifier-bugfix-20260613.md` for the full bugfix history and diagnostic procedures.
```bash
sqlite3 ~/.hermes/kanban.db "
DELETE FROM kanban_notify_subs
WHERE task_id IN (SELECT id FROM tasks WHERE status IN ('done','blocked','archived'));"
```

**Why cleanup matters:** Done tasks won't fire new events, so their subscriptions are dead weight. Keeping them causes confusion when checking `SELECT * FROM kanban_notify_subs`.

### Pitfall: Subscriptions Lost on Gateway Restart (Critical)

**Problem:** The `kanban_notify_subs` table gets cleared when the Gateway process restarts (WAL checkpoint or database re-initialization). All subscriptions are lost silently — no error, no log.

**Impact:** After any gateway restart, previously subscribed tasks will NOT receive completion notifications.

**Solution — Re-subscribe active tasks after restart:**
```bash
# Find active (non-done/non-archived) tasks
hermes kanban list --json 2>/dev/null | python3 -c "
import json, sys
for t in json.load(sys.stdin):
    if t.get('status') not in ('archived','done'):
        print(t['id'])" | while read tid; do
  sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs (task_id, platform, chat_id, thread_id, user_id, notifier_profile, created_at, last_event_id) VALUES ('${tid}', 'qqbot', '54D8D2AB6A48EE35127DD0F86081146A', '', 'binge', 'default', strftime('%s','now'), (SELECT COALESCE(MAX(id),0) FROM task_events));"
done
```

**Also clean up done tasks:** Done/blocked tasks don't need subscriptions:
```bash
sqlite3 ~/.hermes/kanban.db "
DELETE FROM kanban_notify_subs 
WHERE task_id IN (SELECT id FROM tasks WHERE status IN ('done','blocked','archived'));"
```

**When to re-subscribe:** After ANY of these events:
- `hermes gateway stop` + `hermes gateway start`
- `launchctl bootout` / `launchctl bootstrap` for gateway plist
- Config file restoration (.env, config.yaml)
- Database migration

### Pitfall: Gateway Notify Interval — Config vs Actual (Clarification)

**Config setting:** `gateway_notify_interval` in config.yaml (600s for default, 180s for shanli).

**Actual notifier poll interval:** The `_kanban_notifier_watcher()` function in `kanban_watchers.py` defaults to `interval: float = 5.0` seconds. The `gateway_notify_interval` config may control a different mechanism (e.g., dispatcher interval).

**The notifier only logs errors, not successes.** When it works, there's no log entry. When the table is missing, it logs: `kanban notifier tick failed: no such table: kanban_notify_subs`

**Verification approach:** Check if the subscription's `last_event_id` advances after a task completes. If it stays at the old value, the notifier isn't firing.

### 17. Tirith Auto-Install on Gateway Restart (2026-06-13)

**Problem:** Gateway startup calls `ensure_installed()` in `gateway/run.py:2112-2117`, which auto-downloads tirith security scanner from GitHub to `~/.hermes/bin/tirith`. After installation, tirith scans ALL terminal commands, including kanban commands with Chinese text, triggering "Confusable Unicode characters" approval prompts.

**Impact:** Every `hermes kanban create` with Chinese in the task title/body requires user approval, blocking the workflow.

**Root cause chain:**
```
Gateway restart → ensure_installed() → tirith downloaded → scans terminal commands
→ Chinese characters flagged as "Confusable Unicode" → approval required
```

**Fix:** Disable tirith in config.yaml:
```bash
sed -i '' 's/tirith_enabled: true/tirith_enabled: false/' ~/.hermes/config.yaml
```

**Note:** This is NOT caused by code changes to kanban_watchers.py. It's a side effect of restarting the Gateway, which triggers tirith installation.

### 18. Kanban Worker HTTP 401 — Profile .env Missing (2026-06-13)

**Problem:** Kanban worker crashes with `HTTP 401: Authentication Fails, Your api key is invalid` when the worker profile's `.env` file doesn't contain the required API key.

**Symptom:** Task shows `Agent crash x2: pid XXXX not alive` in diagnostics.

**Root cause:** Each kanban profile (e.g. `~/.hermes/profiles/lili/`) needs its own `.env` file with the API keys. The main `~/.hermes/.env` is NOT automatically inherited by profile workers.

**Fix:** Copy the main `.env` to the profile directory:
```bash
cp ~/.hermes/.env ~/.hermes/profiles/<profile_name>/.env
```

**Verification:** After fix, dispatch should succeed without 401 errors.

### 19. 多轮审核工作流（2026-06-14 实战验证）

**场景：** 小说整卷终审，需要多轮"审核→修复→再审核"循环。

**轮次模式：**
```
v1: 大莉M审核 → 发现6个P0问题
v2: 闪莉修复P0 → 发现内部标题未改
v3: 莉莉审核 → 发现频率未统一
v4: 闪莉修复频率+编号 → 发现诺亚身份残留
v5: 诺亚身份修复 → 发现第205章三重矛盾
v6: 第205章重写 → 发现"诺亚的弟弟"引用错误
v7: 修正引用 → 最终通过
```

**关键教训：**
- 每轮修复可能引入新问题，不要跳过审核
- P0修复任务body必须写明 `旧值→新值`（见下方第20条）
- 字符类修改（如"弟弟"→"丈夫"）必须用grep全卷扫描，不能只改显式引用
- 最终审核应覆盖8个维度（见下方审核维度清单）

### 20. 角色身份一致性检查（grep全卷扫描）

**场景：** 修改角色关系（如"弟弟"→"丈夫"）后，需要确认全卷一致。

**检查步骤：**
```bash
# 1. 搜索所有显式引用
grep -rn '弟弟诺亚\|萝莎的弟弟' 正文/

# 2. 搜索所有间接引用（"弟弟"在萝莎语境中）
grep -rn '弟弟' 正文/ | grep -i '萝莎\|诺亚\|她弟弟\|我弟弟'

# 3. 搜索称呼变化（"姐姐"→合适称呼）
grep -rn '姐姐' 正文/ | grep '诺亚'

# 4. 搜索矛盾表述（"没有丈夫"/"没有结过婚"）
grep -rn '没有丈夫\|没有结过婚' 正文/

# 5. 确认区分：同一角色的不同关系（如伊莱亚斯=萝莎的弟弟，诺亚=萝莎的丈夫）
grep -rn '弟弟伊莱亚斯\|我弟弟伊莱亚斯' 正文/
```

**常见陷阱：**
- 只改了"弟弟诺亚"连写，漏掉了单独的"弟弟"指代诺亚
- 改了称呼但没改年龄/背景描写（如"把他养大"暗示姐弟关系）
- 两稿拼接残留：同一章内矛盾表述并存

### 21. 全面终审维度清单（网文标准）

**8个审核维度：**

| 维度 | 检查方法 | 通过标准 |
|------|---------|---------|
| 剧情连贯性 | 逐章检查角色状态、时间线、因果链 | 无矛盾 |
| 对话质量 | 抽样精读，检查说教感/旁白感 | 自然流畅 |
| 上下文逻辑 | 设定一致性（频率、污染等级等） | 全卷统一 |
| AI味检测 | grep高频词（某种/仿佛/不禁等） | "某种"<60次/卷 |
| 字数检查 | Python统计纯汉字数 | 90%章节≥4500字 |
| 两稿拼接 | grep重复段落 | 0对重复 |
| 伏笔回收 | 对照大纲伏笔清单 | 核心伏笔已回收 |
| P0修复验证 | grep验证关键修复项 | 全部通过 |

**AI味高频词阈值：**
| 词语 | 阈值/卷 | 说明 |
|------|---------|------|
| "某种" | <60次 | 单章<5次 |
| "仿佛" | <10次 | |
| "不禁" | <5次 | |
| "宛如" | <5次 | |
| "嘴角微微上扬" | <3次 | |
| "般"比喻句 | <50次 | 高潮章可放宽 |

**字数标准：**
- 目标：4500-6000字/章（纯汉字）
- 底线：4000字（低于此为未完稿）
- 上限：7000字（超过需精简）
- 统计方式：`len(re.findall(r'[\u4e00-\u9fff]', content))`

### 22. 章节缺失分析（填不填？）

**场景：** 编号重排后出现空缺（如162-240中缺182和193）。

**决策流程：**
```
1. 检查前后章衔接是否自然
   → 181章结尾 vs 183章开头
   → 如果是场景/时间跳跃，通常不需要补

2. 检查废弃版本是否有对应内容
   → 废弃版本中可能有旧稿

3. 评估旧稿是否与当前剧情矛盾
   → 如旧稿写"医生被抓"但当前剧情医生是自由的，则矛盾

4. 决策：
   - 衔接自然 + 旧稿矛盾 → 不补
   - 衔接断裂 + 旧稿可用 → 参考旧稿补写
   - 衔接断裂 + 旧稿矛盾 → 需要全新补写
```

**本卷案例：**
- 第182章：181→183衔接自然（时间跳跃），废弃版本有严重文本重复 → 不补
- 第193章：192→194衔接自然（场景转换），废弃版本与当前剧情矛盾 → 不补

### 23. 修复任务必须指明修改方向（2026-06-14 教训）
**问题**：修复任务body写"诺亚身份统一"，执行者将"夫夫"改为"丈夫"，但实际需要的是"丈夫"→"弟弟"。

**解决**：修复任务body中每项修改必须写明 `旧值→新值`：
```
❌ "诺亚身份统一"
✅ "第233章第56行：'萝莎的丈夫'→'萝莎的弟弟'"
❌ "频率统一为16.9Hz"
✅ "全文搜索替换：'16.5赫兹'→'16.9赫兹'，'16.5Hz'→'16.9Hz'"
```

**Problem:** Kanban worker crashes with `HTTP 401: Authentication Fails, Your api key is invalid` when the worker profile's `.env` file doesn't contain the required API key.

**Symptom:** Task shows `Agent crash x2: pid XXXX not alive` in diagnostics.

**Root cause:** Each kanban profile (e.g., `~/.hermes/profiles/lili/`) needs its own `.env` file with the API keys. The main `~/.hermes/.env` is NOT automatically inherited by profile workers.

**Fix:** Copy the main `.env` to the profile directory:
```bash
cp ~/.hermes/.env ~/.hermes/profiles/<profile_name>/.env
```

**Verification:** After fix, dispatch should succeed without 401 errors.

### Pitfall: Chapter Renumbering Requires Updating BOTH File Names AND Internal Titles
**Problem:** When renaming chapter files to fix numbering gaps, the file names change but the internal markdown titles (`# 第XXX章：标题`) remain unchanged. This creates a mismatch where file says "第182章" but content says "# 第263章".

**Root Cause:** Only `mv` or `os.rename` was used on files; no script updated the first line of each file.

**Solution:** After renaming files, run a second pass to fix internal titles:
```python
import os, re
for f in sorted(os.listdir('.')):
    match = re.match(r'^第(\d+)章_(.+)', f)
    if not match: continue
    file_num = int(match.group(1))
    with open(f, 'r') as fh:
        first_line = fh.readline().strip()
    internal_match = re.search(r'第(\d+)章', first_line)
    if not internal_match: continue
    internal_num = int(internal_match.group(1))
    if internal_num != file_num:
        new_line = re.sub(r'第\d+章', f'第{file_num}章', first_line, count=1)
        with open(f, 'r') as fh:
            content = fh.read()
        content = content.replace(first_line + '\n', new_line + '\n', 1)
        with open(f, 'w') as fh:
            fh.write(content)
```

**Verification:** After renumbering, always run:
```bash
# Check internal vs file name mismatch
for f in 第*章_*.md; do
  fn=$(echo "$f" | sed 's/第\([0-9]*\)章.*/\1/')
  in=$(head -1 "$f" | sed 's/.*第\([0-9]*\)章.*/\1/')
  [ "$fn" != "$in" ] && echo "MISMATCH: $f"
done
```

**Pitfall:** The `sed` regex for extracting numbers from filenames can fail if the filename contains multiple "第" characters. Use Python for reliability.

### Pitfall: Multi-Version Chapter Cleanup
**Problem:** When chapters are rewritten multiple times (V1, V2, V3...), old versions remain in the directory. Same story beat appears at different chapter numbers.

**Solution:** 
1. Identify canonical versions (usually the latest/highest quality)
2. Move non-canonical to `正文_废弃版本/` directory
3. Renumber canonical files to be sequential
4. Update internal titles

**Verification:** After cleanup, check for:
- Duplicate chapter numbers (same number, different files)
- Missing chapter numbers (gaps in sequence)
- Internal title mismatches

**Problem:** User corrected agent for changing cron schedules, settings, or configurations without explicit confirmation.

**User's correction:** "不要擅自做决定" (Don't make decisions on your own)

**Solution:**
- **Cron schedules**: Always ask before changing frequency, delivery targets, or enable/disable status
- **Model/provider settings**: Always confirm before switching models or providers
- **File modifications**: Show analysis first, wait for "改" before executing
- **Configuration changes**: Present the change and its impact, wait for approval

**Workflow:**
```
1. Identify what needs to change
2. Present the proposed change with rationale
3. Wait for user confirmation ("好"/"改"/"可以")
4. Only then execute the change
```

**Exception:** User explicitly says "直接改" or "你来处理" in the original request.

#### 30. 修改任务必须走看板（2026-06-17 用户纠正）

**问题：** 用户要求修复章节时，我直接用 delegate_task 执行，而不是创建看板任务。用户纠正："为什么不是看板"。

**正确做法：** 所有修改任务（修复bug、修改文件、润色文本）都必须创建看板任务，不要直接 delegate_task。

**原因：**
- 看板任务有状态追踪（running/done/blocked）
- 看板任务有通知推送（QQ）
- 看板任务可重试（max_retries）
- 看板任务可归档留痕
- delegate_task 是同步的，任务完成即消失，无法追踪

**例外：** 用户明确说"你直接改"或"直接修"时，可以用 patch/execute_code 直接修改。

### 31. 主目录污染防护（2026-06-17 用户纠正）

**问题：** 我把未经终审的章节复制到正文主目录（/Users/libing/Desktop/weinMac/我在深渊事务所/正文/），用户纠正："只有确定的正文才放进去防止污染"。

**正确做法：**
- 闪莉初写 → 临时目录（/Users/libing/Desktop/临时文件-0001/脑洞文/正文_geminified/）
- Gemini精修 → 临时目录
- 莉莉审核 → 临时目录
- 大莉M终审 → 临时目录
- **只有终审通过后** → 才复制到主目录

**验证流程：**
1. 莉莉终审通过（8维度评分≥80）
2. 大莉M剧情矛盾审核通过（P0=0）
3. 用户确认"放进去"
4. cp 到主目录

### 32. 不要轮询/盯着看板任务（2026-06-17 用户纠正）

**问题：** 我用 sleep + hermes kanban show 反复轮询任务状态，用户纠正："订阅就行不用看着"。

**正确做法：**
1. 创建任务后立即订阅通知（kanban_notify_subs）
2. 告诉用户"等修完QQ会推通知"
3. 不要 sleep + poll 循环
4. 用户说"看一下"时才检查状态

**原因：**
- 订阅后 Gateway 每5秒自动检查，完成即推送
- 轮询浪费资源且无意义
- 用户不想看到中间状态

## Pitfall: Parallel Writing Batches Cause Worldbuilding Drift
**Problem:** When writing chapters in parallel batches (e.g., batch A writes 334-345, batch B writes 346-378), later batches may hallucinate entirely different worldbuilding — introducing organizations, locations, and technology that don't exist in the original setting.

**Symptoms:**
- Keywords like "西区/深渊/裁决所/黑巫师/蒸汽步枪" appear in chapters that should be about "雾港/共济会/金齿轮封印"
- Characters suddenly have different abilities, roles, or backgrounds
- The story diverges into a completely different genre

**Root Cause:** Parallel kanban workers don't read ALL previous chapters — they only read the immediately preceding chapter. If the task body doesn't explicitly include worldbuilding constraints, workers invent their own setting.

**Prevention — Add explicit worldbuilding constraints to EVERY writing task:**
```
## 世界观（必须严格遵守）
禁止词：[list of words that MUST NOT appear]
正确设定：[list of correct worldbuilding elements]
```

**Detection — After parallel batches complete, grep for forbidden keywords:**
```bash
for i in $(seq START END); do
  f=$(ls 第${i}章_*.md 2>/dev/null | head -1)
  [ -n "$f" ] && bad=$(grep -c "FORBIDDEN_KEYWORD" "$f") && [ "$bad" -gt 0 ] && echo "❌ 第${i}章: ${bad}处"
done
```

**Fix:** Delete affected chapters, add worldwriting constraints to task body, rewrite in sequential batches (not parallel).

## Pitfall: Kanban Worker Saves File Without Title Suffix
**Problem:** Worker saves chapter as `第XXX章.md` instead of `第XXX章_标题.md`, causing glob patterns `第${i}章_*.md` to miss the file.

**Detection:**
```bash
ls 第${i}章.md 2>/dev/null  # exists but 第${i}章_*.md doesn't
```

**Fix:** After each batch, check for files without title suffix and rename:
```bash
title=$(head -1 "第${i}章.md" | sed 's/# //')
newname=$(echo "$title" | sed 's/：/_/')
mv "第${i}章.md" "${newname}.md"
```

## Pitfall: LongCat Token Exhaustion Blocks Writing Pipeline
**Problem:** LongCat model has daily token limits. When tokens run out, all kanban writing tasks fail.

**Solution — Have backup providers ready:**
1. Gemini web2api (gemini-web2api at localhost:8081) — works for writing but NOT for kanban workers (no tool calling support)
2. DeepSeek V4 Flash — cheap, good Chinese, works with kanban
3. Xiaomi MiMo — already configured

**When LongCat exhausts:** Switch shanli profile to DeepSeek or use Gemini via script (not kanban) for writing.

## Pitfall: Gemini Web2API Doesn't Support Tool Calling
**Problem:** gemini-web2api reverse proxy works for raw text generation but kanban workers crash because Gemini doesn't support function/tool calling.

**Symptoms:** Worker exits with "Model returned empty after tool calls" or HTTP 401.

**Solution:** Use Gemini via direct script (execute_code/terminal) for writing, NOT via kanban worker. Kanban workers need DeepSeek or LongCat which support tool calling.

## Pitfall: Duplicate Kanban Tasks on Same Chapter
**Problem:** When dispatching tasks for chapters that depend on each other, duplicate tasks may be created for the same chapter number.

**Prevention:** Check `hermes kanban list` before dispatching. If a task for the same chapter already exists (running or ready), don't create another.

**Problem:** Passing long task bodies with quotes, newlines, or special characters via shell variable (`BODY=$(cat ...); hermes kanban create --body "$BODY"`) often fails silently — shell expansion mangles quotes, backticks, and `$` signs.

**Solution:** Use `write_file` to create a temp file, then `cat` it inline:

```python
# Step 1: Write body to temp file
write_file(path="/tmp/kanban_body.txt", content=long_body_with_quotes_and_newlines)

# Step 2: Use cat in terminal (NOT shell variable)
terminal(command='hermes kanban create --body "$(cat /tmp/kanban_body.txt)" --assignee shanli --workspace "dir:/path" "Title"')
```

**Why not shell variables:** Bash `$BODY` expansion breaks on:
- Single/double quotes inside the body
- Backticks and `$(...)` command substitutions
- `$` signs (interpreted as variable references)
- Newlines in some shells

**Pattern:** Always use file-based body passing for tasks with >100 words or any special characters.

### Pitfall: Cronjob Tool Rejects Symlinked Scripts (2026-06-15)

**Problem:** When restoring cron jobs that reference scripts (e.g., `nv_ping.py`), creating symlinks in `~/.hermes/scripts/` causes the cronjob tool to reject them with `Script path escapes the scripts directory via traversal`.

**Root cause:** The cronjob tool has a security check that rejects symlinks — it resolves the symlink target and validates the real path is within `~/.hermes/scripts/`. Symlinks pointing outside this directory are blocked.

**Solution:** Copy the actual script files instead of creating symlinks:
```bash
# ❌ WRONG — symlink rejected
ln -sf ~/.hermes/skills/productivity/nv-multi-model/scripts/nv_ping.py \
       ~/.hermes/scripts/nv_ping.py

# ✅ CORRECT — copy actual file
cp ~/.hermes/skills/productivity/nv-multi-model/scripts/nv_ping.py \
   ~/.hermes/scripts/nv_ping.py
chmod +x ~/.hermes/scripts/nv_ping.py
```

**Why this matters:** Scripts referenced by cron jobs must be actual files in `~/.hermes/scripts/`, not symlinks to files elsewhere. This is a security feature to prevent path traversal attacks.

**Verification:** After copying, check that the cronjob tool accepts the script:
```bash
# The script should be a regular file, not a symlink
file ~/.hermes/scripts/nv_ping.py
# Should show: Python script text executable (not "symbolic link to ...")
```

### Pitfall: Dispatch Takes No Arguments

**Problem:** `hermes kanban dispatch <task_id>` fails with "unrecognized arguments" — dispatch doesn't accept task IDs.

**Solution:** `hermes kanban dispatch` dispatches ALL ready tasks. Use `--max N` to limit:

```bash
# Dispatch all ready tasks (up to 3)
hermes kanban dispatch --max 3

# Check what would be dispatched without spawning
hermes kanban dispatch --dry-run
```

### 33. Parallel Writing Worldbuilding Drift (Critical — 2026-06-25)

**Problem:** When writing novel chapters in parallel batches, workers completely ignore the worldbuilding constraints in the task body. Chapters end up with wrong settings, organizations, and character descriptions that don't match the original story.

**Symptoms:**
- Chapters introduce non-existent locations (e.g., "西区" instead of "雾港")
- Characters gain wrong abilities (e.g., "蒸汽步枪" instead of "差分机")
- New organizations appear (e.g., "裁决所""黑巫师" instead of "共济会三派")
- The task body explicitly forbids these terms, but workers ignore them

**Root Cause:** The kanban worker's LLM doesn't reliably follow negative constraints ("不要写X") in task bodies, especially when the prompt is long and complex.

**Solution — Explicit Red Lines in Every Task Body:**
```
## 世界观红线（违反即为废稿）
- 地点=雾港（地面工业城市）
  禁止：西区/中城区/深渊/黑雾/圣母广场/北方军团/黄昏事务所
- 组织=共济会三派（温和派/激进派/纯理性派）
  禁止：裁决所/黑巫师/圣光骑士团
- 技术=金齿轮封印/朔月力量/差分机
  禁止：蒸汽步枪/畸变者
```

**Post-Completion Verification (Mandatory):**
After each batch completes, run a grep check before proceeding:
```bash
for i in $(seq START END); do
  f=$(ls 第${i}章_*.md 2>/dev/null | head -1)
  [ -z "$f" ] && echo "❌ 第${i}章: 缺失" && continue
  bad=$(grep -c "FORBIDDEN_KEYWORDS" "$f")
  [ "$bad" -gt 0 ] && echo "❌ 第${i}章: 跑偏${bad}处" || echo "✅ 第${i}章"
done
```

**Lesson:** Never trust parallel writing tasks to follow worldbuilding constraints without verification. Always check after completion.

## Task Body Best Practices

1. **Clear chapter/section references:** "第163-170章" not "第1-8章" — vague numbering causes wrong chapter generation
2. **Relative file paths:** "保存到：正文/ 目录下" not absolute paths — avoids path confusion when workspace is project root
3. **Specific modification targets:** Include line numbers for deletions when possible
4. **Completion criteria:** Define what "done" looks like
5. **Output format:** Specify what reports/artifacts to produce
6. **Pre-load key context:** Include outline summaries and guidelines directly in task body to reduce file reads

### 7. Anti-Concatenation Constraint (Critical for Writing Tasks)

**Problem:** AI generates two versions of the same chapter content, resulting in "两稿拼接" (two-draft concatenation) — 60-75% of chapters affected in Vol 4.

**Root Cause:** Writing task lacks explicit prohibition against generating multiple versions.

**Solution:** Add explicit anti-concatenation constraint to writing task body:

```
⚠️ 严禁两稿拼接：每章只生成一个版本，不要重复生成相同内容。
如果发现内容重复，立即删除重复部分。
写完一章后检查是否有重复段落。
```

**Why it matters:**
- Vol 3 (with detailed task requirements): 0 concatenation issues
- Vol 4 (with minimal task requirements): 6/8 chapters with concatenation
- The difference: Vol 3 had explicit constraints, Vol 4 did not

### 8. Detailed Task Structure (Vol 3 vs Vol 4 Comparison)

**Vol 3 Task Structure (Successful):**
```
1. 核心策略：读取范围、写作范围、审核流程
2. 必须读取的文件（按优先级）
3. 写作要求（章节范围、大纲元素、字数、风格、角色名规范）
4. 执行步骤（8步详细流程）
5. 审核流程（5步详细说明）
6. 品质要求（检查字数、检查拼接）
```

**Vol 4 Task Structure (Failed):**
```
1. 简单的字数要求
2. 大纲概要
3. 关键承接说明
4. ai写作注意事项要点
```

**Key Differences:**
| Element | Vol 3 | Vol 4 | Impact |
|---------|-------|-------|--------|
| Read scope | ✅ "前30章" | ❌ Not specified | Worker reads wrong files |
| File paths | ✅ Absolute paths | ⚠️ Relative only | Worker searches, gets confused |
| Writing style | ✅ 5 detailed rules | ❌ Only guidelines | No specific guidance |
| Execution steps | ✅ 8-step flow | ❌ None | Worker skips checks |
| Review process | ✅ 5-step detail | ⚠️ Simple hint | Incomplete fixes |
| Anti-concat | ❌ Not explicit | ❌ Not explicit | Concatenation explosion |

### 9. Writing Task Template (Best Practice)

```bash
hermes kanban create "第X卷第Y批写作（第A-B章）" \
  --assignee shanli \
  --workspace "dir:/path/to/project" \
  --body "## 任务：写《书名》第X卷第Y批章节（第A-B章）

### 核心策略
- **读取范围**：本批次之前的所有章节（第X-A-1章）
- **写作范围**：第A-B章（共N章，全部新写）
- **审核流程**：写完N章 → 莉莉审核 → 修改 → 直到没有问题 → 继续写下一批

### 一、必须读取的文件（按优先级）
#### 1. 大纲文件（最高优先级）
- /path/to/大纲.md
#### 2. 前文正文
- /path/to/正文/第X章_标题.md
- ...（依次读取到第Y-1章）

### 二、写作要求
#### 章节范围
- 第A章：标题
- 第B章：标题
#### 每章字数
- 纯汉字数 4500-5500字（⚠️ 必须用Python统计汉字数，不用wc -m）
- 不超过6000字
#### 写作风格
- 短段落，动作展示
- 不升华收尾
- 对话自然，不说教
- 去AI味
#### ⚠️ 严禁两稿拼接
- 每章只生成一个版本
- 写完一章后检查是否有重复段落

### 三、角色名规范
- 去姓：杰克、乔治...
- 全名：瓦尔特、瓦伦...

### 四、执行步骤
1. 读取大纲，理解剧情走向
2. 读取前文，了解前情和风格
3. 逐章写作（每章只生成一个版本）
4. 每写完一章，检查是否有重复内容
5. 保存到输出目录
6. 完成后输出完成报告

### 五、审核流程
1. 完成N章后，等待莉莉审核
2. 莉莉审核维度：字数/大纲/风格/拼接
3. 根据审核意见修改
4. 修改后再次提交审核
5. 直到没有问题，才能继续写下一批

### 六、品质要求
- 每章写完后检查字数
- 每章写完后检查是否有两稿拼接"

## Workflow Patterns

### 10. Writing Pipeline Flow (Clarified 2026-06-13)

**User correction:** 大莉M终审 is ONLY for the final review of the ENTIRE volume, not each batch.

**Per-batch flow:**
```
闪莉写 → 莉莉审 → (有问题→Agnes改→莉莉复审→循环) → 通过 → 下一批
```

**Volume-end flow:**
```
所有批次完成 → 大莉M终审（整卷最终审核）
```

**Key distinction:** 莉莉 handles per-batch review/fix cycles. 大莉M only appears ONCE at the very end of a volume for the final quality gate.

### 10a. Sequential Task Dispatch Pattern (2026-06-18 verified)

**场景：** 写作任务有依赖关系（批次2需要读批次1的产出），需要顺序执行。

**做法：** 一次性创建所有任务，但只dispatch第一个。后续任务等前一个完成后自动dispatch。

```bash
# 创建3个任务（全部ready）
T1=$(hermes kanban create "批次1" --assignee shanli ... | grep -o 't_[a-f0-9]*')
T2=$(hermes kanban create "批次2" --assignee shanli ... | grep -o 't_[a-f0-9]*')
T3=$(hermes kanban create "批次3" --assignee shanli ... | grep -o 't_[a-f0-9]*')

# 订阅所有任务
for tid in $T1 $T2 $T3; do
  sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs ..."
done

# 只dispatch第一个
hermes kanban dispatch --max 1
```

**后续dispatch：** 等T1完成（QQ通知推送），手动dispatch T2：
```bash
hermes kanban dispatch --max 1
```

**⚠️ 注意：** 不要等冰哥说"看一下"才检查状态。订阅了QQ通知后，完成时会自动推送。

### 11. Auto-Schedule Review After Writing Completes (Critical)

**Problem:** Writing task completes, agent reports results but does NOT proactively schedule the review task. User has to ask "安排莉莉审核了嘛？" — breaking the expected write→review→fix→next-batch flow.

**Root Cause:** Agent treats writing completion as the end of the task, instead of the midpoint of the batch workflow.

**Solution:** When reporting writing completion, IMMEDIATELY present the review task plan and ask for confirmation (or dispatch directly if user said "明天早上我来看结果"):

```
Writing task completes
  → Report results (word count, quality summary)
  → "审核任务已安排" / "要安排莉莉审核吗？"
  → Create review kanban task (--assignee lili)
  → Dispatch review
  → Report review results
  → If issues found: create fix task (--assignee shanli)
  → Loop until pass → then create next batch
```

**铁律：** 写作完成 ≠ 任务完成。写作完成只是 batch workflow 的第一步。报告写作结果时必须同时安排审核。

### 11. Pre-Read Requirement in Every Writing Task Body (Critical)

**Problem:** Kanban writing task body only says "read previous chapter" — flash worker produces content disconnected from 20+ chapters of context (wrong character states, repeated events, style drift).

**User's correction:** "这次看板有没有预读前20章等第三卷的要求"

**Solution:** EVERY writing task body (not just the first batch) must include a pre-reading section:

```
## ⚠️ 重要：预读前文要求（必读）
1. 上一章正文（精读）
2. 前20章正文（跳读标题+开头/结尾段落）
3. 前一卷最后5章（了解卷末承接）
4. 本批次大纲（精读）
5. ai写作注意事项（快速浏览）
6. 角色设定文件（按需读取）
```

**Why every batch, not just the first:**
- Flash worker has NO memory between sessions — each batch is a fresh start
- Character states, ongoing events, and style patterns need continuous reinforcement
- The pre-read section is the ONLY way to maintain cross-batch consistency

---

### 24. 大纲先行验证（写作前必做）

**场景：** 开始新卷写作前，先验证大纲一致性，再动手写。

**用户指令：** "先统一大纲，确认大纲这件没有冲突"

**验证流程：**
```
1. 读取新卷大纲全文
2. 检查角色设定是否与前卷一致（如诺亚=丈夫/弟弟）
3. 检查时间线是否连贯
4. 检查设定数据是否一致（频率、污染等级等）
5. 检查情节点顺序是否合理
6. 确认无冲突后才开始写作
```

**案例：** 第五卷大纲写"诺亚=弟弟"，但第四卷正文已确立"诺亚=丈夫"。写作前发现并统一为"丈夫"，避免了全卷返工。

### 25. 大纲编号 vs 正式编号映射（写作任务必须明确）

**问题：** 大纲使用卷内编号（第22章、第23章...），但正文输出需要正式编号（第261章、第262章...）。Worker读了大纲后搞混，把"大纲第22章：伊莲娜·灰羽"写成了"第266章：伊莲娜·灰羽"（应该是第261章）。

**根因：** 任务body没有明确说明大纲编号到正式编号的映射关系。Worker直接用了大纲的编号。

**解决方案：** 在写作任务body中加入明确的映射表：

```
⚠️ 重要：大纲使用"卷内编号"，正文使用"正式编号"。本任务要求按"正式编号"输出。

### 编号映射表（必须严格遵守）
| 大纲编号 | 正式编号 | 章节标题 |
|---------|---------|---------|
| 第22章 | 第261章 | 伊莲娜·灰羽 |
| 第23章 | 第262章 | 酒杯中的谋杀 |
| ... | ... | ... |

### 文件命名规则
- 文件名：第{正式编号}章_{标题}.md
- 内部标题：# 第{正式编号}章：{标题}
⚠️ 绝对不能用大纲编号命名文件！
```

**验证：** 写作完成后检查文件名和内部标题一致性：
```python
for i in range(start, end+1):
    files = glob.glob(f"第{i}章_*.md")
    if files:
        with open(files[0]) as fh:
            first_line = fh.readline().strip()
        match = re.search(r'第(\d+)章', first_line)
        if match and int(match.group(1)) != i:
            print(f"MISMATCH: 第{i}章 ≠ {first_line}")
```

**何时使用：** 每次写作任务的正式编号与大纲编号不同时（即所有新卷写作，因为大纲用卷内编号）。

**26. 卷内编号在大纲中使用**

**场景：** 大纲中的章节编号应使用卷内顺序（第1章、第2章...），而非正式编号（第241章、第242章...）。

**用户指令：** "大纲里章节号不要用正式的编号用卷内顺序编写出来在按顺序编号"

**原因：**
- 正式编号在扩写/重编号时会频繁变化
- 卷内编号稳定，不受跨卷编号影响
- 大纲是写作参考，不是最终发布版本

**格式：**
```
❌ 第241章：下潜——沉钟升降舱
✅ 第1章：下潜——沉钟升降舱
```

### 26. 全面审核偏好（非分批）

**场景：** 用户偏好一次性审核全部章节，而非分批审核。

**用户指令：** "不要分批进行直接一起输出一个报告"

**原因：** 分批审核可能遗漏跨章节的剧情矛盾、角色状态不一致等问题。全面审核能发现系统性问题。

**实现：** 审核任务body中明确写"审核范围：全卷N章，一次性输出一份完整报告"。

---

## 主角团信息卡（跨卷一致性保障）

当需要创建角色设定参考文档时，参考 `references/character-info-card.md`。

核心要点：
- 每个新卷写作前必须创建/更新主角团信息卡
- 信息卡包含：角色设定、写作红线、世界观、衔接状态
- 写作任务body中必须将信息卡列为"必须读取"文件
- 跨卷审核时对照信息卡逐项验证

## 章节重编号与版本管理

当需要批量重编号小说章节或管理多版本文件时，参考 `references/chapter-renumbering.md`。

核心要点：
- 重编号用TEMP_两步法避免冲突
- 内部标题（# 第XXX章）必须与文件名同步
- 废弃版本移到 `正文_废弃版本/` 目录，不要删除
- 重编号后必须让冰哥确认

## Gemini精修流水线

当需要对闪莉初写版进行文本精修（禁用词清理、高频词控制、去AI味）时，参考 `references/gemini-refinement-pipeline.md`。

核心流程：闪莉初写 → Gemini精修 → Python脚本清理高频词 → 莉莉审核 → 移入主目录

**⚠️ Gemini精修的局限性（2026-06-18 实测）：**
- Gemini可能**引入**禁用词（如"仿佛"），不是只删不加
- "一种"等高频词Gemini难以完全清零（多轮精修仍有残留）
- 建议流程：Gemini精修 → Python脚本强制清理残留 → 莉莉审核
- shanliG profile（Gemini 3.5 Flash @ localhost:8081）已配置，可直接使用

**gemini-web2api（将Gemini网页版转为API）：** 参考 `references/gemini-web2api-setup.md`
- GitHub: Sophomoresty/gemini-web2api (1.8k stars)
- 本地服务器 localhost:8081，OpenAI兼容格式
- shanliG profile已配置指向该服务器
- 用途：LongCat额度用完时，用Gemini网页版额度继续写作

**⚠️ 关键限制（2026-06-23 实测）：**
- **不支持function calling** → kanban worker会崩溃（空响应）→ 必须用Python脚本直接调API
- **字数控制差** → 输出7000-10000字（目标4500-5500）→ 需要严格prompt+多轮精简
- **反向工程产物** → 不是官方API，Google随时可能封禁
- **安全风险** → 必须绑定127.0.0.1，设置api_keys

**Hybrid写作工作流（Gemini不可用kanban时）：**
```
1. Python脚本调Gemini API写章节 → 保存到工作目录
2. kanban create --assignee lili → 莉莉审核
3. 审核不通过 → Python脚本再改 → 再审
4. 循环最多3轮 → 断路器触发问冰哥
```
- 写作用脚本（`~/.hermes/scripts/gemini_write_chapter.py`），不走kanban worker
- 审核仍走kanban（lili用DeepSeek）
- 每批只写2章（Gemini字数膨胀严重，8章迭代预算容易耗尽）

## macOS Terminal Control

For interacting with foreground terminal applications (MiMo Code, SSH, etc.), see `references/macos-terminal-control.md` — AppleScript-based technique for sending input to Terminal.app windows. Includes Chinese text input via clipboard paste method.

## Agent-Reach (Internet Access for AI Agents)

Agent-Reach gives AI agents free internet access to Twitter, YouTube, GitHub, Bilibili, etc. See `references/agent-reach-setup.md` for installation and usage.

## Novel Chapter File Naming

See `references/novel-chapter-naming.md`. Key: filenames must have title suffix (`第{ch}章_{标题}.md`), internal titles use colon format.

## NV Ping Debugging

See `references/nv-ping-debugging.md`. Key pitfalls: URL double-append, empty groups death spiral, model deprecation.

## Hermes Skills Hub

Hermes has a built-in Skills Hub with 92,109+ skills (97 official). Browse, search, and install skills via `hermes skills browse/search/install`. See `references/hermes-skills-hub.md` for details.

**Quick start:**
```bash
# Check available platforms
/tmp/agent-reach-env/bin/agent-reach doctor

# Extract browser cookies for Twitter/XHS
/tmp/agent-reach-env/bin/agent-reach configure twitter-cookies --from-browser chrome
```

**Current status (2026-06-13):** 12/13 platforms available (GitHub, YouTube, Twitter, Reddit, 小红书, 小宇宙, 雪球, Bilibili, V2EX, RSS, any webpage, 全网搜索). Only LinkedIn requires complex MCP setup.

## Hermes Workspace

Hermes Workspace 是独立的 Web UI 项目（端口 3000），不是 hermes dashboard（端口 9119）。
代码位置：`/Users/libing/hermes-workspace/`，启动：`bash start.sh`。
当用户说"web工具"或"web插件"时，可能指的是 Workspace。
详见 `references/hermes-workspace.md`。

## MiMo Code Integration

MiMo Code (小米AI编程助手, based on OpenCode) can be controlled programmatically via a Hermes plugin. For custom provider configuration (e.g., Agnes API), see `references/mimocode-custom-provider.md`.

**Plugin location:** `~/.hermes/plugins/mimo-code/`

**Available tools:**
- `mimo_task` — One-shot: auto-start server, send task, get result
- `mimo_server_start/stop/status` — Server management
- `mimo_session_create/prompt/messages/abort/list` — Session management

**Usage pattern:** When user says "让 mimo 写..." or "用 mimo 修改...", call `mimo_task` tool. The plugin handles server lifecycle automatically.

**MiMo Code server mode:** `mimo serve --port 3000` (headless server)

---

## External AI Providers

For using external AI models (FreeModel, etc.) with Hermes, see `references/freemodel-api.md` — covers OpenAI vs Anthropic format endpoints, Claude Code integration, and common pitfalls.

## Dual-Gateway Architecture Fix

For fixing dual-gateway issues (Telegram polling conflict, model switching, cron job loss), see `references/dual-gateway-fix.md` — complete step-by-step repair procedure with verification checklist.

## Multi-AI Review Pattern

For complex infrastructure issues, use multiple independent AI analyses:

```text
大莉M (mimo-v2.5-pro)  → 出方案
大莉D (deepseek-v4-pro) → 审核方案
外部AI (FreeModel/etc)  → 独立验证
→ 汇总共识和分歧 → 最终方案
```

User preference: review before fixing (先审核), then routine fixes can be confirmed with just ok.

### External AI for Editing Tasks

When internal agents (闪莉/Agnes) produce unsatisfactory results, use FreeModel's GPT-5.5 for precise editing:

```python
delegate_task(
    goal="修复第X-Y章的P0问题...",
    model="custom:FreeModel GPT-5.5",
    context="文件位置：/path/to/正文/",
    toolsets=["terminal", "file"]
)
```

**When to use GPT-5.5 instead of 闪莉/Agnes:**
- Precise text fixes (repetition removal, word count adjustment)
- Independent validation of internal agent output
- When user explicitly requests external AI

**Note:** The custom:FreeModel GPT-5.5 provider uses local mimo-v2.5-pro for execution, not actual GPT-5.5. For true external AI, use execute_code to call the API directly.

## File Management Patterns

### Report File Organization

**Problem:** Review/writing/modification reports clutter the main content directory.

**Solution:** Create a dedicated reports folder and move all reports there.

```bash
# Create reports folder
mkdir -p "/path/to/project/小说检查报告"

# Move reports after task completion
mv /path/to/project/正文/*报告*.md /path/to/project/小说检查报告/
mv /path/to/project/*报告*.md /path/to/project/小说检查报告/
```

**Convention:**
- All review/writing/modification reports → `小说检查报告/`
- Only chapter files remain in `正文/`
- Keep project root clean

### Temporary File Cleanup

**Problem:** Kanban workers generate temporary Python scripts (check_*.py, fix_*.py, verify_*.py) that clutter the project.

**Solution:** Clean up temporary files after task completion.

```bash
# Delete temporary Python scripts
rm /path/to/project/*.py
rm /path/to/project/脑洞文/*.py
```

**When to clean:**
- After each batch of writing/modification
- Before user review
- When user explicitly asks

### Bulk Archive All Done Tasks (Quick Cleanup)

**Problem:** Board accumulates dozens of done tasks, making it hard to see active work.

**Solution:** One-liner loop to archive all done tasks at once:

```bash
# Archive all done tasks in one shot
DONE_IDS=$(hermes kanban list 2>/dev/null | grep "✓" | awk '{print $2}')
for id in $DONE_IDS; do hermes kanban archive "$id" 2>/dev/null; done
echo "Archived $(echo $DONE_IDS | wc -w) tasks"
```

**After cleanup, verify:**
```bash
hermes kanban list 2>/dev/null  # Should show only active/blocked tasks
```

**Optional: permanently delete archived tasks too:**
```bash
hermes kanban archive --rm $DONE_IDS
```

### Kanban Task Deletion (CLI Method)

**Problem:** `hermes kanban remove` does not exist — the correct workflow uses `archive` + `archive --rm`.

**Solution:** Two-step deletion:

```bash
# Step 1: Archive the tasks
hermes kanban archive t_xxx t_yyy t_zzz

# Step 2: Permanently delete archived tasks
hermes kanban archive --rm t_xxx t_yyy t_zzz
```

**Pitfall:** `hermes kanban remove` → "invalid choice" error. Always use `archive` then `archive --rm`.

### Pitfall: Cron Job Time Conflicts

**Problem:** Multiple cron jobs scheduled at the same time (e.g., both at :00) can cause delivery conflicts or missed notifications.

**Example:** Kanban notifier (`*/15`) and drink water reminder (`*/20`) both fire at :00, causing simultaneous QQ messages that may overlap or confuse the user.

**Solution — Offset schedules:**
```bash
# Kanban: fires at :00, :15, :30, :45
hermes cron update <job_id> --schedule "*/15 * * * *"

# Drink water: fires at :05, :25, :45 (offset by 5 minutes)
hermes cron update <job_id> --schedule "5/20 9-19 * * *"
```

**Alternative:** If user prefers fixed schedules, accept the occasional overlap and let both messages arrive naturally. Always ask user before changing schedules.

**When to use:** Cleaning up blocked/obsolete tasks that are no longer needed (e.g., old batches already completed, superseded plans, test tasks).

**Verification after cleanup:**
```bash
hermes kanban list 2>/dev/null | grep -v done  # Should show nothing or only active tasks
```

### Kanban Database Cleanup (Archived Tasks)

**Problem:** The Workspace Tasks view (port 3000) shows "archived" tasks as "Triage" (47 tasks visible). Over time, completed research tasks, old writing tasks, and test tasks accumulate, making the board cluttered. User said: "除了自动其他的都删除".

**Root Cause:** Tasks with `status = 'archived'` in the kanban SQLite database appear as "Triage" in the Workspace Tasks web UI. These are tasks that were completed long ago but never cleaned up.

**Solution:** Identify cron-related tasks (keep) vs historical tasks (delete), then clean up via direct SQLite operations.

```python
import sqlite3

db_path = '/Users/libing/.hermes/kanban.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. Check what's in archived
c.execute("SELECT id, title, body FROM tasks WHERE status = 'archived'")
tasks = c.fetchall()
print(f"Archived tasks: {len(tasks)}")

# 2. Identify cron tasks (keep these)
cron_ids = []
for id, title, body in tasks:
    body_str = str(body) if body else ''
    if 'Cron' in body_str or 'cron' in body_str or '关联Cron' in body_str:
        cron_ids.append(id)
        print(f"  KEEP: [{id}] {title}")

# 3. Delete non-cron archived tasks
c.execute(f"DELETE FROM tasks WHERE status = 'archived' AND id NOT IN ({','.join(['?' for _ in cron_ids])})", cron_ids)
deleted = c.rowcount
conn.commit()
print(f"Deleted {deleted} non-cron archived tasks")

# 4. Verify
c.execute("SELECT COUNT(*) FROM tasks WHERE status = 'archived'")
remaining = c.fetchone()[0]
print(f"Remaining archived: {remaining}")
conn.close()
```

**Key insight:** Cron tasks have "关联Cron: <hex_id>" in their body field. All other archived tasks are safe to delete.

**When to clean:**
- When user complains about "很多我没布置的任务" in the Triage column
- Periodically as maintenance
- When the Workspace Tasks view shows excessive Triage count

**Verification after cleanup:**
```bash
hermes kanban stats  # Should show triage: 0
```

### 11. Writing Progress Check Pattern (Read-Only)

**Problem:** User asks "写作进度怎么样" or "闪莉改完了吗" — need to quickly assess status across multiple batches without modifying anything.

**Solution:** Three-step status check:

```bash
# 1. Kanban task status — find blocked/done/active tasks
hermes kanban list 2>/dev/null | grep -E "(blocked|active|pending|done)" | grep -E "(第四卷|写作|修改|审核)"

# 2. File modification dates — see what was actually written/modified recently
ls -lt "/path/to/正文/" | head -20

# 3. Specific blocked task details
hermes kanban show <task_id> 2>/dev/null | head -20
```

**Status report template:**
```
📊 第X卷写作进度总览
| 批次 | 章节 | 字数 | 写作 | 审核 | 修改 | 状态 |
|------|------|------|------|------|------|------|
| 第N批 | A-B章 | XXXXX字 | ✅ | ✅ | ✅/⚠️ | 完成/卡住 |

⚠️ 卡住原因：[LongCat额度不足/协议违规/etc]
📄 正文文件情况：[版本数/最新修改时间]
🔴 未完成工作：[剩余章节/待重试任务]
```

**Word count display preference (冰哥):** When reporting chapter completion or progress, ALWAYS include per-chapter word counts. Format: `第XXX章: NNNN 字`. This applies to:
- Progress checks ("好了吗")
- Completion reports ("写作完成")
- Review summaries
- Any time listing chapter files

**⚠️ 必须使用纯汉字数（汉字数），不是总字符数：**
- `wc -m` 统计的是总字符数（含标点、空格、换行），不是网文标准字数
- 网文标准字数 = 纯汉字数（Unicode 4E00-9FFF 范围内的汉字）
- 差距可达 20-30%（如总字符4500 vs 汉字数3400）

**正确统计方式（Python）：**
```python
import re
with open('文件路径') as f:
    content = f.read()
hanzi = len(re.findall(r'[\u4e00-\u9fff]', content))
print(f"纯汉字数: {hanzi}")
```

**常见错误：**
- ❌ `wc -m < file.md` → 总字符数（含标点空格）
- ❌ `wc -c < file.md` → 字节数
- ✅ Python `re.findall(r'[\u4e00-\u9fff]')` → 纯汉字数

**Key signals to look for:**
- `blocked` tasks with crash diagnostics → check `hermes kanban log <task_id>` for root cause
- Duplicate chapter files (e.g., `第230章_灯塔对决.md` + `第230章_主灯塔对决.md`) → old vs new versions, clean up old ones
- File modification dates → confirm if modifications actually happened

### 12. MiMo Code as Writing Alternative (2026-06-13 实测)

**MiMo Code 可以作为写作/修改的替代工具，但质量不如闪莉。**

**实测对比（第284-285章）：**
| 指标 | MiMo Code | 闪莉 |
|------|-----------|------|
| 写作速度 | 较慢（列文件耗时） | 快 |
| 字数控制 | 不稳定（285章只有2307字） | 稳定（全部4500+） |
| AI高频词 | 较差（像18次、某种7次） | 较好（修改后全部达标） |
| 速率限制 | 有（限免版触发Too many requests） | 无 |
| 适合场景 | 简单修改、测试 | 正式写作、批量修改 |

**MiMo Code 速率限制问题：**
- 触发条件：连续编辑多个文件
- 症状：`Too many requests esc interrupt`
- 解决：等几分钟重试，或用脚本直接改

**MiMo Code 模型限制：**
- MiMo Code 只支持小米自己的模型（mimo-auto/mimo-v2.5等）
- 不支持外部模型如 Agnes、DeepSeek、Claude 等
- 无法通过 `mimo providers login` 添加自定义 provider（有 bug）
- 如果需要使用其他模型，应直接用 API 或 Hermes 子代理

**使用方式：** 当冰哥说"让mimo写..."时，调用 `mimo_task` 工具。但正式写作任务仍推荐用闪莉。

### 12b. Gemini via Script as Writing Alternative (2026-06-23 实测)

**场景：** LongCat额度耗尽，用gemini-web2api+Python脚本替代闪莉做写作。

**⚠️ 核心限制：** gemini-web2api不支持function calling → 不能用kanban worker → 必须用Python脚本直接调API。

**工作流：**
```
Python脚本调Gemini写章节 → 保存文件 → kanban create --assignee lili审核 → 脚本修 → 循环
```

**脚本位置：** `~/.hermes/scripts/gemini_write_chapter.py`

**写作质量对比（实测第七卷）：**
| 指标 | Gemini（脚本） | 闪莉（kanban） |
|------|---------------|---------------|
| 字数控制 | 差（输出7000-10000字，需多轮精简） | 好（直接4500-5500） |
| 禁用词 | 差（"仿佛"经常出现） | 好（严格控制） |
| 高频词 | 差（"一种"10+次） | 好（通常≤3次） |
| 中文质量 | 好（文笔自然） | 好 |
| 速度 | 快（单章30秒） | 中（单章2-3分钟） |
| 成本 | 免费（会员额度） | LongCat额度 |
| batch size | 2章/批（限制） | 8章/批 |

**建议：** Gemini适合额度用完时的应急方案，正式写作仍推荐闪莉。Gemini写完后必须走审核+清词流程。

### 12c. 并行修复+写作（"一期干吧"模式）（2026-06-24 实战验证）

**场景：** 审核发现需要修的章节，同时又有新章节要写。用户说"一期干吧"，意味着修复和写作同时进行，不要串行等待。

**流程：**
```
1. 创建修复任务（--assignee shanli）
2. 创建写作任务（--assignee shanli）
3. 同时dispatch（--max 2）
4. 两个都完成后统一汇报
```

**注意：** 修复和写作任务必须指向同一个工作目录，这样修完的章节和新写的章节都在一起，方便后续统一审核。

**实测案例：** 第七卷351章字数不足+352章需要新写，两个任务同时dispatch，全部完成且达标。

### 13. Notification Interpretation Pattern (Batch vs. Overall)

**Problem:** User receives a kanban done notification and assumes the entire novel is finished, when actually only one batch completed. User says "小说写完了" but means "a batch finished."

**Root Cause:** Completion notifications don't distinguish between "batch N of M completed" and "all work done." User sees "✅ 完成" and interprets it as total completion.

**Solution:** When user reports receiving a completion notification, follow this workflow:

```
1. Find the notification content
   - Check: ~/.hermes/cron/output/<cron_job_id>/*.md (latest files)
   - Or: session_search for "完成" + "看板"

2. Identify what actually completed
   - Read the task title → extract chapter range and batch number
   - Example: "闪莉重写扩写-第277-283章-v2" = batch 15 of ~12 batches

3. Calculate overall progress
   - Current chapter / total chapters in volume
   - File mapping: file chapter N = outline chapter (N - 234)
   - Fourth volume: chapters 234-316 (82 chapters total)

4. Present clear status report
   - What just completed (batch name + chapter range)
   - Overall progress (X/Y chapters, Z%)
   - Remaining work (which chapters still need writing)
   - Next step recommendation (continue writing? review? modify?)

5. Ask if user wants to proceed with next batch
```

**Example output format:**
```
📌 刚完成：第四卷第十五批（277-283章）重写扩写
📊 总进度：50/82 章（61%）
📄 剩余：第284-316章（33章）
⏭️ 下一步：安排第四卷第十六批写作（284-290章）？
```

**Pitfall:** Never assume "done" means "all done" — always verify against the total chapter count and batch decomposition.

### 12. Alternative Worker: MiMo Code

MiMo Code (Xiaomi's OpenCode fork) can be used as an alternative to Hermes subagents for writing/coding tasks.

**When to use:**
- User explicitly requests MiMo Code
- Want to compare output quality between models
- Need a different model/provider for specific tasks

**How to use:**
```bash
# One-shot mode
mimo run 'Write chapter 284 of the novel...'

# Interactive TUI (requires AppleScript clipboard paste for Chinese)
# See opencode skill references/applescript-terminal-control.md
```

**Limitations:**
- MiMo-V2.5 free tier has rate limits
- Large tasks may timeout or get stuck
- Chinese input requires AppleScript clipboard paste workaround

### 15. Gateway Crash Loop: active_profile Redirects Default Gateway (Critical)

**Problem:** `~/.hermes/active_profile` contains a profile name (e.g., "shanli"). When the default gateway starts without `--profile`, `_apply_profile_override()` reads this file and overrides `HERMES_HOME` to the other profile's directory. Both gateways then compete for the same PID/lock files, causing infinite crash loop.

**Error message:** `ERROR gateway.run: Another gateway instance (PID XXXX) started during our startup. Exiting to avoid double-running.`

**Root cause chain:**
1. Default plist launches without `--profile` flag
2. `_apply_profile_override()` reads `~/.hermes/active_profile` → finds "shanli"
3. HERMES_HOME overridden to `~/.hermes/profiles/shanli`
4. Both gateways write to same `gateway.pid` / `gateway.lock`
5. Infinite crash-restart loop

**Fix:** Add `--profile default` to the default gateway plist:
```xml
<string>--profile</string>
<string>default</string>
<string>gateway</string>
<string>run</string>
<string>--replace</string>
```

**Verification:** After fix, both gateways should have separate PIDs and both exit status 0.

**Impact:** Without this fix, the kanban notifier cannot run (it only starts in the dispatch-owning gateway), so task completion notifications never fire.

### 16. Kanban Notify Subscriptions Lost on Gateway Restart

**Problem:** `kanban_notify_subs` table rows are cleared when the gateway process restarts (likely WAL checkpoint or DB reinitialization).

**Solution:** Always re-subscribe tasks after gateway restart. The auto-subscribe rule (Rule 14) handles this for new tasks, but existing subscriptions need manual re-insertion.

**Pattern:** After any gateway restart:
```bash
# Re-subscribe all active tasks
for tid in $(hermes kanban list --json 2>/dev/null | python3 -c "import json,sys; [print(t['id']) for t in json.load(sys.stdin) if t.get('status') not in ('done','archived')]"); do
  sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs (task_id, platform, chat_id, thread_id, user_id, notifier_profile, created_at, last_event_id) VALUES ('${tid}', 'qqbot', '54D8D2AB6A48EE35127DD0F86081146A', '', 'binge', 'default', strftime('%s','now'), (SELECT COALESCE(MAX(id),0) FROM task_events));"
done
```

## Kanban Workflow Pipeline (Clarified)

The correct pipeline flow is:

```
闪莉写 → 莉莉审 → (有问题→闪莉改→莉莉再审→循环) → 通过 → 写下一批
                                                          ↓
                                              整卷写完后 → 大莉M终审
```

**Key rules:**
- 莉莉审核是循环的：发现问题就改，改完再审，直到通过
- 大莉M终审只在**整卷写完后**做一次，不是每批都审
- 每批通过后直接写下一批，不需要等大莉M

### 19. Chapter Renumbering: File Names ≠ Internal Titles (Critical)

**Problem:** Renaming chapter files (e.g., `第183章_xxx.md` → `第182章_xxx.md`) does NOT update the internal markdown title (`# 第183章：xxx`). This causes file names and internal titles to be completely out of sync — a problem that affects ALL downstream tools (grep, review, publishing).

**Root Cause:** `mv` only renames the file. The `# 第XXX章` line inside the file retains the old number.

**Solution — Two-step renumbering:**
```bash
# Step 1: Rename files
mv "第183章_xxx.md" "第182章_xxx.md"

# Step 2: Update internal title (MUST be done separately)
sed -i '' 's/# 第183章/# 第182章/' "第182章_xxx.md"
```

**For bulk renumbering, use Python:**
```python
import os, re
for f in os.listdir('.'):
    match = re.match(r'^第(\d+)章_(.+)', f)
    if match and int(match.group(1)) >= old_start:
        # Rename file
        new_num = int(match.group(1)) - offset
        new_name = f'第{new_num:03d}章_{match.group(2)}'
        os.rename(f, new_name)
        # Update internal title
        with open(new_name, 'r') as fh:
            content = fh.read()
        content = re.sub(rf'第{match.group(1)}章', f'第{new_num}章', content, count=1)
        with open(new_name, 'w') as fh:
            fh.write(content)
```

**Verification after renumbering:**
```bash
# Check internal titles match file names
for f in 第*.md; do
  file_num=$(echo "$f" | grep -o '第[0-9]*章' | sed 's/第//;s/章//')
  internal_num=$(head -1 "$f" | grep -o '第[0-9]*章' | sed 's/第//;s/章//')
  [ "$file_num" != "$internal_num" ] && echo "MISMATCH: $f"
done
```

**Pitfall:** If renumbering includes files from OTHER volumes (e.g., Volume 3 chapters 160-161 when renumbering Volume 4 starting at 162), those files will be incorrectly renamed. Always filter to the target volume range before renumbering.

### 35e. Kanban Worker File Naming — Title Suffix Missing (2026-06-24 实战验证)

**问题：** Kanban worker写完章节后保存为 `第353章.md`（无标题后缀），而不是预期的 `第353章_标题.md`。导致后续审核脚本、grep检查找不到文件。

**根因：** Worker在task body中没有明确指定文件命名格式，或workspace路径导致文件保存位置不正确。

**诊断：**
```bash
# 检查是否有无标题的文件
ls 第353*.md
# 如果只有 第353章.md 没有 第353章_标题.md，说明worker命名不规范
```

**修复：**
```bash
# 从文件内容提取标题
title=$(head -1 第353章.md | sed 's/# //')
newname=$(echo "$title" | sed 's/：/_/')
mv "第353章.md" "${newname}.md"
```

**预防：** 写作任务body中明确指定文件命名规则：
```
文件命名：第{正式编号}章_{标题}.md
内部标题：# 第{正式编号}章：{标题}
```

### 35g. 大纲扩写：章节插入与重编号（2026-06-24 实战验证）

**场景：** 大纲每个情节点规划了3-4章，但实际只写了1-2章。需要补充缺失章节，把故事展开到大纲规划的篇幅。

**诊断：** 对比大纲规划 vs 实际：
```bash
# 大纲说"约3-4章"，但只有1-2章 → 需要补写
grep "章节参考" 大纲.md | head -12
ls 第*章_*.md | wc -l  # 实际章节数
```

**两步法：**

**Step 1：重编号（给新章节腾位置）**
```python
# 重编号映射：旧编号 → 新编号
mapping = {
    336: 338, 337: 339, 338: 341,  # 情节点二
    339: 342, 340: 343,            # 情节点三
    # ... 省略
}

# 第一步：重命名为TEMP_（避免冲突）
for old, new in mapping.items():
    os.rename(f"第{old}章_*.md", f"TEMP_{old}_第{old}章_*.md")

# 第二步：从TEMP改为新编号（同时更新内部标题）
for old, (temp_file, new) in temp_mapping.items():
    content = open(temp_file).read()
    content = content.replace(f"第{old}章", f"第{new}章", 1)  # 只改第一个
    open(temp_file, 'w').write(content)
    os.rename(temp_file, f"第{new}章_*.md")
```

**Step 2：补写缺失章节**
- 缺失章节用 `ls 第*章_*.md | grep -v TEMP` 检查
- 每个缺失章节创建独立的写作任务
- 前驱章节已存在的可以并行dispatch（见2a）

**⚠️ 关键：** 必须先备份再重编号！
```bash
cp -r 第七卷_同源之战 第七卷_同源之战_backup
```

**Pitfall：** 重编号时如果只改文件名不改内部标题，后续grep/check会找到错误的章节号。必须同时更新 `# 第XXX章：标题` 行。

### 35h. "报告出来直接改" — 审核后自动修复偏好（2026-06-24 实战验证）

**用户指令：** "还是像之前那样报告出来直接改"

**含义：** lili审核报告出来后，不需要问用户"要修吗？"，直接创建修复任务。

**处理方式：**
```
lili审核完成 → 读取报告 → 立即创建修复任务（--assignee shanli） → dispatch → 通知用户
```

**不要做的事：**
- ❌ 不要问"要修吗？"
- ❌ 不要等用户确认
- ❌ 不要只报告结果不行动

**例外：** 如果问题很严重（如剧情矛盾、设定错误），仍然要先报告再决定。

---

## ⚠️ 必须用看板执行修改任务（2026-06-17 冰哥纠正）

**问题**：章节修改/修复任务直接用 `delegate_task` 跑子代理，跳过了看板系统。
**冰哥原话**："为什么不是看板"
**根因**：认为"小修改"可以绕过看板直接执行。
**规则**：所有涉及小说章节的修改任务，无论大小，必须通过看板派发。
- 写作任务 → kanban create --assignee shanli
- 修改/修复任务 → kanban create --assignee shanli
- 审核任务 → kanban create --assignee lili
- **例外**：纯分析（不改文件）可以用子代理；紧急单行错别字可以用 patch 直接修

**原因**：看板提供任务追踪、完成通知、worker隔离、重试机制。直接跑子代理没有这些保障。

## ⚠️ 正文目录污染防护（2026-06-17 冰哥纠正）

**问题**：把未终审的精修版章节复制到主正文目录。
**冰哥原话**："只有确定的正文才放进去防止污染"
**规则**：只有莉莉终审通过的章节才能放入 `/Users/libing/Desktop/weinMac/我在深渊事务所/正文/`
- 闪莉初写版 → 临时目录
- Gemini精修版 → 临时目录
- 莉莉审核中 → 临时目录
- **莉莉终审通过** → 移入主目录
- 大莉M终审（整卷）→ 通过后最终确认

**检查清单**：复制前确认 `hermes kanban show <task_id>` 状态为 `done` 且审核报告结论为"通过"。

## ❌ 绝对禁止：绕过看板直接改文件

**冰哥原话（2026-06-17）："停，为什么不是看板"**

小说写作/修改/审核任务**必须**通过kanban task派发，不能用delegate_task直接修改文件。即使任务看起来很简单（如"修几个错别字"），也要走看板。

**原因**：
1. 看板有完整的任务追踪、通知、重试机制
2. 绕过看板无法通知冰哥任务状态
3. 看板任务有workspace隔离，不会污染其他文件

**唯一例外**：冰哥明确说"直接改"的极小修改（如1-2处错别字），可以用patch工具直接修。但涉及3处以上修改或结构性调整，必须走看板。

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Using scratch workspace | Files deleted | Always use `dir:` for file tasks |
| 直接子代理改章节，不走看板 | 无追踪、无通知、无重试 | 所有章节修改必须通过 kanban |
| 未终审就放入主目录 | 污染正文，难以回滚 | 只有莉莉终审通过才移入 |
| Chinese char in profile name | `spawn_failed: Invalid profile name` | Use `[a-z0-9_-]` only |
| Monolithic modification task | Iteration budget exhaustion | Decompose into 2-3 chapter chunks |
| Modifying without confirmation | User frustration | Analyze first, wait for "改" |
| Absolute paths in task body | Path confusion | Use relative paths |
| Vague chapter references | Wrong chapters modified | Use exact chapter numbers |
| Reports in content directory | Cluttered project structure | Move to 小说检查报告/ folder |
| Temporary scripts not cleaned | Project root messy | Clean up after each batch |
| `hermes kanban remove` | "invalid choice" error | Use `archive` then `archive --rm` |
| Both comparison tasks write to same dir | File corruption | Use separate output directories |
| `deliver: origin` doesn't push to QQ | No notification on QQ | Use `qqbot:<channel_id>` format |
| Gemini反代不支持function calling | kanban worker崩溃（空回复） | 用Python脚本直接调API，不走kanban worker |
| Gemini字数控制差 | 输出7000-10000字（目标4500-5500） | 严格prompt+Python后处理+每批只写2章 |
| Gemini不精简只扩写 | 让Gemini精简=无效操作 | 用Python正则直接替换禁用词/高频词 |
| gemini-web2api绑定0.0.0.0 | 本地API暴露到网络 | 改config.json为127.0.0.1 + 设置api_keys |
| "像"高频词是最顽固的 | Gemini/shanli都容易产出10-22次/章 | prompt中显式加"像≤10次"约束+Python后处理 |
| 大纲情节点被压缩 | 45章的卷只写了21章 | task body中明确每个情节点的章节数分配表 |
| User misreads batch notification as "all done" | Wrong progress assumption | Always verify batch vs total progress |
**Solution:** After any gateway restart or config restoration, verify the native notifier is working:
```bash
# Check subscriptions exist
sqlite3 ~/.hermes/kanban.db "SELECT * FROM kanban_notify_subs;"

# Verify gateway is the dispatch-owning one (default profile)
ps aux | grep "hermes_cli.main gateway run" | grep -v shanli
```

The native notifier (5-second polling) replaced the old cron-based `kanban_done_notifier.py` (15-minute polling). No cron job needed.

**Preferred approach:** Subscribe tasks to native notifier via `kanban_notify_subs` table (see section 14).

### Cron Job Deliver Setting Pitfall

**Problem:** Cron job output is saved locally but NOT pushed to the user's chat. User sees tasks complete on the kanban board but receives no notification.

**Root cause:** The `deliver` setting defaults to `"local"` (save only, no push). For notifications to reach the user's chat, it must be set appropriately per platform.

**Fix — platform-specific deliver targets:**

```bash
# Check current deliver setting
hermes cron list 2>/dev/null | grep -A5 "看板任务完成提醒"

# Option A: Push to current chat (works for CLI origin)
hermes cron update <job_id> --deliver origin

# Option B: Push to QQ (origin does NOT work for QQ!)
hermes cron update <job_id> --deliver "qqbot:54D8D2AB6A48EE35127DD0F86081146A"

# Option C: Push to specific Discord channel
hermes cron update <job_id> --deliver "discord:1506530728957972542"

# Option D: Push everywhere
hermes cron update <job_id> --deliver "origin,all"
```

**QQ-specific pitfall:** `deliver: origin` does NOT push to QQ windows. QQ requires the explicit channel ID format `qqbot:<hex_id>`. Find the ID via `hermes send --list` or check `~/.hermes/channel_directory.json`.

### 27. Dual Gateway Architecture — Layered Bug (2026-06-15)

**Problem:** Two Hermes gateways (default + shanli) running simultaneously, sharing the same Telegram Bot Token, caused:
1. Telegram messages randomly distributed to different gateways
2. Model switching (mimo-v2.5 vs LongCat) depending on which gateway won polling
3. Cron jobs lost during Hermes Agent update (8→1 jobs)
4. Telegram polling conflict every ~25 seconds

**Root cause:** Two LaunchAgent plists with `RunAtLoad: true` and `KeepAlive: true`:
- `ai.hermes.gateway.plist` (default)
- `ai.hermes.gateway-shanli.plist` (shanli)

**Fix (verified 2026-06-15):**
1. `launchctl bootout` shanli gateway (NOT kill — KeepAlive trap)
2. `mv plist → .disabled` (prevent reboot restart)
3. `kickstart` default gateway (clear Telegram session state)
4. `echo "default" > ~/.hermes/active_profile` (reset)
5. Recover lost cron jobs from state snapshot

**Correct architecture:** Single gateway + multi-profile kanban dispatch:
- Default gateway manages all messaging platforms (Telegram/QQ/Discord)
- Kanban dispatches to profiles via `kanban.profiles: ["lili", "shanli"]`
- Workers automatically use profile's HERMES_HOME, .env, and config.yaml

**Verification:** `ps aux | grep hermes_cli.main | grep -v grep` → should show only 1 process

**Detailed reference:** `references/two-gateway-architecture.md`

## Gateway Kanban Notifier (Configurable Interval)

**Problem:** Cron-based kanban done notifier runs every N minutes, causing delayed notifications.

**Discovery:** Hermes Gateway has a built-in kanban notifier that polls at a configurable interval and pushes notifications when tasks complete. It requires subscription records in `kanban_notify_subs` table.

### Gateway Kanban Notifier (Instant Notifications)

**How it works:** Hermes Gateway has a built-in kanban notifier (`_kanban_notifier_watcher`) that polls every 5 seconds and pushes notifications instantly when tasks complete. It runs as an asyncio task inside the default gateway process.

**Requirements:**
1. Both gateways must be running (default + shanli)
2. Default gateway plist must have `--profile default` (avoids active_profile collision)
3. `kanban.dispatch_in_gateway: true` in config.yaml
4. Subscription records in `kanban_notify_subs` table (see section 14)

**Notification format:** `✔ @{assignee} Kanban {task_id} done — {title}\n{summary}`

**Subscription lifecycle:**
- Created via SQL INSERT (section 14 auto-subscribe pattern)
- Cursor advanced atomically on each tick
- Auto-removed when task reaches done/archived status
- May be cleared on Gateway restart — verify after restart

**Known issues (fixed in 2026-06-13):**
1. Subscriptions cleared on Gateway restart → re-insert after restart
2. Default Gateway crash loop if `active_profile` file exists → add `--profile default` to plist
3. send() return value not checked → fixed in `gateway/kanban_watchers.py`
4. See `references/two-gateway-architecture.md` for architecture details (includes Telegram polling conflict and cron job recovery)

### 27. Dual-Gateway Root Cause Analysis (2026-06-15 verified)

**Layered bug diagnosis process — use multi-AI review for complex infrastructure issues:**

When facing a multi-layered infrastructure issue, use this diagnostic pattern:
1. **Collect evidence first** — don't jump to conclusions
2. **Delegate to internal AI agents** — 大莉M for analysis, 大莉D for review
3. **Delegate to external AI models** — FreeModel Claude Opus 4.8 / GPT-5.5 for independent perspective
4. **Verify technical details with source code** — read the actual implementation
5. **Consolidate findings** — compare consensus and disagreements across all AIs

**Multi-AI review pattern (validated 2026-06-15):**
```
大莉M (mimo-v2.5-pro)  → 出方案
大莉D (deepseek-v4-pro) → 审核方案
Claude Opus 4.8 (FreeModel) → 独立分析
GPT-5.5 (FreeModel) → 独立分析
→ 汇总四方意见 → 找共识和分歧 → 最终方案
```

**Why multi-AI:** Single-model analysis can miss blind spots. Four independent analyses catch issues that one model might overlook (e.g., 大莉D found the KeepAlive trap that 大莉M missed).

**Dual gateway symptoms and root causes:**

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Telegram model switches randomly | Two gateways share same Bot Token, compete for getUpdates | Stop one gateway |
| Kanban notifications on wrong platform | Gateway home channel auto-push | Verify kanban_notify_subs |
| Cron jobs lost after update | jobs.json reset during Hermes Agent update | Restore from state snapshot |
| KeepAlive restarts killed process | Both plists have `<key>KeepAlive</key><true/>` | Use `launchctl bootout` first |

**Verification that single gateway works for kanban:**
- Default gateway config has `kanban.profiles: ["lili", "shanli"]`
- Worker spawn sets `HERMES_HOME` to profile directory automatically
- Workers read profile-specific `.env` and `config.yaml`
- No dependency on shanli gateway process

### 28. Dual-Gateway Telegram Polling Conflict — Complete Fix (2026-06-15 validated)

**Problem:** Two gateway processes (default + shanli) share the same Telegram Bot Token, causing `Conflict: terminated by other getUpdates request` errors every ~25 seconds. Messages are randomly distributed between the two gateways, so the user sees different models responding (e.g., LongCat from shanli vs auto from default) depending on which gateway wins the polling race.

**Symptoms:**
- Telegram shows "model switching" without user action
- Kanban notifications appear on unexpected platforms
- Gateway logs filled with `Telegram polling conflict (1/5)` warnings
- Response quality inconsistent (different models handling same conversation)

**Root cause:** Telegram Bot API's `getUpdates` is exclusive — only one client can poll at a time. When two gateways use the same bot token, they compete:
```
Gateway A (default, auto model) ──┐
                                  ├─→ Telegram API ──→ random winner gets message
Gateway B (shanli, LongCat) ─────┘
```

**Diagnostic:**
```bash
# Check if multiple gateways are running
ps aux | grep "hermes_cli.main" | grep -v grep

# Check for polling conflicts in logs
grep "Telegram polling conflict" ~/.hermes/logs/gateway.log | tail -5

# Check which profiles are active
cat ~/.hermes/active_profile
```

**Complete Fix Procedure (validated 2026-06-15):**

⚠️ **顺序很重要！** 必须按以下步骤执行，不能跳步。

```
Phase 1 — 停掉多余gateway（5分钟）

Step 1: 备份
  cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak.$(date +%Y%m%d%H%M%S)
  cp ~/.hermes/kanban.db ~/.hermes/kanban.db.bak.$(date +%Y%m%d%H%M%S)

Step 2: bootout shanli gateway（⚠️ 必须先bootout，不能先kill）
  launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist
  sleep 3

Step 3: 确认进程死亡
  ps aux | grep "profile shanli" | grep -v grep
  # 应该无输出

Step 4: 禁用plist（防复活）
  mv ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist \
     ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist.disabled

Step 5: kickstart default gateway（清理Telegram会话状态）
  launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway
  sleep 15

Step 6: 重置active_profile
  echo "default" > ~/.hermes/active_profile

Step 7: 验证conflict消失
  tail -10 ~/.hermes/logs/gateway.error.log | grep -i "conflict"
  # 重启后应该无conflict

Phase 2 — 恢复Cron Jobs（10分钟）

Step 1: 从state snapshot恢复有效jobs
  - 验证每个job的脚本路径是否存在
  - 跳过脚本缺失的job
  - 用hermes cron add或cronjob工具恢复

Step 2: 验证
  hermes cron list
```

**⚠️ KeepAlive陷阱：** 两个plist都有 `<key>KeepAlive</key><true/>`。如果先kill进程再disable plist，launchd会**立即自动重启**进程。必须先 `launchctl bootout` 卸载服务，再disable plist。

**为什么不需要重启default gateway？** Default gateway一直在正常运行，停掉shanli后conflict自动消失。但如果Telegram session state需要清理，用 `launchctl kickstart -k` 比 stop+start 更可靠。

**Kanban worker spawn验证：** 停掉shanli后，default gateway的 `kanban.profiles: ["lili", "shanli"]` 配置仍然有效。Worker spawn时HERMES_HOME自动设为profile目录（`~/.hermes/profiles/shanli/`），读取该profile的.env和config.yaml。不需要shanli gateway进程。

**Cron job恢复注意事项：**
- Cron scheduler不处理profile字段，所有jobs用gateway的HERMES_HOME运行
- 恢复LongCat模型的job时，必须显式指定model/provider字段
- 脚本不存在的job不要恢复（会执行失败）
- 恢复后验证：检查cron output目录是否有新文件生成

**Prevention:** When setting up multiple gateways, each should have its own bot token or disable platform connections on all but one gateway. 单gateway+多profile是Hermes的设计本意。

### Pitfall: Gateway Crash Loop Pitfall (default + shanli profiles)

**Problem:** When both default and shanli profile gateways run, they crash with "Another gateway instance started during our startup."

**Root cause:** `~/.hermes/active_profile` contains `shanli`, causing the default gateway (no `--profile` flag) to override `HERMES_HOME` to the shanli profile directory. Both gateways then compete for the same PID/lock files.

**Fix:** Add `--profile default` to the default gateway's plist:
```xml
<string>--profile</string>
<string>default</string>
<string>gateway</string>
<string>run</string>
<string>--replace</string>
```

**File:** `~/Library/LaunchAgents/ai.hermes.gateway.plist`

## Cron Job Diagnostic Pitfall: `hermes cron status` False Negative

**Problem:** `hermes cron status` and `hermes cron list` may report "Gateway is not running — jobs won't fire automatically" even when the gateway IS running via macOS LaunchAgent.

**Root cause:** The CLI's gateway detection checks a different mechanism than the actual launchd service. The gateway may be running (PID visible in `ps aux`, launchd plist loaded) but the CLI status check misses it.

**Ground truth check — use `hermes gateway status` instead:**
```bash
# ❌ UNRELIABLE — may falsely report "not running"
hermes cron status
hermes cron list  # also shows the warning

# ✅ GROUND TRUTH — shows actual launchd service status + PID
hermes gateway status
```

**Full diagnostic sequence when cron jobs appear not to fire:**
```bash
# Step 1: Check gateway is actually running (ground truth)
hermes gateway status
# Look for: "✓ Gateway service is loaded" + PID number

# Step 2: Verify process exists
ps aux | grep "hermes_cli.main gateway" | grep -v grep

# Step 3: Check job exists and is enabled
hermes cron list 2>/dev/null
# Ignore the "Gateway is not running" warning here

# Step 4: Check execution history (most reliable)
ls -la ~/.hermes/cron/output/<job_id>/
# Each .md file = one execution. Recent timestamps = job is firing.

# Step 5: Manual trigger test
# Via MCP tool: cronjob action=run job_id=<id>
# Via CLI: hermes cron run <job_id>

# Step 6: Check gateway logs for errors
tail -20 ~/.hermes/logs/gateway.log
tail -10 ~/.hermes/logs/gateway.error.log
```

**Key insight:** The execution output directory (`~/.hermes/cron/output/<job_id>/`) is the MOST reliable indicator of whether a cron job is actually firing. If .md files are being created with recent timestamps, the job is working — regardless of what `hermes cron status` says.

**MCP vs CLI job ID mismatch:** The `cronjob` MCP tool and `hermes cron` CLI may display different job IDs for the same job. The MCP tool uses the full hex ID from `~/.hermes/cron/jobs.json`; the CLI may show a different format. Both refer to the same underlying job.

### Two-Layer Cron Diagnosis (2026-06-22 validated)

**Problem:** Cron job fails repeatedly. Surface error shows skill content dump or misleading message. Agent spends time fixing the skill when the real issue is framework-level.

**Root Cause Pattern:** Two independent failure layers can cause cron errors:
1. **Skill layer** — SKILL.md missing, outdated, or malformed
2. **Framework layer** — Hermes agent runtime errors (ImportError, TypeError, module cache stale)

**Diagnostic flowchart:**
```
Cron job fails
  ├─ Check output file: ~/.hermes/cron/output/<job_id>/
  │   ├─ File is ~2KB with "skill not found" → SKILL.md missing (Layer 1)
  │   ├─ File is ~22KB with skill content + error at end → Framework error (Layer 2)
  │   └─ File is ~22KB with actual report content → Success (check delivery)
  │
  ├─ Layer 1 fix: Recover SKILL.md (see section 31a)
  │
  └─ Layer 2 fix:
      ├─ Read the actual error at end of output file
      ├─ ImportError from agent.* → Gateway has stale module cache
      │   └─ Fix: hermes gateway restart
      ├─ TypeError in tool code → Python version mismatch
      │   └─ Check: venv python vs system python
      └─ Other errors → Check gateway.error.log for details
```

**Key insight:** When the output file is large (20KB+) and contains the full skill content, the skill loaded successfully — the error is in the agent runtime, not the skill. Don't waste time re-patching the skill.

**Verification after fix:**
```bash
# 1. Check output file size — >10KB means skill loaded
ls -la ~/.hermes/cron/output/<job_id>/ | tail -3

# 2. Check last_status updated
cronjob action=list  # Look for last_status field

# 3. Check actual report content exists (not just skill dump)
grep -c "【⏰" ~/.hermes/cron/output/<job_id>/*.md
# Should show >0 for successful morning report
```

**Detailed case studies:** See `references/cron-framework-error-diagnosis.md` for specific ImportError/TypeError patterns (e.g., `inject_memory_provider_tools`, Python version compatibility).

---

### 27. Worker Timeout 处理（2026-06-15 实战验证）

**问题：** Kanban任务超时（max_runtime到期），但worker进程仍在运行，占用资源。

**症状：**
- 收到 `timed out (max_runtime=0s); will retry` 通知
- `hermes kanban show <task_id>` 显示 status: running
- `ps aux | grep hermes.*worker` 可以看到僵尸worker进程

**诊断：**
```bash
# 检查任务状态
hermes kanban show <task_id> | head -10

# 检查是否有worker在跑
ps aux | grep "hermes.*kanban.*worker\|hermes.*-p.*--accept-hooks" | grep -v grep

# 检查worker运行时间
ps -p <PID> -o pid,etime,command
```

**修复：**
```bash
# 1. 杀掉僵尸worker
kill <PID>
sleep 2
# 如果还是zombie状态
kill -9 <PID>
wait <PID> 2>/dev/null

# 2. 检查已写章节（确认工作成果）
cd /path/to/正文
for i in $(seq 11 20); do
  f=$(ls 第${i}章_*.md 2>/dev/null | head -1)
  if [ -n "$f" ]; then
    words=$(python3 -c "import re; print(len(re.findall(r'[\u4e00-\u9fff]', open('$f').read())))")
    echo "✓ 第${i}章: $f (${words}字)"
  else
    echo "✗ 第${i}章: 未写"
  fi
done

# 3. 如果章节已写完，归档超时任务
hermes kanban archive <task_id>

# 4. 如果章节未写完，创建补写任务
hermes kanban create "补写第X-Y章" --assignee shanli --body "..."
```

**关键教训：** 超时 ≠ 无成果。Worker可能已经写了大部分章节，只是最后几章没来得及。先检查文件再决定是否重写。

### 28. 看板任务归档清理（2026-06-15 实战验证）

**问题：** 看板上积累了大量旧的blocked/done任务，影响视觉和管理。

**清理方法：**
```bash
# 查看所有非活跃任务
hermes kanban list 2>&1 | grep -E "(blocked|done|archived)"

# 批量归档旧任务
hermes kanban archive t_xxx t_yyy t_zzz

# 归档后彻底删除（可选）
hermes kanban archive --rm t_xxx t_yyy t_zzz
```

**建议：** 每完成一个写作批次后，归档该批次的所有任务（写作/审核/修复），保持看板整洁。

### 29. Cron Job Script 路径陷阱（2026-06-15 实战验证）

**问题：** 用 cronjob 工具创建 script 类型的 cron job 时，symlink 会报 `Script path escapes the scripts directory via traversal` 错误。

**原因：** Cron scheduler 对 script 路径有安全检查，不允许 symlink 指向 ~/.hermes/scripts/ 之外的文件。

**正确做法：** 复制脚本文件，不要用 symlink：
```bash
# ❌ 错误：symlink 会被拒绝
ln -sf ~/.hermes/skills/productivity/nv-multi-model/scripts/nv_ping.py ~/.hermes/scripts/nv_ping.py

# ✅ 正确：复制文件
cp ~/.hermes/skills/productivity/nv-multi-model/scripts/nv_ping.py ~/.hermes/scripts/nv_ping.py
chmod +x ~/.hermes/scripts/nv_ping.py
```

**验证：**
```bash
ls -la ~/.hermes/scripts/nv_ping.py
# 应该显示普通文件，不是 symlink
```

**已知可从此处复制的脚本：**
- `nv_ping.py` → `~/.hermes/skills/productivity/nv-multi-model/scripts/nv_ping.py`
- `nv_daily_eval.py` → `~/.hermes/skills/productivity/nv-multi-model/scripts/nv_daily_eval.py`
- `gen_v5.py` → `~/.hermes/profiles/dalid/skills/productivity/financial-dashboard/scripts/gen_v5.py`

### 30. Kanban Task max_runtime=0s 超时陷阱（2026-06-15）

**问题：** Kanban任务创建后立即超时，显示 `timed out (max_runtime=0s); will retry`。

**原因：** 任务创建时没有正确继承config.yaml中的 `max_runtime: 2h` 设置，使用了默认值0。

**诊断：**
```bash
hermes kanban show <task_id> | grep "max_runtime"
```

**解决：** 如果任务反复超时，检查config.yaml中的kanban.max_runtime设置，确保不是0。

### 33. Kanban Worker 文件名不含标题后缀（2026-06-25 发现）

**问题：** kanban worker 写文件时，文件名可能是 `第XXX章.md` 而非 `第XXX章_标题.md`，导致后续 glob 匹配 `第${i}章_*.md` 找不到文件。

**症状：** 任务显示 done 但 `ls 第${i}章_*.md` 返回空，实际文件存在为 `第XXX章.md`。

**修复：** 写完后立即检查并重命名。

**预防：** 任务 body 中明确要求文件名格式：`文件名必须为 第{编号}章_{标题}.md`

### 34. Provider 额度耗尽时的降级策略（2026-06-25 发现）

**问题：** LongCat 额度用完后 shanli profile 的所有任务都会 blocked（HTTP 402）。

**处理：** 检查 provider 状态 → 切换到备用 provider（lili/DeepSeek） → 通知用户。

### 35. 并行写作的世界观一致性风险（2026-06-25 发现）

**问题：** 多个章节并行写作时，worker 可能引入错误的世界观设定。

**预防：** 任务 body 中明确列出禁止词清单 → 每批完成后扫描红线词 → 不超过3章并行 → 写完验证再写下一批。

### 31a. SKILL.md 丢失恢复（从 Session 历史提取）

**场景：** Skill 目录存在但 SKILL.md 被删除（只剩 references/ 文件），cron 任务每天报 `skill not found`。

**根因：** SKILL.md 文件被意外删除或覆盖，但 references/ 文件保留了补丁历史。

**恢复流程：**
1. 用 `grep -rl '<skill-name>' ~/.hermes/sessions/` 找到曾加载该 skill 的 session JSON
2. 从 session JSON 的 `skill_view` 工具响应中提取完整 SKILL.md 内容
3. 从 references/ 文件中提取版本补丁（如 v3.4→v3.5→v3.6）
4. 应用补丁后写入 SKILL.md
5. 用 `skill_view(name='...')` 验证

**详细步骤：** 见 `references/skill-recovery-from-sessions.md`

**预防：** 定期备份重要 skill 文件到 `~/.hermes/backups/`

---

### 33. Cron Job 从 State Snapshot 恢复（2026-06-15 实战验证）

**场景：** Hermes Agent 更新后 jobs.json 被重置，丢失了所有 cron jobs。

**恢复步骤：**
```bash
# 1. 备份当前 jobs.json
cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak.$(date +%Y%m%d)

# 2. 检查 state snapshot 中的 jobs
cat ~/.hermes/state-snapshots/<timestamp>/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    print(f'{j[\"id\"]}: {j[\"name\"]} (script={j.get(\"script\",\"none\")}, model={j.get(\"model\",\"default\")})')
"

# 3. 验证脚本路径存在
for script in nv_ping.py nv_daily_eval.py health_daily.py; do
  test -f ~/.hermes/scripts/$script && echo "✓ $script" || echo "✗ $script MISSING"
done

# 4. 逐个恢复（用 cronjob 工具）
# Script jobs:
cronjob action=create name="..." script="nv_ping.py" no_agent=true schedule="*/30 * * * *" deliver=local

# Agent jobs:
cronjob action=create name="..." prompt="..." schedule="0 8 * * *" deliver="telegram:611807381" \
  model='{"model":"LongCat-2.0-Preview","provider":"longcat"}' skills='["daily-morning-report"]'
```

**注意事项：**
- Schema 字段可能变化，需要补充 `profile: null, context_from: null, enabled_toolsets: null` 等
- `deliver` 格式：`telegram:611807381`（不是简单的 `telegram`）
- LongCat 模型的 job 需要显式指定 `model` 和 `provider`
- `next_run_at` 会被 cron 引擎自动计算，不需要手动设置

### 33. 跨卷一致性审核（2026-06-18 新增）

**场景：** 完成一个卷的写作后，需要审核该卷与之前所有卷的设定一致性。

**审核顺序：**
```
第二卷 vs 第一卷
第三卷 vs 第一卷+第二卷
第四卷 vs 第一卷+第二卷+第三卷
...以此类推
```

**审核维度（仅剧情/设定，不做文字/字数审核）：**
1. 角色设定一致性：身份、能力、外貌、性格是否与前卷一致？
2. 世界观一致性：地理、技术、组织、势力设定是否前后一致？
3. 时间线一致性：事件先后顺序是否合理？
4. 角色关系一致性：角色之间的关系是否前后一致？
5. 能力体系一致性：能力发展是否前后一致？
6. 伏笔回收：前卷伏笔是否得到合理回收？
7. 场景重复：是否有与前卷重复的场景/事件？

**执行方式：** 用大莉M（delegate_dalim）做审核，不用莉莉（莉莉负责文字层面，大莉M负责结构层面）。

**审核报告格式：**
- P0致命：必须修复（设定根本性冲突）
- P1严重：建议修复（时间线矛盾、角色行为矛盾）
- P2建议：可优化（细节不一致、场景重复）

**修复决策：** 以较早的卷为准（"前50章正文为准"），修改较新的章节。

**案例（第五卷）：**
- 发现290-304章与240-289章存在系统性矛盾（深度1200m vs 12000m、诺亚身份、大卫本质等）
- 根因：290-304章是基于大纲新写的，未对照前50章正文
- 修复：重写290-304章，对齐前50章设定

**关键教训：**
- 新写章节必须预读前文，不能只看大纲
- 大纲本身可能与正文存在差异（大纲是规划，正文是事实）
- 跨卷审核应在每卷完成后立即做，不要积累到最后

**"以前面的为准"决策规则（2026-06-18）：**
当跨卷审核发现设定矛盾时，以较早的章节为准，修改较新的章节。
- 冰哥原话："以前面的为准剩下的你定"
- 原因：前文已经读者建立了认知，改前文会破坏已有阅读体验
- 例外：如果前文有明显错误且后文已修正，可协商决定

**重写后旧版本清理（2026-06-18 陷阱）：**
重写任务完成后，旧版本文件可能残留在目录中，导致：
- 同一章节号出现两个文件（如"第297章_大卫的选择.md"和"第297章_大卫与诺亚重聚.md"）
- 旧版本包含错误设定（如大卫=AI、万米深度）
- 验证脚本可能读到旧版本

**修复步骤：**
```bash
# 1. 重写完成后立即检查重复文件
ls 第XXX章*.md  # 看是否有多个同编号文件

# 2. 删除旧版本（保留新版）
rm "第297章_大卫的选择.md"  # 旧版（大卫=AI）

# 3. 验证新版本无残留问题
grep -c "万米\|流体合金\|超级人工智能\|安保长官" 第297章*.md
```

**预防：** 写作任务body中明确指定输出文件名，避免新旧版本并存。

### 34. 本地优先工作流（新卷写作标准流程）

**场景：** 新卷写作时，先在本地临时目录完成，定稿后再移入主目录。

**流程：**
```
1. 创建本地工作目录：/Users/libing/Desktop/临时文件-0001/脑洞文/第X卷_卷名/
2. 复制主角团信息卡 + 大纲 + 前10章到工作目录
3. 闪莉在本地目录写作
4. 莉莉审核（在本地目录）
5. 大莉M终审（在本地目录）
6. 用户确认"定稿"后，cp到主目录
```

**原因：** 防止未定稿内容污染主目录；本地目录可安全删除/重写；定稿前可自由实验。

**案例：** 第六卷"地下档案馆"使用此流程。

### 35. 自动写-审-修循环 + 断路器（2026-06-22 新增）

**场景：** 每批写作完成后，需要多轮"莉莉审核→闪莉修复→莉莉再审"循环，直到全部达标。手动创建任务效率低。

**用户指令：** "每次闪莉改完就让莉莉审核直到没有问题，同时同一问题连续三次没有改成功就停下来问我"

**完整流水线（3阶段）：**
```
闪莉写（kanban）→ 莉莉审（kanban）→ 全部达标？→ 结束，写下一批
                                       ↓ 有问题
                              闪莉修（kanban）→ 莉莉审（kanban）→ 全部达标？→ 结束
                                                                      ↓ 有问题
                                                              同一问题连续3次？→ 停下问冰哥
                                                                      ↓ 否
                                                              继续下一轮修复
```

**监控架构：**
```
监控脚本（cron every 5m, no_agent=true）
  ├─ phase=write: 检查写作任务 → 完成后自动创建审核任务
  ├─ phase=review: 检查审核任务 → 完成后检查质量
  │   ├─ 全部达标 → status=all_passed, 结束
  │   └─ 有残留 → 记录问题历史 → 创建修复任务
  │       ├─ 同一问题连续3次 → status=stuck, 停下来问冰哥
  │       └─ 未到3次 → phase=fix, 继续循环
  ├─ phase=fix: 检查修复任务 → 完成后自动创建审核任务
  └─ 任务未完成 → 静默输出 [SILENT]
```

**实现步骤：**

1. 创建跟踪文件（JSON，放在工作目录下）：
```json
{
  "round": 1,
  "max_rounds": 3,
  "issue_history": {},
  "write_task": "t_xxx",
  "current_fix_task": null,
  "current_review_task": null,
  "phase": "write",
  "status": "running"
}
```
**phase字段值：** `write`（等待写作完成）→ `review`（等待审核）→ `fix`（等待修复）→ `review`（再审）→ ...

2. 创建监控脚本 `~/.hermes/scripts/fix_review_loop.py`：
   - 读取跟踪文件，根据 `phase` 分支处理
   - `hermes kanban show <task_id>` 检查任务状态
   - 审核完成后用Python统计高频词/字数
   - 根据结果自动创建下一轮任务
   - 问题历史计数，连续3次不达标触发断路器
   - 每次创建新任务后必须 `subscribe_task`

3. 创建cron job（`no_agent=true`, `script=fix_review_loop.py`, `schedule=every 5m`）

4. 初始写作/修复任务用 `--workspace dir:/path` 指定工作目录

**断路器逻辑：**
```python
# 同一问题连续3轮未解决
stuck_issues = {k: v for k, v in track['issue_history'].items() if v >= 3}
if stuck_issues:
    track['status'] = 'stuck'
    print(f"🛑 同一问题连续3轮未解决，需要冰哥介入：\n{stuck_list}")
```

**质量检查指标（可自定义）：**
- 字数：`len(re.findall(r'[\u4e00-\u9fff]', content))` ≥ 4500
- 禁用词：0次
- 高频词：每章≤3次

**Pitfalls：**
- 脚本用 `no_agent=true`（纯脚本，不消耗LLM token）
- `deliver=local`（只存文件不推送，避免刷屏）
- 跟踪文件放在工作目录下，任务完成即可清理
- 每轮创建新任务时必须 `subscribe_task`（否则无QQ通知）
- 脚本遇到异常状态（blocked/crashed）应输出明确错误，不要静默
- 循环结束后必须停掉cron+归档任务（见模板文件"循环结束后标准清理"）
- 批次间脚本复用用`cp+sed`而不是重写（见模板文件"批次间脚本复用"）

### 35a. 快速连续派发多批（2026-06-22 实战验证）

**场景：** 用户说"直接下一批"，意味着不需要确认，立即创建下一批写作任务+监控。

**流程：**
```
1. 查看大纲，确定下一批章节范围和对应情节点
2. 创建写作任务（--assignee shanli, --workspace dir:...）
3. 订阅通知 + dispatch
4. cp+sed创建批次监控脚本
5. 创建跟踪文件
6. 创建cron job
7. 告诉用户"已启动，QQ推通知"
```

**关键：** 不要问"要继续吗？"——用户说"直接下一批"就是命令。但仍然需要读大纲确定章节范围，不能盲目创建。

**模板文件：** 参考 `references/fix-review-loop-template.md`（含完整脚本、跟踪文件模板、批次间脚本复用、循环结束后标准清理）

### 35b. Writing 8 Chapters May Hit Iteration Budget (2026-06-23 实战验证)

**问题：** 写作任务分配8章，但复杂大纲（如需要大量世界观铺设的情节点）会导致每章消耗更多迭代次数，最终在90/90上限被block。

**实测案例：** 第七卷第一批（334-341章），大纲包含同星会分裂史+三个新势力登场+铁穹计划技术分析。Worker写了8章但5章字数不足（336章仅2709字），任务被block。

**症状：** `hermes kanban show <task_id>` 显示 `blocked` + `Iteration budget exhausted (90/90)`。

**诊断：** 检查已写章节质量：
```bash
for i in $(seq START END); do
  f=$(ls 第${i}章_*.md 2>/dev/null | head -1)
  [ -n "$f" ] && python3 -c "import re; print(f'第${i}章: {len(re.findall(r\"[\u4e00-\u9fff]\", open(\"$f\").read()))}字')"
done
```

**处理流程：**
1. 停掉该批次的cron监控：`cronjob action=remove job_id=xxx`
2. 统计哪些章节达标（≥4500字）、哪些不达标
3. 创建修复任务，只补字数不足的章节（不重写全部）
4. 更新跟踪文件：`phase: "fix"`, `current_fix_task: "新task_id"`, 保留 `issue_history`
5. 重新创建cron监控（如果还需要走审核循环）
6. 修复完成后再走正常审核流程

**预防：** 复杂大纲批次考虑拆分为4-5章/批，而非8章。简单大纲（日常推进）8章没问题。

**⚠️ blocked ≠ 失败：** Worker可能已经写了大部分章节，只是最后几章没来得及。先检查文件再决定。不要直接重写全部。

### 35b. Provider Switching When Tokens Run Out (2026-06-23 verified)

**场景：** LongCat额度耗尽，需要切换到其他provider继续写作。

**可用替代方案（按推荐顺序）：**
1. **gemini-web2api**（本地反代，免费，用Gemini网页版额度）
2. **DeepSeek V4 Flash**（$0.28/M output，最便宜的官方API）
3. **小米MiMo**（已配置，中文写作质量好）

**切换步骤：**
```bash
# 1. 确认替代provider可用
curl -s http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3.5-flash","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'

# 2. 创建任务时指定新assignee
hermes kanban create "写作任务" --assignee shanliG ...  # Gemini
# 或
hermes kanban create "写作任务" --assignee shanli ...    # DeepSeek（需改config）

# 3. 监控脚本和流程不变
```

**⚠️ 注意事项：**
- gemini-web2api是反向工程产物，不是官方API，Google随时可能封禁
- 长task body会导致Gemini返回空响应（见references/gemini-web2api-setup.md）
- 切换provider后写作质量可能有差异，审核标准不变
- 建议：Gemini做写作（免费），DeepSeek/MiMo做审核（便宜稳定）

### 35c. "看一下" vs "直接下一批" 的区别

**"看一下"（检查状态）：**
- 只读kanban list + 检查文件 + 报告结果
- 不创建新任务
- 不改任何东西

**"直接下一批"（立即派发）：**
- 读大纲 → 创建写作任务 → 订阅 → dispatch → 创建监控 → cron
- 全自动，不需要用户确认
- 完成后QQ推通知

---

### 35. 自动化写→审→修循环（含断路器）（2026-06-22 实战验证）

**场景：** 小说批量写作，每批写完→莉莉审核→有问题→闪莉改→再审，直到通过。

**核心机制：**
```
闪莉写 → 莉莉审 → 通过→结束
              ↓ 有问题
         闪莉改 → 莉莉审 → 通过→结束
              ↓ 有问题（同一问题连续3次？）
         是→停下问冰哥 / 否→继续下一轮
```

**实现方式：** Python监控脚本 + cron每5分钟检查

**脚本核心逻辑（3个phase）：**
1. `write` phase：等待写作任务done → 创建审核任务
2. `review` phase：等待审核任务done → 检查章节质量 → 全通过→结束 / 有残留→检查断路器→创建修复任务
3. `fix` phase：等待修复任务done → 检查质量 → 全通过→结束 / 有残留→回到review

**断路器：** 同一问题（如"高频词:某种"）连续3轮未解决 → `status: "stuck"` → 停止循环，通知冰哥介入

**跟踪文件（.fix_review_loop.json）：**
```json
{
  "round": 1,
  "max_rounds": 3,
  "issue_history": {"高频词:某种": 1, "禁用词:深吸一口气": 2},
  "current_fix_task": "t_xxx",
  "current_review_task": null,
  "phase": "fix",
  "status": "running",
  "write_task": "t_yyy",
  "batch": "305-312"
}
```

**status值：** running / all_passed / stuck / max_rounds_reached / *_failed_*

**章节质量检查（check_chapters函数）：**
```python
# 每章检查：字数≥4500 + 禁用词0次 + 高频词≤3次
for word in ['深吸一口气', '仿佛', '不由得']:  # 禁用词，0次
for word in ['某种', '一种', '微微', '如同']:   # 高频词，≤3次
```

**模板化创建流程（每批重复）：**
```bash
# 1. 创建跟踪文件
cat > .fix_review_loop_rN.json << 'EOF'
{"round":1,"max_rounds":3,"issue_history":{},"phase":"write","status":"running","write_task":"TASK_ID","batch":"START-END"}
EOF

# 2. 创建监控脚本（从上一批复制+修改）
cp fix_review_loop_batchN-1.py fix_review_loop_batchN.py
sed -i '' 's/rN-1\.json/rN.json/' fix_review_loop_batchN.py
sed -i '' 's/START_PREV, END_PREV/START, END/' fix_review_loop_batchN.py
sed -i '' 's/第N-1批/第N批/g' fix_review_loop_batchN.py

# 3. 创建cron（no_agent=true，deliver=local）
cronjob action=create script=fix_review_loop_batchN.py no_agent=true schedule="every 5m" deliver=local
```

**完成后的清理：**
```bash
# 停cron + 归档done任务
cronjob action=remove job_id=xxx
DONE_IDS=$(hermes kanban list 2>/dev/null | grep "✓" | awk '{print $2}')
for id in $DONE_IDS; do hermes kanban archive "$id" 2>/dev/null; done
```

**实测数据（第六卷前四批）：**
| 批次 | 章节 | 修复轮次 | 断路器触发 | 最终达标 |
|------|------|---------|-----------|---------|
| 第一批 | 305-312 | 2轮 | 否 | ✅ |
| 第二批 | 313-320 | 2轮 | 否 | ✅ |
| 第三批 | 321-328 | 2轮 | 否 | ✅ |
| 第四批 | 329-336 | 3轮 | 否 | ✅ |

**关键经验：**
- 每批2-3轮修复是常态，第1轮通常字数和高频词都不达标
- "某种""一种"是最顽固的高频词，经常需要2轮才能压到≤3
- 断路器3次是合理阈值——实测从未触发过，说明闪莉2-3轮内能修好
- 监控脚本用no_agent=true（纯脚本，不消耗LLM token）

**⚠️ 注意事项：**
- 写作任务和修复任务的workspace必须指向同一个目录
- 审核任务用scratch workspace（不需要持久化文件）
- 每个任务创建后必须订阅kanban_notify_subs
- 脚本中的check_chapters章节范围必须与batch匹配

### 35d. "跳过"模式 — 用户偏好快速推进（2026-06-23 实战验证）

**场景：** 审核发现高频词/禁用词问题，但用户更关心写作进度，不想反复修同一类问题。

**用户行为：** 反复说"跳过"、"先写"、"先跳过" — 意味着暂时不修，继续推进写作，之后统一修。

**处理方式：**
```
审核发现问题 → 报告给用户 → 用户说"跳过" → 归档当前任务 → 立即开始下一批写作
```

**不要做的事：**
- ❌ 不要反复问"要修吗？" — 用户已说跳过
- ❌ 不要创建修复任务 — 用户不想修
- ❌ 不要停下等用户确认 — 直接写下一批

**适合跳过的问题：**
- 高频词略超（仿佛1-3次、某种4-5次）
- 字数略超上限（6000-7000字）
- 打字错误

**不适合跳过的问题：**
- 字数严重不足（<3000字）
- 禁用词大量出现
- 剧情矛盾
- 设定错误

**事后处理：** 整卷写完后，统一修一轮高频词（用Python正则批量替换）比逐章修更高效。

### 35e3. 并行写作导致世界观跑偏（2026-06-25 实战验证）

**问题：** 并行dispatch多个写作任务（不同情节点同时写），后半批章节完全丢失了原世界观，自己编了一套设定。

**实测案例：** 第七卷扩写，前半部分（334-345章）正确使用"雾港""共济会三派"设定，但后半部分（346-378章）突然引入"西区""裁决所""黑巫师""蒸汽步枪""畸变者"等完全不存在的元素。23章需要重写。

**根因：** 并行写作时，每个worker只读取了大纲和前驱章节，但没有读取完整的世界观设定文件。不同worker独立生成内容，导致世界观碎片化。

**诊断：** grep关键词检查：
```bash
# 检查跑偏内容
for keyword in "西区" "裁决所" "黑巫师" "蒸汽步枪" "畸变者"; do
  count=$(grep -rl "$keyword" 第*章_*.md 2>/dev/null | wc -l)
  [ "$count" -gt 0 ] && echo "⚠️ $keyword: $count章"
done
```

**预防：** 写作任务body中必须包含核心世界观约束：
```
⚠️ 重要：严格按原世界观写，不要引入以下不存在的设定：
- 地名：西区、深渊、北境等（原设定为"雾港"地面城市）
- 组织：裁决所、黑巫师集会、圣光骑士团（原设定为共济会三派）
- 物品：蒸汽步枪、畸变者、血肉教派（原设定为金齿轮封印体系）
- 角色能力：杰克是鉴定能力者/事务所所长，不是清道夫/战士
```

**修复：** 跑偏章节需要整体重写，不能只改关键词（因为整个剧情逻辑都错了）。

**教训：** 并行写作速度虽快，但必须在每个task body中包含完整的世界观红线。宁可多写几行约束，也不要事后重写23章。

### 35e2. "先写完再统一审"模式（2026-06-24 实战验证）

**用户指令：** "先全扩写完再审查吧，按情节点扩写，写完直接下一部分直到写完"

**含义：** 不走"写→审→修→审"的逐批循环，而是先把所有章节写完，最后统一做一次终审。

**流程：**
```
写情节点一（2-3章）→ 写情节点二（2-4章）→ ... → 写情节点十二 → 全卷终审 → 统一修 → 再审
```

**与标准流程的区别：**
| 标准流程 | "先写完再审"模式 |
|---------|----------------|
| 每批写完→审→修→再审 | 全部写完→一次终审→统一修 |
| 质量逐批保证 | 整体质量靠终审兜底 |
| 适合正式发布 | 适合初稿快速产出 |
| 修的轮次多（每批2-3轮） | 修的轮次少（全卷1-2轮） |

**适用场景：**
- 大纲明确，剧情走向已确定
- 用户更关心进度而非单章质量
- 有终审+统一修的兜底机制

**⚠️ 必须有终审：** 不能"写完就完"，必须走一次lili全卷终审+统一修复。

**模板脚本：** `references/fix-review-loop-template.py` — 可复制后修改常量直接使用

## Time Estimates

Based on observed patterns:
- **Writing 5-7 chapters:** 15-30 minutes
- **Writing 8 chapters:** 25-30 minutes (but causes issues — prefer 5-7)
- **Review (8 chapters):** 1-2 minutes
- **Modification (2-3 chapters):** 3-10 minutes
- **Modification (4 chapters):** 5-15 minutes
- **Modification (8 chapters):** Fails (decompose instead)
- **Full review + modification cycle:** ~45 minutes total

## Monitoring Frequency

When monitoring kanban tasks in the background, adjust check interval based on task complexity:

| Task Type | Check Interval | Rationale |
|-----------|---------------|-----------|
| Simple (single chapter edit) | 1-5 minutes | Fast completion |
| Medium (3-5 chapters writing) | 5-15 minutes | Standard writing task |
| Complex (7-8 chapters writing) | 15-30 minutes | Large batch, longer runtime |
| Review tasks | 5-10 minutes | Review is fast but needs attention |

**Automated monitoring**: Use the Gateway native kanban notifier (section 14 — auto-subscribe on task creation). The old cron-based approach (`references/kanban-done-notifier.md`) is deprecated.

**Implementation pattern:**
```bash
# Background monitoring with adaptive interval
terminal(
    background=True,
    notify_on_complete=True,
    command="while true; do
      status=$(hermes kanban show <task_id> 2>&1 | grep 'status:' | awk '{print $2}')
      if [ \"$status\" = \"done\" ] || [ \"$status\" = \"blocked\" ]; then
        echo \"Task completed! Status: $status\"
        break
      fi
      sleep <interval>  # 60-1800 seconds based on complexity
    done"
)
```

**Why this matters:** Checking too frequently wastes resources; checking too rarely delays notification. Match interval to expected task duration.

## Real-World Performance Data

### Parallel Model Comparison Workflow (2026-06-11)

**Pattern:** Compare output quality between two different models on the same modification task.

**Workflow:**
1. Create Task A (`--assignee shanli`) → modifies files in original directory
2. Create Task B (`--assignee shanli-agnes20flash`) → modifies files in a **SEPARATE directory**
3. Both tasks dispatch in parallel (`--max 2`)
4. After both complete → compare results (word count, quality, style)
5. User decides which version to keep

**Key requirements:**
- Task B must output to a **different directory** (e.g., `正文_agnes/`) to avoid file conflicts
- Both tasks should have identical task bodies (same modification requirements)
- Use `--max 2` when dispatching to allow both tasks to run concurrently

**Example:**
```bash
# Task A: shanli modifies original files
hermes kanban create "修改任务（闪莉版）" \
  --assignee shanli \
  --body "## 修改要求\n...\n### 输出\n修改后的文件覆盖原文件"

# Task B: shanli-agnes20flash modifies to separate directory
hermes kanban create "修改任务（Agnes版）" \
  --assignee shanli-agnes20flash \
  --body "## 修改要求\n...\n### 输出\n修改后的文件保存到：/path/to/正文_agnes/"

# Dispatch both
hermes kanban dispatch --max 2
```

**Pitfall:** If both tasks write to the same directory, they will conflict and corrupt files. Always use separate output directories for comparison tasks.

### Token Consumption (LongCat Model)
- **Daily limit:** 5M tokens
- **Typical consumption:** 500K tokens per 6 kanban tasks
- **Main cost driver:** Redundant file reads (47 reads vs optimal 16 reads)

### Optimization Results (Verified)
| Metric | Before Optimization | After Optimization | Improvement |
|--------|---------------------|-------------------|-------------|
| Read operations per task | 47 | 16 | -66% |
| Total operations | 81 | 31 | -62% |
| Task completion time | 81min (failed) | 7min | ✅ Completed |

### Key Learnings
1. **Chapter numbering must be explicit:** "第163-170章" not "第1-8章" — vague numbering causes wrong chapter generation
2. **Relative paths in task body:** Use "保存到：正文/ 目录下" when workspace is set to project root
3. **Modification task sweet spot:** 4 chapters per task balances overhead vs decomposition cost
4. **Review is fast:** 1-2 minutes for 8 chapters — always decompose writing/modification, never review

## Token Consumption Optimization

**Problem:** Complex tasks with many file operations consume excessive tokens (500K+ per session).

**Root Cause:** Redundant file reads — worker reads entire file after each modification to verify, leading to 10+ reads of the same file.

**Optimization Strategies:**

### 1. Reduce Verification Reads
- **Bad:** Read entire file after every modification
- **Good:** Only read the modified section, or skip verification reads entirely
- **Impact:** Can reduce reads from 13x to 2x per file

### 2. Pre-load Content in Task Body
- Include key reference content directly in the task body
- Worker doesn't need to read large files (outlines, guidelines) separately
- **Example:** Include outline chapter summaries in task body instead of worker reading 110KB outline file

### 3. Decompose by File, Not Just by Chapter
- **Bad:** "修改全部8章的所有问题" (8 files × multiple operations = 80+ ops)
- **Good:** "修改第164-166章（两稿拼接修复）" (3 files × targeted ops = ~15 ops)
- **Rule:** Each task should touch ≤3 files with ≤20 total operations

### 4. Use Patch Instead of Write for Modifications
- **Bad:** `write_file` (rewrites entire file, large output token cost)
- **Good:** `patch` (only sends changed lines, minimal output)
- **Impact:** 10x reduction in output tokens for modifications

**Token Budget Awareness:**
- LongCat model has daily token limits
- 500K tokens/day is typical for 6 kanban tasks
- Monitor with `hermes kanban log <task_id>` to identify bloated operations
