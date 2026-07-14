# Cron Job Splitting Pattern

## Problem

Some cron tasks take too long to complete within a single schedule window. Example: the financial dashboard needs to fetch data from yfinance (which can take 1-4 hours due to rate limiting), but the user wants results delivered at a specific time.

## Solution

Split into two cron jobs:

| Job | Schedule | Purpose | Deliver |
|-----|----------|---------|---------|
| **Generate** | Early (e.g., 6:00 AM) | Run the heavy computation, save results locally | `local` (no delivery) |
| **Send** | Target time (e.g., 10:00 AM) | Read saved results, format, and deliver | `discord` / `telegram` / etc. |

## Example: Financial Dashboard

```
Job 1: 金融看板生成 - 早6点执行
  Schedule: 0 6 * * *
  Script/Task: gen_v5.py → saves HTML to ~/Desktop/美股总结/
  Deliver: local (no user notification)

Job 2: 金融看板发送 - 10点推送到Discord
  Schedule: 0 10 * * *
  Task: Read latest HTML file, extract summary, upload to Discord
  Deliver: discord
  Prompt: "Find today's financial dashboard HTML at ~/Desktop/美股总结/金融看板_v5_*.html, extract summary, and send to Discord"
```

## Key Design Decisions

1. **Generate job uses `deliver: local`** — no user notification, just saves files
2. **Send job reads from known path** — must use absolute paths (cron environment may have different `~`)
3. **Send job must handle missing file gracefully** — if generate job failed, send job should not error
4. **File naming convention** — use timestamps in filenames so send job can find the latest: `ls -1t ~/path/prefix_*.html | head -1`

## Implementation Notes

- The send job should use `no_agent: false` (LLM-driven) so it can intelligently handle errors and format the output
- If the generate job uses yfinance or other rate-limited APIs, consider adding a `--skip-if-exists` flag to avoid re-fetching
- Both jobs should use absolute paths, never `~` or `os.path.expanduser("~")`

## When to Use

- Cron task takes >30 minutes and user needs results at a fixed time
- Task involves rate-limited APIs (yfinance, web scraping)
- Task involves generating large files that need separate delivery
- User explicitly requests "generate at X, deliver at Y"
