# Batching Large Kanban Tasks + Timeout/Retry Tuning

> When a kanban task is too large for a single worker run, the worker silently exits without calling `kanban_complete` — logged as **"protocol violation: worker exited cleanly (rc=0)"**. This is NOT always a crash; it can be a timeout, an auth failure, or a context limit.

## Diagnosis: "worker exited cleanly — protocol violation"

Always check the worker log first:

```bash
hermes kanban log <task_id> | tail -30
```

This tells you whether it's an auth error, timeout, or model issue.

| Symptom | Likely Cause | Fix |
|:--------|:-------------|:----|
| Log shows `HTTP 401: incorrect api key` | **API key expired** — LongCat or other free-tier keys go stale | Renew the key at the provider's website, update `~/.hermes/.env`, then reclaim the task |
| Log shows `HTTP 403: quota exceeded` | **Free tier daily limit reached** | Switch models or wait for reset |
| Worker exits ~60s after start, no auth errors in log | Task too large for the default 8m runtime | Batch into smaller pieces + increase `--max-runtime` |
| Worker crashes with SIGTERM after N minutes | Runtime cap hit | Increase `--max-runtime` |

**Critical:** Never blindly increase `--max-runtime` for an auth-related protocol_violation. A 2h runtime on a 401 error just wastes 2 hours retrying the same auth failure. Always check the log first.

## Per-Task Runtime and Retry Flags

```bash
hermes kanban create "任务名" \
  --max-runtime 2h \      # Accepts: 90s, 30m, 2h, 1d
  --max-retries 10 \      # Max consecutive failures before blocking
  --assignee shanli
```

| Flag | Format | Default | When to Use |
|:-----|:-------|:--------|:------------|
| `--max-runtime` | `90s`, `30m`, `2h`, `1d` | 8m (from config.yaml) | Slow models (LongCat ~16 t/s), large context loads (1M tokens) |
| `--max-retries` | Integer | 2 (from config.yaml `failure_limit`) | Fragile workers that may transiently fail; give 5-10 for LongCat |

## Batching Strategy for Large Writing Tasks

When a task involves writing 28-35万字 across 55-65 chapters, **do NOT create one giant task**. Batch by 3-6 chapters per kanban task.

### Rule of Thumb

| Batch Size | Runtime | Suitable For |
|:-----------|:--------|:-------------|
| 3-6 chapters | 2h per batch | LongCat (~16 t/s) or slow free models |
| 6-10 chapters | 4h per batch | Fast models (NV NIM, Google Flash) |
| 1 batch = 1 kanban task | — | Each batch is independently completable |

### Example: Second Volume (55-65 chapters)

Instead of one task "Write all Chapter 023-068":

```bash
# Batch 1: Chapters 040-045
hermes kanban create "写书：第二卷 第040-045章" \
  --max-runtime 2h \
  --max-retries 10 \
  --assignee shanli

# After Batch 1 completes:
# Batch 2: Chapters 046-051
hermes kanban create "写书：第二卷 第046-051章" \
  --max-runtime 2h \
  --max-retries 10 \
  --assignee shanli
```

### Why Batching Works

1. **Smaller context load** — the worker only needs the current batch's outline + previous chapter summaries, not all 65 chapters
2. **Runtime is predictable** — 3-6 chapters × 5000 words = 15K-30K output tokens. At LongCat ~16 t/s, that's ~16-31 minutes of generation. Add reading/planning overhead → 2h is safe
3. **Each batch produces standalone output** — if one batch fails, only that batch is lost, not the entire second volume
4. **Progress is visible** — each completed batch = a clear milestone in the kanban board

## Slow Model Tuning (LongCat with 1M Context)

LongCat-2.0-Preview has 1M context but ~16 t/s speed. Adjustments:

- **Reading phase** — loading 1M tokens of context + outlines can take 30-60 seconds before generation starts
- **Generation phase** — 5000 words ≈ 5000-7000 tokens → 5-7 minutes of generation
- **Total per batch** — reading + planning + generation + verification ≈ 30-45 minutes for 3-6 chapters. Set `--max-runtime 2h` for safety margin
- **Retries** — if a batch occasionally fails (network blip, provider hiccup), `--max-retries 10` means it self-recovers without human intervention
- **Watch for key expiry** — LongCat free API keys can expire silently. The symptom is identical to timeout: `protocol_violation` at ~60s. Always run `hermes kanban log <id> | grep -i "401\|403\|api key\|invalid"` to rule out auth failures before tuning runtime.
