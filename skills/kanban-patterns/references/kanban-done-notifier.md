# Kanban Done Notifier (DEPRECATED)

> **⚠️ DEPRECATED (2026-06-13):** This cron-based notifier has been replaced by the Gateway native kanban notifier. The cron job `bdbe2ad194e3` was removed. Use `kanban_notify_subs` table subscriptions instead (see SKILL.md section 14).

## Overview

The cron-based `kanban_done_notifier.py` has been **deleted** at user request.
Replaced by Gateway native notifier + auto-subscribe on task creation.

See SKILL.md section 14 "Auto-Subscribe Kanban Notifications on Task Creation"
for the current approach.

## Historical Reference (kept for diagnostics)

### Script Location (no longer exists)
`~/.hermes/scripts/kanban_done_notifier.py`

## How It Works

1. Calls `hermes kanban list --json` to get all non-archived tasks
2. Compares current state against a snapshot file (`~/.hermes/data/kanban_done_state.json`)
3. Detects tasks that changed to `done` since last check
4. Filters out auto-tasks (cron, monitoring, scheduled) by keyword matching
5. Outputs notification text (cron auto-delivers) or stays silent

## Auto-Task Filtering

The script filters out tasks containing these keywords in title or body:

```
提醒, 监控, 自动, cron, schedule
每日, 早报, 喝水, 健康, 金融
天气, 新闻, 日报, 周报
```

This prevents notification spam from recurring automated tasks.

## Cron Job Setup

```bash
hermes cron create \
  --name "看板任务完成提醒" \
  --schedule "*/15 * * * *" \
  --script "~/.hermes/scripts/kanban_done_notifier.py" \
  --no-agent \
  --deliver origin
```

- **Interval**: 15 minutes (adjustable)
- **Mode**: `no_agent=True` (pure script, zero token cost)
- **Delivery**: Auto-delivers to current session when output is non-empty

## Manual Testing

```bash
# Test the script directly
python3 ~/.hermes/scripts/kanban_done_notifier.py

# Check state file
cat ~/.hermes/data/kanban_done_state.json | python3 -m json.tool | head -20

# Reset state (re-detect all done tasks)
rm ~/.hermes/data/kanban_done_state.json
```

## Integration with Novel Writing Pipeline

The notifier is used in the novel writing workflow:

1. Agnes modification task completes → notifier fires
2. Cron job detects completion → creates莉莉 review task automatically
3. Review task completes → notifier fires again

This creates a hands-off write→review→modify→review cycle.

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Pure script (no_agent) | Zero token cost for monitoring |
| State file comparison | Only notifies on NEW completions, not repeated |
| Keyword filtering | Avoids spam from cron-generated tasks |
| 15-minute interval | Balance between responsiveness and resource usage |
| Silent on no change | No notification = no noise |

## Diagnostic Checklist

When the notifier appears not to work, follow this order (most reliable first):

| Check | Command | What to look for |
|-------|---------|------------------|
| Execution history | `ls -la ~/.hermes/cron/output/bdbe2ad194e3/` | Recent .md files with timestamps |
| Gateway status | `hermes gateway status` | "✓ Gateway service is loaded" + PID |
| Gateway process | `ps aux \| grep hermes_cli.main gateway` | PID should match launchd plist |
| Script works | `python3 ~/.hermes/scripts/kanban_done_notifier.py` | Empty output = no new done tasks (normal) |
| State file | `cat ~/.hermes/data/kanban_done_state.json` | JSON with task_id→status mappings |
| Gateway logs | `tail -20 ~/.hermes/logs/gateway.log` | Look for cron/ticker entries |
| Manual trigger | `cronjob action=run job_id=bdbe2ad194e3` | Should show last_status: "ok" |

**⚠️ Known false negative:** `hermes cron status` may say "Gateway is not running" even when it IS running via launchd. Trust `hermes gateway status` instead (see SKILL.md "Cron Job Diagnostic Pitfall" section).

**When script output is empty:** This is NORMAL behavior (no new done tasks). To verify the script works, temporarily modify `~/.hermes/data/kanban_done_state.json` to remove a done task's entry — the next run should detect it as "newly done" and produce output.
