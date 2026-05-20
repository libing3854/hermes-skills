# 🚀 大莉 Review Loop (Code/System Architecture Review)

## Overview

A structured review-repair-reverify cycle using 大莉 (Pro model, `deepseek-v4-pro`) for deep code/system architecture review. Unlike lightweight pre-commit checks (see `requesting-code-review`), this pattern is for **post-implementation architecture review** — a second set of critical eyes on the design, not just syntax/style.

**Core principle:** After implementation, spawn 大莉 with full system context for a deep, structured review. Prioritize findings, fix them, then re-review for closure.

## When to Use

- After significant code/system work (5+ files touched, new module, refactor)
- After writing a complex script, tool, or service (like `task_tracker.py`)
- When the code touches multiple subsystems (ping system, task scheduling, data pipeline)
- When you want a **second opinion** on architecture/design decisions
- After `requesting-code-review` passes (pre-commit clean) but you want deeper review

**Don't use for:** Simple one-off scripts, documentation-only work, trivial bug fixes.

## The Pattern: Three-Phase Loop

### Phase 1: Dispatch 大莉 with Full Context

Provide complete system context so 大莉 understands the big picture:

```python
delegate_task(
    goal="Review the new <system> implementation comprehensively",
    context="""
    CONTEXT: What this system does, why it exists, where it fits.
    FILES: List every relevant file with purpose.
    DESIGN: Key design decisions made.

    REVIEW DIMENSIONS:
    1. Logic — Is the approach sound? Any edge cases missed?
    2. Reliability — Error handling, edge cases, failure modes?
    3. Stability — Oscillation risk, feedback loops, race conditions?
    4. Maintainability — Code structure, naming, clarity?
    5. Integration — Works with existing systems?
    6. Correctness — Does it actually do what the spec says?

    OUTPUT FORMAT:
    - Use ✅/⚠️/🔴 for severity
    - Prioritize findings as P1 (blocking), P2 (important), P3 (nice-to-fix)
    - Include specific fix suggestions for each issue
    - End with "overall verdict" (PASS / CONDITIONAL/PASS / FAIL)
    """,
    model={model: "deepseek-v4-pro"},
    toolsets=["file", "terminal"]
)
```

### Phase 2: Apply Fixes

Read 大莉's findings, apply fixes in priority order (P1 → P2 → P3). Each fix should be focused — one issue per change.

**Best practice:** For each P1/P2 fix, save a brief note of what was changed and why, so 大莉 can verify in Phase 3.

### Phase 3: Re-review by 大莉

Dispatch 大莉 again with:
1. The original context (what the system does)
2. The original findings list
3. What was fixed and how

```python
delegate_task(
    goal="Re-review after fixes. Verify all P1/P2 issues are resolved.",
    context=f"""
    ORIGINAL REVIEW FINDINGS (for reference):
    {original_findings}

    FIXES APPLIED:
    - [P1] Hysteresis buffer added (dual threshold 2500/3500)
    - [P1] Cold start defaults added
    - [P2] Time window filtering implemented
    ...

    SYSTEM CONTEXT (same as first review):
    {system_context}

    CHECK:
    - [ ] All P1 issues resolved?
    - [ ] All P2 issues resolved?
    - [ ] Fixes didn't introduce new issues?
    - [ ] Any new findings on the updated code?

    OUTPUT same format as Phase 1:
    - Overall verdict: PASS / CONDITIONAL-PASS / FAIL
    - Any remaining issues
    - Any new issues introduced by fixes
    """,
    model={model: "deepseek-v4-pro"},
    toolsets=["file", "terminal"]
)
```

## 大莉's Review Format (Canonical)

大莉 naturally produces this structured output when given good context:

```
## 1. ✅ Fix Verification Checklist (逐项核查)

| # | Fix Item | Status | Verification |
|---|----------|--------|-------------|
| 1 | Hysteresis buffer | ✅ Pass | Dual thresholds implemented in _decide_group() |
| 2 | Cold start defaults | ✅ Pass | DEFAULT_RECOMMENDATIONS defined |

## 2. 🔴/🟡/🟢 New Findings

### P1 — [Issue] (Severity)
- Detail
- Why it matters
- Fix suggestion

### P2 — [Issue] (Medium)
...

### P3 — [Issue] (Minor)
...

## 3. ⚠️ Boundary Cases Check

| Scenario | Handled? | Notes |
|----------|----------|-------|
| File missing | ✅ | Falls back to "normal" |
| All records are failures | ⚠️ | Silently skipped |

## 4. ✅ Overall Verdict

**PASS** — All P1/P2 issues resolved, no new issues introduced.
```

## Real-World Example: `task_tracker.py` v1.0 → v1.1

The pattern was used to upgrade the task execution tracker from prototype to production-ready:

**Phase 1 findings (P1):** No hysteresis buffer → oscillation risk, no cold start data → empty suggestions on first run, no log rotation → unbounded growth

**Phase 2 fixes:** Added dual-threshold hysteresis (2500/3500ms), cold start defaults dict, 7-day time window filter, short-task exemption (<1500ms), spike → local model fix, `force_refresh` cleanup, rationale/by_group_stats/config/sample_counts fields

**Phase 3 re-review:** All 10 issues resolved (✅ 10/10). PASS verdict. Two minor suggestions (P3) for completeness.

## Pitfalls

- **Don't skip Phase 3** — The re-review catches fix-induced regressions
- **Don't overload context** — Keep the context focused; 大莉 has high token capacity but clarity matters
- **Don't mix review types** — Code review vs document review vs design review need different lenses
- **Don't fix everything at once** — Apply P1 → P2 → P3 sequentially; P3 can wait for a follow-up
- **Don't use ⚡ 闪莉 for this** — Deep architecture review requires Pro-level reasoning; flash models miss subtle design issues

## When to Stop

The loop terminates when:
1. **PASS** — No remaining P1/P2 issues. P3 issues captured for later.
2. **CONDITIONAL PASS** — P1 resolved, minor P2 remaining with known workaround (document the caveat)
3. **FAIL after 2 cycles** — Something fundamentally wrong. Escalate to human (冰哥) for design rethink.

## Relationship to Other Review Patterns

| Pattern | Tool | Scope | Depth | Phase |
|---------|------|-------|-------|-------|
| `requesting-code-review` | ⚡ 闪莉 | Pre-commit safety | Shallow (security, style) | Before commit |
| **大莉 Review Loop** | 🚀 大莉 | Post-impl architecture | Deep (design, edge cases) | After system built |
| 大莉 Self-Review (Meta-pattern) | 🚀 大莉 | Workflow docs | Deep (logic, style) | After doc rewrite |
| 大莉 Final Integration (SDD) | 🚀 大莉 | Cross-component | Deep (consistency) | After all tasks done |

The 大莉 Review Loop is the **deepest** — it's for when code exists but you want a second architectural opinion. Use it sparingly; it burns Pro tokens.
