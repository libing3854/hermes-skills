# Four-Tier Subagent System (四级子代理体系)

## Origin

Created on 2026-05-17 during a conversation where the user (冰哥) refactored the 莉莉丝工作规范 (Lily's Work Specification) from a cold technical manual into a personality-driven "工作心法" (Work Philosophy). The user proposed the three-tier naming scheme, later expanded to four tiers when NVIDIA NIM multi-model support was integrated.

## Tier Definitions

| Tier | Name | Model | Call Method | When to Use |
|------|------|-------|-------------|-------------|
| 🐣 **Mimi** | **闪莉mimi** | NVIDIA NIM pool (<4B or <10B+<5s) | Via Python script → NVIDIA API | 小莉's backup when 小莉 is busy. Same use cases: file ops, content gen, code writing |
| 🏠 **Local** | **小莉** | gemma-4-e4b (localhost:1234) | `terminal + xiaoli chat -q '...'` | File read/write, text generation, code writing, batch processing — pure local, no network |
| ⚡ **Flash** | **闪莉** | NVIDIA NIM multi-model pool (37 models) | Via Python script → NVIDIA API (concurrent racing) | **Default for most work.** Routine search, info gathering, daily tasks, image understanding |
| 🚀 **Deep** | **大莉** | deepseek-v4-pro | `delegate_task(model: pro)` | Complex reasoning, financial analysis, cross-validation, security audits — heavy lifting |

> ⚠️ **Naming disambiguation**: "闪莉" (Flash) ≠ "莉莉丝" (the primary AI). "闪莉mimi" (Mimi) = 小莉's cloud backup, not a separate agent.

### Key Change: 闪莉 Uses NVIDIA NIM Multi-Model Pool

闪莉 is no longer a single flash model. It uses the NVIDIA NIM API (`nvapi-*` key, expires **2027-05-17**) with **concurrent request racing**:

1. 37 available models total (tested from ~130 listed)
2. Grouped by capability: 🐣mimi (15), 🚀轻量 (20), 🧠强 (4 within 轻量)
3. Per-task: launch 3 concurrent requests to the fastest models in the matching group
4. First response wins; remaining threads discarded
5. Latency data refreshed every 30 min via 小莉 ping (alternating Group A/Group B)

See `references/nvidia-nim-models.md` for the full model classification and ping configuration.

## Key Constraints

- **小莉 has no network**: Local model only, no web access
- **大莉 is expensive**: Use sparingly, only for tasks that genuinely need Pro-level reasoning
- **闪莉mimi** is 小莉's cloud backup: same use profile but runs on NVIDIA NIM. Used when 小莉 is busy or timing out.
- **闪莉 is default**: Most daily work falls here. Uses concurrent racing for lowest latency.
- **NVIDIA rate limit**: ~15 concurrent req/s. Keep racing groups to 3-4 models.
- **Parallel execution**: `delegate_task(tasks=[...])` can mix Flash and Pro in one batch

## Combination Patterns

The 莉莉丝工作规范 defines six teamwork patterns for multi-agent orchestration:

| # | Pattern | Flow |
|---|---------|------|
| 1 | 🐣 **闪莉mimi solo** | 莉莉丝 → 闪莉mimi (NVIDIA, 小莉替补) → validate → deliver |
| 2 | 🏠 **小莉 solo** | 莉莉丝 → 小莉(background) → validate → deliver |
| 3 | ⚡🏠 **闪莉 + 小莉** | 闪莉(NVIDIA racing) ∥ 小莉(file) → 莉莉丝 merge → deliver |
| 4 | 🚀🏠 **大莉 + 小莉** | 大莉(reason) ∥ 小莉(output) → 莉莉丝 validate → deliver |
| 5 | 🚀⚡ **大莉 + 闪莉** | 大莉(reason) ∥ 闪莉(NVIDIA search) → 大莉 merge → 莉莉丝 final check → deliver |
| 6 | 🚀⚡🏠 **全家桶 (Full Stack)** | 大莉(core) ∥ 闪莉(search) ∥ 小莉(file) → 大莉 merge → 莉莉丝 final check → deliver |

## Safety & Validation

The 莉莉丝工作规范 also defines:
- **3-tier safety**: Risk-level classification (🟢🟡🔴) + sub-agent sandbox constraints + backup-before-write policy
- **6-point validation checklist**: Format, source traceability, security scan, contradiction check, temp file cleanup, artifact cleanup
- **Error handling**: Timeout → cancel, error → retry once → downgrade, conflict → higher tier wins, cascading failure → report to user

## Self-Review Practice

A notable session practice: 大莉 (Pro model) was used to review and score the 莉莉丝工作规范 itself, producing a structured 5-dimension evaluation (logic, operability, safety, efficiency, style) with priority-sorted improvement recommendations. This demonstrates a meta-pattern: **use the top-tier agent to audit your own workflow documents**.

## Related Skills

- `subagent-driven-development` — Main skill containing the tier system documentation and combination patterns
- `hermes-skill-creator` — Uses subagents for skill creation tasks
- `references/nvidia-nim-models.md` — Full NVIDIA model classification, ping groups, and latency data
