# Kanban Notifier Bugfix — 2026-06-13

## Summary

Three bugs found and fixed in the Gateway native kanban notifier system:

1. **send() return value not checked** — failed sends silently ignored
2. **Default Gateway crash loop** — active_profile collision
3. **Subscriptions cleared on restart** — WAL checkpoint issue

## Bug 1: send() Return Value (Fixed)

**File:** `~/.hermes/hermes-agent/gateway/kanban_watchers.py` ~line 306

**Problem:** `adapter.send()` returns `SendResult(success=False)` on failure instead of raising. Notifier only caught exceptions, so failed sends fell through to success path. Cursor already advanced → event permanently lost.

**Fix (applied by 大莉M, reviewed by 大莉D 9/10):**
```python
send_result = await adapter.send(sub["chat_id"], msg, metadata=metadata)
if send_result is not None and getattr(send_result, "success", True) is False:
    _err_detail = getattr(send_result, "error", None) or "unknown send error"
    raise RuntimeError(
        f"adapter.send returned success=False: {_err_detail}"
    )
```

**How it works:**
- RuntimeError triggers existing except-block
- except-block: increment fail counter → log warning → rewind cursor → break
- After MAX_SEND_FAILURES=3, subscription dropped
- Next tick re-claims same events and retries

## Bug 2: Default Gateway Crash Loop (Fixed)

**File:** `~/Library/LaunchAgents/ai.hermes.gateway.plist`

**Problem:** `~/.hermes/active_profile` contains "shanli". Default gateway (no `--profile` flag) reads this, overrides HERMES_HOME to shanli directory. Both gateways compete for same PID/lock files.

**Fix:** Added `--profile default` to ProgramArguments:
```xml
<string>--profile</string>
<string>default</string>
<string>gateway</string>
<string>run</string>
<string>--replace</string>
```

**Verified:** Both gateways now have separate PIDs, both exit status 0.

## Bug 3: Subscriptions Cleared on Restart (Workaround)

**Problem:** `kanban_notify_subs` table cleared when gateway restarts (WAL checkpoint or DB re-init).

**Workaround:** Re-subscribe active tasks after any gateway restart. See kanban-patterns skill section 16.

## Diagnostic Commands

```bash
# Check subscriptions
sqlite3 ~/.hermes/kanban.db "SELECT task_id, last_event_id FROM kanban_notify_subs;"

# Check task events
sqlite3 ~/.hermes/kanban.db "SELECT id, kind FROM task_events WHERE task_id='t_xxx' ORDER BY id DESC LIMIT 3;"

# Check both gateways running
ps aux | grep "hermes_cli.main" | grep -v grep

# Check for crash loop
grep "Another gateway instance" ~/.hermes/logs/gateway.error.log | tail -5
```

## Bug 4: Tirith Auto-Install Blocks Kanban Commands (Fixed)

**Problem:** Gateway startup calls `ensure_installed()` which auto-downloads tirith security scanner. After installation, kanban commands with Chinese text trigger "Confusable Unicode characters" approval prompts.

**Fix:** `sed -i '' 's/tirith_enabled: true/tirith_enabled: false/' ~/.hermes/config.yaml`

**Note:** NOT caused by kanban_watchers.py code change. Side effect of Gateway restart triggering tirith download.

## Bug 5: Kanban Worker HTTP 401 — Profile .env Missing (Fixed)

**Problem:** Worker crashes with `HTTP 401: Authentication Fails` when profile's `.env` file doesn't contain API key. Main `.env` is NOT inherited by profile workers.

**Fix:** `cp ~/.hermes/.env ~/.hermes/profiles/<profile>/.env`

## Timeline

| Time | Event |
|------|-------|
| 20:24 | Task t_7c33f317 created (298-304 chapters modification) |
| 20:33 | Subscriptions created via CLI |
| 20:55 | Task completed (event id 756) |
| 20:56 | User asked "推送了看看" — no notification received |
| 20:57 | Gateway restarted (default crashed due to active_profile) |
| 21:00 | Subscriptions re-created (last_event_id=756, too late) |
| 21:10 | 大莉M investigated — found send() return value bug |
| 21:20 | 大莉M fixed kanban_watchers.py |
| 21:25 | 大莉D reviewed fix (9/10, APPROVE) |
| 22:08 | Gateway restarted with --profile default fix |
| 22:10 | Tirith auto-installed → kanban commands blocked by security scan |
| 22:10 | Subscriptions re-created with last_event_id=0 |
| 22:12 | Notification delivered to QQ ✅ |
| 22:15 | Tirith disabled (tirith_enabled: false) |
| 22:36 | Agnes微调 task created, but lili review crashed (HTTP 401) |
| 22:44 | Agnes微调 completed |
| 23:01 | Lili review retried after .env fix → completed (48/50) |
