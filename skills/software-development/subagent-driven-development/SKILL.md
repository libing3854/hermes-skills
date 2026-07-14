---
name: subagent-driven-development
description: "Execute plans via delegate_task subagents (2-stage review)."
version: 1.2.0
author: Hermes Agent (adapted from obra/superpowers)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [delegation, subagent, implementation, workflow, parallel]
    related_skills: [writing-plans, requesting-code-review, test-driven-development]
---

# Subagent-Driven Development

## Overview

Execute implementation plans by dispatching fresh subagents per task with systematic two-stage review.

**Core principle:** Fresh subagent per task + two-stage review (spec then quality) = high quality, fast iteration.

## When to Use

Use this skill when:
- You have an implementation plan (from writing-plans skill or user requirements)
- Tasks are mostly independent
- Quality and spec compliance are important
- You want automated review between tasks

**vs. manual execution:**
- Fresh context per task (no confusion from accumulated state)
- Automated review process catches issues early
- Consistent quality checks across all tasks
- Subagents can ask questions before starting work

## The Process

### 1. Read and Parse Plan

Read the plan file. Extract ALL tasks with their full text and context upfront. Create a todo list:

```python
# Read the plan
read_file("docs/plans/feature-plan.md")

# Create todo list with all tasks
todo([
    {"id": "task-1", "content": "Create User model with email field", "status": "pending"},
    {"id": "task-2", "content": "Add password hashing utility", "status": "pending"},
    {"id": "task-3", "content": "Create login endpoint", "status": "pending"},
])
```

**Key:** Read the plan ONCE. Extract everything. Don't make subagents read the plan file — provide the full task text directly in context.

### 2. Per-Task Workflow

For EACH task in the plan:

#### Step 1: Dispatch Implementer Subagent

Use `delegate_task` with complete context. Default tier: ⚡ **闪莉** (routine implementation work).

```python
delegate_task(
    # ⚡ 闪莉 — 日常编码任务用闪速模型，够用又快
    model={model: "deepseek-v4-flash"},
    goal="Implement Task 1: Create User model with email and password_hash fields",
    context="""
    TASK FROM PLAN:
    - Create: src/models/user.py
    - Add User class with email (str) and password_hash (str) fields
    - Use bcrypt for password hashing
    - Include __repr__ for debugging

    FOLLOW TDD:
    1. Write failing test in tests/models/test_user.py
    2. Run: pytest tests/models/test_user.py -v (verify FAIL)
    3. Write minimal implementation
    4. Run: pytest tests/models/test_user.py -v (verify PASS)
    5. Run: pytest tests/ -q (verify no regressions)
    6. Commit: git add -A && git commit -m "feat: add User model with password hashing"

    PROJECT CONTEXT:
    - Python 3.11, Flask app in src/app.py
    - Existing models in src/models/
    - Tests use pytest, run from project root
    - bcrypt already in requirements.txt
    """,
    toolsets=['terminal', 'file']
)
```

#### Step 2: Dispatch Spec Compliance Reviewer

After the implementer completes, verify against the original spec. Tier: ⚡ **闪莉** (routine verification).

```python
delegate_task(
    # ⚡ 闪莉 — 规范检查是规则匹配，日常任务
    model={model: "deepseek-v4-flash"},
    goal="Review if implementation matches the spec from the plan",
    context="""
    ORIGINAL TASK SPEC:
    - Create src/models/user.py with User class
    - Fields: email (str), password_hash (str)
    - Use bcrypt for password hashing
    - Include __repr__

    CHECK:
    - [ ] All requirements from spec implemented?
    - [ ] File paths match spec?
    - [ ] Function signatures match spec?
    - [ ] Behavior matches expected?
    - [ ] Nothing extra added (no scope creep)?

    OUTPUT: PASS or list of specific spec gaps to fix.
    """,
    toolsets=['file']
)
```

**If spec issues found:** Fix gaps, then re-run spec review. Continue only when spec-compliant.

#### Step 3: Dispatch Code Quality Reviewer

After spec compliance passes. Tier: choose based on complexity:
- ⚡ **闪莉** — routine style/pattern review
- 🚀 **大莉** — security audit, deep logic analysis, complex edge cases

```python
delegate_task(
    # 🚀 大莉 — 安全审查+深度逻辑检查用 Pro 模型
    # ⚡ 闪莉 — 日常风格/模式检查用 Flash 即可
    model={model: "deepseek-v4-pro"},  # switch to deepseek-v4-flash for routine reviews
    goal="Review code quality for Task 1 implementation",
    context="""
    FILES TO REVIEW:
    - src/models/user.py
    - tests/models/test_user.py

    CHECK:
    - [ ] Follows project conventions and style?
    - [ ] Proper error handling?
    - [ ] Clear variable/function names?
    - [ ] Adequate test coverage?
    - [ ] No obvious bugs or missed edge cases?
    - [ ] No security issues?

    OUTPUT FORMAT:
    - Critical Issues: [must fix before proceeding]
    - Important Issues: [should fix]
    - Minor Issues: [optional]
    - Verdict: APPROVED or REQUEST_CHANGES
    """,
    toolsets=['file']
)
```

**If quality issues found:** Fix issues, re-review. Continue only when approved.

#### Step 4: Mark Complete

```python
todo([{"id": "task-1", "content": "Create User model with email field", "status": "completed"}], merge=True)
```

### 3. Final Review

After ALL tasks are complete, dispatch a final integration reviewer. Tier: 🚀 **大莉** (cross-component consistency check).

```python
delegate_task(
    # 🚀 大莉 — 跨组件整合检查需要深度推理
    model={model: "deepseek-v4-pro"},
    goal="Review the entire implementation for consistency and integration issues",
    context="""
    All tasks from the plan are complete. Review the full implementation:
    - Do all components work together?
    - Any inconsistencies between tasks?
    - All tests passing?
    - Ready for merge?
    """,
    toolsets=['terminal', 'file']
)
```

### 4. Verify and Commit

```bash
# Run full test suite
pytest tests/ -q

# Review all changes
git diff --stat

# Final commit if needed
git add -A && git commit -m "feat: complete [feature name] implementation"
```

## Task Granularity

**Each task = 2-5 minutes of focused work.**

**Too big:**
- "Implement user authentication system"

**Right size:**
- "Create User model with email and password fields"
- "Add password hashing function"
- "Create login endpoint"
- "Add JWT token generation"
- "Create registration endpoint"

## Model Tier System: 🏠 小莉 / 🐣 闪莉mimi / ⚡ 闪莉 / 🚀 大莉

For Chinese-language environments, subagents can be classified into three tiers by model capability. This provides a quick mental model for choosing the right subagent for each task.

| Tier | Name | Model | When to Use |
|------|------|-------|-------------|
| 🐣 **Mimi** | **闪莉mimi** | NVIDIA NIM pool (<4B or <10B+<5s) | 小莉's backup when busy — file ops, content gen, code writing |
| 🏠 **Local** | **小莉** | Local model (gemma-4-e4b at localhost:1234) | File read/write, text generation, code writing, batch template processing — pure local work, no network needed |
| ⚡ **Flash** | **闪莉** | NVIDIA NIM multi-model pool (37 models, concurrent racing) | Routine search, information gathering, daily tasks, image understanding — **majority of daily work** |
| 🚀 **Deep** | **大莉** | Pro-tier model (e.g. deepseek-v4-pro) | Complex reasoning, financial analysis, cross-validation, security audits — heavy lifting |

> ⚠️ **Naming note**: The Flash-tier sub-agent is called **闪莉** (Li Shan), not **莉莉** (Li Li), to avoid confusion with the primary AI assistant **莉莉丝** (Lilith). This was a deliberate renaming after 大莉 reviewed the original spec and flagged the ambiguity.

### Quick decision guide

```
Task arrives — first, self-assess complexity (⭐1-5):
⭐ Simple question/light task?        → Answer directly, no sub-agent needed
⭐⭐⭐+  Need help?                      → Pick a combination pattern below

What does this task need?\n├─ 💬 Simple Q&A / lightweight?       → Answer directly myself\n├─ 💻 Pure local processing?          → 🏠 小莉 (profile-based: xiaoli chat -q '...')\n│  └─ 小莉 busy?                      → 🐣 闪莉mimi (NVIDIA, same capability)\n├─ 🌐 Web search / information?       → ⚡ 闪莉 (NVIDIA NIM multi-model racing)\n├─ 🧠 Deep reasoning / analysis?      → 🚀 大莉 (delegate_task with pro model)\n├─ 🔍 Two or more needed?             → Use a combination pattern below\n└─ ❓ Not sure?                       → Ask the user 😊
```

### How to invoke each tier

```python
# 🏠 小莉 — Local model, profile-based
terminal(background=true, notify_on_complete=true, command="xiaoli chat -q '指令'")

# 🐣 闪莉mimi — 小莉's backup via NVIDIA NIM (for when 小莉 is busy)
# See references/nvidia-nim-models.md for model list

# ⚡ 闪莉 — NVIDIA NIM multi-model pool, concurrent racing (default)
# See references/nvidia-nim-models.md for racing strategy and model selection

# 🚀 大莉 — Pro model, delegate_task (heavy tasks only)
delegate_task(tasks=[{goal: "deep task", model: {model: "deepseek-v4-pro"}}])
```

### Mixed-tier parallel execution

`delegate_task` supports `tasks:[...]` for parallel execution. Mix flash and pro tiers in the same batch:

```python
delegate_task(tasks=[
    {goal: "Quick web search for recent news", model: {model: "deepseek-v4-flash"}},
    {goal: "Cross-validate financial report data", model: {model: "deepseek-v4-pro"}},
])
```

This keeps the common work fast (flash) while reserving expensive context for the tasks that genuinely need it.

### Combination Patterns (组合模式)

**Core idea**: Higher-tier agents bring lower-tier agents along to work in parallel, not solo. Think of it as teaming up rather than single-dispatch.

| # | Pattern | When | Flow |
|---|---------|------|------|
| 1 | 🐣 **闪莉mimi solo** | 小莉 is busy, cloud backup needed | 莉莉丝→闪莉mimi(NVIDIA)→校验→交付 |\n| 2 | 🏠 **小莉 solo** | Pure local, no network | 莉莉丝→小莉(background)→校验→交付 |\n| 3 | ⚡🏠 **闪莉 + 小莉** | Web search + local processing | 闪莉(NVIDIA racing) ∥ 小莉(file) → 莉莉丝汇总→交付 |\n| 4 | 🚀🏠 **大莉 + 小莉** | Deep analysis + file output | 大莉(reason) ∥ 小莉(output) → 莉莉丝校验→交付 |\n| 5 | 🚀⚡ **大莉 + 闪莉** | High-difficulty + multi-source research | 大莉(reason) ∥ 闪莉(NVIDIA search) → 大莉汇总 → 莉莉丝终检 |\n| 6 | 🚀⚡🏠 **全家桶** | Large complex project, all three | 大莉(core) ∥ 闪莉(search) ∥ 小莉(file) → 大莉汇总 → 莉莉丝终检 |

### Quick-match table

| Task Characteristics | Best Pattern | ❌ Don't Use | Example |\n|---------------------|-------------|-------------|---------|\n| 小莉 busy, need local-like work | 🐣 闪莉mimi solo | 全家桶/大莉 | Backup file processing |\n| Pure local, no network | 🏠 小莉 solo | 全家桶/大莉 | Batch file rename, template gen |\n| Daily search + local output | ⚡🏠 闪莉+小莉 | 大莉出场 | News gather + write report |\n| Deep analysis + local output | 🚀🏠 大莉+小莉 | 闪莉 solo (underpowered) | Financial report + table |\n| Hard task + multi-source | 🚀⚡ 大莉+闪莉 | 小莉 solo (can't) | Industry research, competitor |\n| Large project full-stack | 🚀⚡🏠 全家桶 | Missing one = broken chain | Complete research project |

### Pitfalls

- **⚠️ CRITICAL: `delegation` config ≠ `delegate_task` model** — The `delegation.provider`/`delegation.model` settings in config.yaml do NOT control what model `delegate_task` uses. You MUST pass `model` explicitly in each task: `delegate_task(tasks=[{goal, model: {model: "agnes-2.0-flash"}}])`. Forgetting this causes delegate_task to use the session's default model (often expensive deepseek-v4-pro). **Cost of this mistake: ¥112 in one session** (671 calls × 5575万 tokens). Always specify model explicitly, even for "simple" tasks.
- **Don't overuse Pro** — Pro models cost more and run slower. Reserve for data-heavy or reasoning-intensive tasks.
- **小莉 has no network access** — Don't assign web searches or API calls to the local model.
- **Profile names matter** — The wrapper name (e.g. `xiaoli`) must match the profile name in Hermes config.
- **Combination patterns require parallel thinking** — Don't sequence sub-agents when they can run in parallel. Always check dependencies first (true parallel vs pipeline vs avoidable false-parallel).
- **Always validate after combination** — Multi-agent outputs can conflict. Check for contradictions before delivery (大莉 > 闪莉 > 小莉 in priority).

## Alternative: Profile-Based Subagent

An alternative to `delegate_task` is dispatching a **profile-based subagent** via terminal:

```bash
terminal(
  background=True,
  notify_on_complete=True,
  command="hermes --profile <name> chat -q 'task instruction' -Q"
)
# or if a wrapper exists:
terminal(
  background=True,
  notify_on_complete=True,
  command="<wrapper> chat -q 'task instruction' -Q"
)
```

### Trade-offs vs delegate_task

| Aspect | `delegate_task` | Profile-based |
|--------|----------------|---------------|
| Model | Inherits parent's model | **Independent** — profile has own model/provider |
| Skills | Inherits parent's toolset | Only has profile's installed skills |
| Duration | Bounded by parent loop | Fully independent, no time limit |
| Output | Returns summary string | Produces files or terminal output |
| Cost | Uses parent's API key | Uses profile's own config |
| Best for | Quick parallel subtasks | Long-running or local-model tasks |

### Pitfalls

- **Custom skills don't sync** — Profile creation only syncs builtin skills. Custom skills must be installed separately or instructions provided inline.
- **Provider naming** — In profile config.yaml, use `model.provider: custom` (the config key), NOT the display name like `custom:Local (localhost:1234)` (which causes "Unknown provider" errors).
- **Local model timeout** — Local models (gemma-4-e4b, etc.) may timeout on complex multi-step tasks (>600s). Best for focused, scoped tasks.
- **Wrapper scripts** — `hermes profile create` auto-generates a wrapper script (e.g. `xiaoli` at `~/.local/bin/`). Use `wrapper chat -q '...'` for convenience.
- **Output cleanup** — Shell redirect `> file 2>&1` mixes terminal artifacts with output. Clean the file after completion.

### When to use which

- **Use `delegate_task`** when: tasks are quick (<5min), need parent's context/tools, parallel execution
- **Use Profile-based** when: need a specific model (local/alternate), long-running tasks, independent config

## Red Flags — Never Do These

- Start implementation without a plan
- Skip reviews (spec compliance OR code quality)
- Proceed with unfixed critical/important issues
- Dispatch multiple implementation subagents for tasks that touch the same files
- Make subagent read the plan file (provide full text in context instead)
- Skip scene-setting context (subagent needs to understand where the task fits)
- Ignore subagent questions (answer before letting them proceed)
- Accept "close enough" on spec compliance
- Skip review loops (reviewer found issues → implementer fixes → review again)
- Let implementer self-review replace actual review (both are needed)
- **Start code quality review before spec compliance is PASS** (wrong order)
- Move to next task while either review has open issues

## Handling Issues

### If Subagent Asks Questions

- Answer clearly and completely
- Provide additional context if needed
- Don't rush them into implementation

### If Reviewer Finds Issues

- Implementer subagent (or a new one) fixes them
- Reviewer reviews again
- Repeat until approved
- Don't skip the re-review

### If Subagent Fails a Task

- Dispatch a new fix subagent with specific instructions about what went wrong
- Don't try to fix manually in the controller session (context pollution)

## Efficiency Notes

**Why fresh subagent per task:**
- Prevents context pollution from accumulated state
- Each subagent gets clean, focused context
- No confusion from prior tasks' code or reasoning

**Why two-stage review:**
- Spec review catches under/over-building early
- Quality review ensures the implementation is well-built
- Catches issues before they compound across tasks

**Cost trade-off:**
- More subagent invocations (implementer + 2 reviewers per task)
- But catches issues early (cheaper than debugging compounded problems later)

## Integration with Other Skills

### With writing-plans

This skill EXECUTES plans created by the writing-plans skill:
1. User requirements → writing-plans → implementation plan
2. Implementation plan → subagent-driven-development → working code

### With test-driven-development

Implementer subagents should follow TDD:
1. Write failing test first
2. Implement minimal code
3. Verify test passes
4. Commit

Include TDD instructions in every implementer context.

### With requesting-code-review

The two-stage review process IS the code review. For final integration review, use the requesting-code-review skill's review dimensions.

### With systematic-debugging

If a subagent encounters bugs during implementation:
1. Follow systematic-debugging process
2. Find root cause before fixing
3. Write regression test
4. Resume implementation

## Meta-Patterns

Beyond the standard implement→review→deliver loop, the three-tier subagent system supports higher-order patterns for maintaining and improving the skills themselves.

### Meta-Pattern 1: 大莉 Self-Review (Workflow Document Audit)

Use the top-tier agent (**🚀 大莉**) to audit your own workflow documents and skill specs. This was demonstrated concretely in a session where 大莉 reviewed the 莉莉丝工作规范 and produced a structured 5-dimension evaluation:

| Dimension | Rating | What It Checks |
|-----------|--------|----------------|
| 逻辑完整性 (Logic) | 1-10 | Are the rules clear, non-contradictory, complete? |
| 可操作性 (Operability) | 1-10 | Can the steps be executed as written? |
| 安全性 (Safety) | 1-10 | Are security checkpoints adequate? |
| 效率 (Efficiency) | 1-10 | Is the workflow economical with resources? |
| 风格一致性 (Style) | 1-10 | Does the tone match the assistant's persona? |

**When to use:** After creating or significantly rewriting a workflow document, skill SKILL.md, or specification. Always dispatch with `model: {model: "deepseek-v4-pro"}`.

**Output artifact:** A structured review with priority-sorted improvement recommendations (high/medium/low) and specific patch suggestions for each issue found.

### Meta-Pattern 2: 大莉 Review Loop (Code/System Architecture Review)

Beyond document audit, 大莉 excels at **deep code/system architecture review** — a structured review-repair-reverify cycle for post-implementation quality assurance.

**Concrete example from a session:** The `task_tracker.py` v1.0 was reviewed by 大莉, which identified:
- **3 P1 issues** (no hysteresis buffer → oscillation risk, no cold start → empty suggestions, no log rotation)
- **Several P2/P3 issues** (dead parameter, spike logic misaligned with spec, no time window filtering)

After applying all fixes (v1.1), 大莉 re-reviewed and gave **PASS** verdict — all 10 issues resolved.

**When to use this pattern instead of document review:**
- After writing complex code (5+ files, new module, multi-system integration)
- When you want a second opinion on architecture/design, not just style
- After `requesting-code-review` passes but you want deeper reasoning

**The three-phase loop:**
1. Dispatch 大莉 with full system context → get P1/P2/P3 prioritized findings
2. Apply fixes in priority order
3. Re-review by 大莉 to verify all issues resolved + no regressions

**See `references/大莉-review-loop.md`** for the full protocol: review format, real-world example, when to stop (PASS/CONDITIONAL/FAIL), and relationship to other review patterns.

### Meta-Pattern 3: Batch Skill Triage

Occasionally, scan the entire skill library for sub-agent calls and upgrade them systematically. This ensures all skills stay aligned with the three-tier system.

**Workflow:**

```
1. Scan: search_files(pattern="delegate_task", path="~/.hermes/skills")
         + search_files(pattern="xiaoli", path="~/.hermes/skills")
         + search_files(pattern="deepseek-v4-pro", path="~/.hermes/skills")

2. Analyze: Classify each skill's sub-agent calls into:
   - Already correct (no change needed)
   - Needs tier annotation (add model parameter to delegate_task)
   - Needs Chinese name (add 又名 to description)
   - Needs Git init (create repo + tag)

3. Execute: Patch each skill's SKILL.md with tier annotations

4. Version: Commit Git repos for versioned skills, tag with SemVer

5. Update references/skill-tier-mapping.md with the canonical mapping
```

**Tier classification rules applied during triage:**

| Task Type | Default Tier | Rationale |
|-----------|-------------|-----------|
| Code implementation | ⚡ 闪莉 | Routine, Flash is sufficient |
| Code review (security) | 🚀 大莉 | Deep analysis required |
| Web search (routine) | ⚡ 闪莉 | Information gathering |
| Web search (cross-validation) | 🚀 大莉 | Multiple sources need reconciliation |
| Local file processing | 🏠 小莉 | No network, pure local |
| Security audit | 🚀 大莉 | Must be Pro-level |
| Debug (simple/known) | ⚡ 闪莉 | Pattern matching |
| Debug (complex/cross-component) | 🚀 大莉 | Requires deep reasoning |

**When to triage:** After any major system change (new model tier added, naming convention updated, new skill added that uses sub-agents). Also useful as a periodic maintenance task.

## Example Workflow

```
[Read plan: docs/plans/auth-feature.md]
[Create todo list with 5 tasks]

--- Task 1: Create User model ---
[Dispatch implementer subagent]
  Implementer: "Should email be unique?"
  You: "Yes, email must be unique"
  Implementer: Implemented, 3/3 tests passing, committed.

[Dispatch spec reviewer]
  Spec reviewer: ✅ PASS — all requirements met

[Dispatch quality reviewer]
  Quality reviewer: ✅ APPROVED — clean code, good tests

[Mark Task 1 complete]

--- Task 2: Password hashing ---
[Dispatch implementer subagent]
  Implementer: No questions, implemented, 5/5 tests passing.

[Dispatch spec reviewer]
  Spec reviewer: ❌ Missing: password strength validation (spec says "min 8 chars")

[Implementer fixes]
  Implementer: Added validation, 7/7 tests passing.

[Dispatch spec reviewer again]
  Spec reviewer: ✅ PASS

[Dispatch quality reviewer]
  Quality reviewer: Important: Magic number 8, extract to constant
  Implementer: Extracted MIN_PASSWORD_LENGTH constant
  Quality reviewer: ✅ APPROVED

[Mark Task 2 complete]

... (continue for all tasks)

[After all tasks: dispatch final integration reviewer]
[Run full test suite: all passing]
[Done!]
```

## Remember

```
Fresh subagent per task
Two-stage review every time
Spec compliance FIRST
Code quality SECOND
Never skip reviews
Catch issues early
```

**Quality is not an accident. It's the result of systematic process.**

## Further reading (load when relevant)

When the orchestration involves significant context usage, long review loops, or complex validation checkpoints, load these references for the specific discipline:

- **`references/大莉-review-loop.md`** — Three-phase review-repair-reverify protocol for deep code/system architecture review using 大莉 (Pro model). Includes review format (P1/P2/P3 findings with ✅/⚠️/🔴 severity), real-world example from `task_tracker.py` upgrade, termination criteria (PASS/CONDITIONAL/FAIL), and relationship to other review patterns. Load when you've built something non-trivial and want a second architectural opinion before shipping.
- **`references/three-tier-subagent-system.md`** — The 小莉/闪莉mimi/闪莉/大莉 model tier hierarchy: definitions, decision guide, invocation patterns, combination patterns (6 teamwork modes), safety/validation rules, and the self-review meta-pattern. Load when choosing which sub-agent tier to delegate a task to, or when orchestrating multi-agent parallel workflows.\n- **`references/nvidia-nim-models.md`** — Complete NVIDIA NIM model classification: 37 working models across 4 tiers (mimi/轻量/强), ping groups (A/B alternating every 30min), concurrent racing strategy, fallback chains, and 小莉 integration. Load when dispatching 闪莉 or 闪莉mimi to understand which models are available and how the racing mechanism works.
- **`references/skill-tier-mapping.md`** — Canonical tier assignments for every skill in the library. Quick-reference table of which task types map to which tier, plus the "default to 闪莉, escalate to 大莉" rule of thumb. Load when applying the tier system to a new skill or reminding yourself of established conventions.
- **`references/context-budget-discipline.md`** — Four-tier context degradation model (PEAK / GOOD / DEGRADING / POOR), read-depth rules that scale with context window size, and early warning signs of silent degradation. Load when a run will clearly consume significant context (multi-phase plans, many subagents, large artifacts).
- **`references/gates-taxonomy.md`** — The four canonical gate types (Pre-flight, Revision, Escalation, Abort) with behavior, recovery, and examples. Load when designing or reviewing any workflow that has validation checkpoints — use the vocabulary explicitly so each gate has defined entry, failure behavior, and resumption rules.
- **`references/adaptation-dual-review-pattern.md`** — Dual-reviewer pattern for code migration/adaptation: one subagent for functionality consistency, another for modification reasonableness. Use when porting code between platforms (e.g., Claude Code skill → Hermes Agent skill).

Context budget and gates references adapted from gsd-build/get-shit-done (MIT © 2025 Lex Christopherson).
