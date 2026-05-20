# Skill-Tier Mapping (技能-分级对照表)

> 记录了 2026-05-17 会话中分析的 7 个技能的 sub-agent 调用分级规划。
> 以后新技能或新任务可以直接参考这里的分配逻辑。

## Overview

When using `delegate_task` in any skill, always specify which tier the sub-agent should use. This table documents the canonical tier assignments for every skill in the library that calls sub-agents.

## Canonical Mapping

| Skill | Sub-Agent Call | Assigned Tier | Reasoning |
|-------|---------------|---------------|-----------|
| `subagent-driven-development` | Implementer | ⚡ **莉闪** | Routine code implementation — Flash is fast enough |
| | Spec compliance reviewer | ⚡ **莉闪** | Rule-matching verification, no deep reasoning needed |
| | Code quality reviewer | ⚡ 莉闪 / 🚀 **大莉** | Routine style → Flash; security/deep logic → Pro |
| | Final integration review | 🚀 **大莉** | Cross-component consistency requires deep reasoning |
| `hermes-skill-creator` | findskill search (Step 0) | ⚡ **莉闪** | Routine information gathering |
| | Security audit | 🚀 **大莉** | Security = deep reasoning, must be Pro |
| | Benchmark tests | ⚡ **莉闪** (default) / 🚀 **大莉** (heavy tests) | Routine → Flash; heavy cross-validation → Pro |
| `us-stock-daily-report` | Market index data | ⚡ **莉闪** | Routine data gathering from fixed sources |
| | Hot stock picks analysis | 🚀 **大莉** | Cross-validation of multiple data points |
| | Economic news | ⚡ **莉闪** | Routine news search |
| | Local formatting via xiaoli | 🏠 **小莉** | Local file generation (already correct) |
| `requesting-code-review` | Independent reviewer | 🚀 **大莉** | Security audit + deep logic = must be Pro |
| | Code fix agent | ⚡ **莉闪** | Routine fix work, no deep analysis needed |
| `spike` | Parallel comparison spikes | ⚡ **莉闪** | Implementation spikes are routine dev work |
| `systematic-debugging` | Routine investigation | ⚡ **莉闪** | Simple reproduction, known patterns |
| | Complex root cause analysis | 🚀 **大莉** | Cross-component, race conditions, memory issues |
| `test-driven-development` | TDD implementation | ⚡ **莉闪** | Routine dev work, Pro not needed |
| `findskill` | (Called by hermes-skill-creator) | ⚡ **莉闪** | Routine search task |
| `health-daily-drink-water` | Local content generation via xiaoli | 🏠 **小莉** (already correct) | Pure local text generation, no network needed |

## Quick Reference: Which Tier for What Task

| Task Type | Tier | Examples |
|-----------|------|---------|
| Code implementation | ⚡ 莉闪 | Write function, create file, implement feature |
| Code review (security/deep) | 🚀 大莉 | Security audit, race condition analysis |
| Code review (style/routine) | ⚡ 莉闪 | Lint check, pattern compliance |
| Web search (routine) | ⚡ 莉闪 | News, docs, API references |
| Web search (cross-validation) | 🚀 大莉 | Financial data, conflicting sources |
| File read/write (local) | 🏠 小莉 | Text gen, formatting, batch processing |
| Spec compliance check | ⚡ 莉闪 | Does output match requirements? |
| Integration check | 🚀 大莉 | Do all components work together? |
| Security audit | 🚀 大莉 | Vulnerability scan, threat analysis |
| Debug (simple) | ⚡ 莉闪 | Known error pattern, single file |
| Debug (complex) | 🚀 大莉 | Multi-component, intermittent, memory/race |
| Parallel exploration | ⚡ 莉闪 | Compare two approaches, spike prototypes |

## Rule of Thumb

```
Is this task pure local processing?
├─ Yes → 🏠 小莉
No → Does it need deep reasoning, cross-validation, or security analysis?
├─ Yes → 🚀 大莉
└─ No → ⚡ 莉闪 (default for everything else)
```

**大莉 is expensive** — default to 莉闪 unless the task genuinely needs Pro-level reasoning. When in doubt, start with 莉闪 and escalate to 大莉 if execution reveals the problem is harder than expected.
