# Two-Gateway Architecture — Lessons Learned (2026-06-15)

## ⚠️ Important: Dual Gateway Was a Mistake

The two-gateway setup (default + shanli) was originally created to run kanban dispatch in a separate process. However, it caused critical problems:

1. **Telegram Bot Token collision** — Both gateways polled the same token, causing random message distribution
2. **Model switching** — Messages randomly processed by different models (mimo-v2.5 vs LongCat)
3. **Cron job loss** — Jobs lost during Hermes Agent update
4. **Resource waste** — Shanli gateway consumed 17h CPU time vs default's 9h

**The correct architecture is single gateway + multi-profile kanban dispatch.**

## Correct Architecture: Single Gateway

```
┌─────────────────────────────────────────────┐
│           Default Gateway (唯一)             │
│  Profile: default                           │
│  Model: mimo-v2.5                           │
│                                             │
│  Platforms: Telegram + QQ + Discord          │
│  Kanban profiles: ["lili", "shanli"]        │
│                                             │
│  Worker: lili (deepseek-v4-flash)           │
│  Worker: shanli (LongCat-2.0-Preview)       │
└─────────────────────────────────────────────┘
```

**Key design principle:** One Gateway manages all messaging platforms. Profile routing happens via kanban dispatch, not separate gateway processes.

## Previous Dual Gateway Setup (DEPRECATED)

| Gateway | Profile | HERMES_HOME | PID File | Purpose |
|---------|---------|-------------|----------|---------|
| ai.hermes.gateway | default | ~/.hermes | ~/.hermes/gateway.pid | Cron scheduler, kanban notifier, platform connections |
| ai.hermes.gateway-shanli | shanli | ~/.hermes/profiles/shanli | ~/.hermes/profiles/shanli/gateway.pid | Kanban dispatch, worker spawning |

## LaunchAgent Plist Locations

```
~/Library/LaunchAgents/ai.hermes.gateway.plist          (default)
~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist   (shanli)
```

## Critical: --profile flag

The default plist MUST include `--profile default` in ProgramArguments. Without it, `_apply_profile_override()` in main.py reads `~/.hermes/active_profile` and overrides HERMES_HOME to the shanli directory, causing PID/lock file collision.

**Correct default plist ProgramArguments:**
```xml
<string>/Users/libing/.hermes/hermes-agent/venv/bin/python</string>
<string>-m</string>
<string>hermes_cli.main</string>
<string>--profile</string>
<string>default</string>
<string>gateway</string>
<string>run</string>
<string>--replace</string>
```

**Shanli plist already has `--profile shanli` — no change needed.**

## How the Profile Override Works

In `hermes_cli/main.py:_apply_profile_override()`:

1. Step 1: Check if `--profile` is already in argv → if yes, skip
2. Step 1.5: Check if current HERMES_HOME is already a profile dir (parent.name == "profiles") → if yes, skip
3. Step 2: Read `~/.hermes/active_profile` → if profile name ≠ "default", override HERMES_HOME
4. Step 3: Resolve profile env (set HERMES_HOME to profile dir)

**Without `--profile default`:** Step 1 is skipped, Step 1.5 passes (HERMES_HOME=/Users/libing/.hermes, parent=libing ≠ profiles), Step 2 reads active_profile="shanli" → overrides to shanli directory → collision.

**With `--profile default`:** Step 1 detects --profile flag → skips Steps 2-3 → HERMES_HOME stays at /Users/libing/.hermes → no collision.

## Telegram Polling Conflict (Shared Bot Token)

**Problem:** When both gateways share the same Telegram Bot Token, they compete for `getUpdates`:

```
Gateway A (default) ──┐
                      ├─→ Telegram API ──→ only one wins per cycle
Gateway B (shanli) ───┘
```

**Symptoms:**
- `Telegram polling conflict (1/5)` in gateway logs every ~25s
- Messages randomly processed by different models (auto vs LongCat)
- Kanban notifications appear on unexpected platforms
- Response quality inconsistent

**Telegram Bot API behavior:**
- `getUpdates` is exclusive — only one client can poll at a time
- If another client polls while one is active, the first gets a `Conflict` error
- The conflicting client must wait (typically 20-30s) before retrying
- No guaranteed ordering — both clients compete randomly

**Fix options:**
1. Stop the extra gateway: `kill <PID>`
2. Use different bot tokens for each gateway
3. Disable Telegram on one gateway (remove telegram config from that profile)

**Verification:**
```bash
# Check running gateways
ps aux | grep "hermes_cli.main" | grep -v grep

# Check for conflicts
grep "Telegram polling conflict" ~/.hermes/logs/gateway.log | tail -5
```

## Kanban Notifier Location

The kanban notifier (`_kanban_notifier_watcher`) runs ONLY in the default gateway. It requires:
- `kanban.dispatch_in_gateway: true` in config
- `kanban_notify_subs` table with subscription records
- Default gateway to be the dispatch-owning gateway

If the default gateway crashes (e.g., active_profile collision), the notifier never starts and no notifications fire.

## Service Management

```bash
# Check status of both
launchctl list | grep hermes

# Restart default
launchctl bootout gui/$(id -u)/ai.hermes.gateway
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist

# Restart shanli
hermes gateway stop
hermes gateway start

# Verify both running
ps aux | grep "hermes_cli.main" | grep -v grep
```

## Stop Shanli Gateway (2026-06-15 verified)

**⚠️ KeepAlive trap:** Both plists have `<key>KeepAlive</key><true/>`. If you `kill` the process first, launchd will IMMEDIATELY restart it. Must use `launchctl bootout` first.

**Correct order:**
```bash
# Step 1: bootout the service (stops process + disables KeepAlive)
launchctl bootout gui/$(id -u)/ai.hermes.gateway-shanli.plist

# Step 2: confirm process is dead
ps aux | grep "profile shanli" | grep -v grep
# Should return nothing

# Step 3: if still alive (rare), force kill
kill <PID>

# Step 4: disable plist to prevent restart on reboot
mv ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist.disabled
```

**Rollback:**
```bash
mv ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist.disabled ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist
```

## Kanban Worker Spawn — Single Gateway Works

**Verified (2026-06-15):** When default gateway dispatches a task to `--assignee shanli`, the worker spawn mechanism:
1. Reads `kanban.profiles: ["lili", "shanli"]` from default gateway config
2. Spawns worker with `HERMES_HOME = ~/.hermes/profiles/shanli/` (profile directory)
3. Worker reads shanli profile's `.env` and `config.yaml`
4. Worker uses shanli's model (LongCat-2.0-Preview)

**Conclusion:** Stopping shanli gateway does NOT break kanban dispatch. The default gateway handles all dispatch, and workers automatically use the correct profile environment.

## Cron Job Recovery — Pitfalls (2026-06-15 verified)

**Problem:** Restoring jobs from state snapshot may fail because:
1. **Missing scripts:** `nv_ping.py`, `nv_daily_eval.py`, `gen_v5.py` may not exist at expected paths
2. **Schema differences:** Snapshot fields vs current version fields differ (profile, no_agent, context_from, enabled_toolsets)
3. **Cron scheduler ignores profile field:** Jobs with `profile: "shanli"` still run in default gateway's environment

**Before restoring, verify:**
```bash
# Check script existence
ls ~/.hermes/scripts/nv_ping.py 2>/dev/null || echo "MISSING"
ls ~/.hermes/scripts/nv_daily_eval.py 2>/dev/null || echo "MISSING"
ls ~/.hermes/skills/productivity/financial-dashboard/scripts/gen_v5.py 2>/dev/null || echo "MISSING"
```

**Schema fix when restoring:**
```python
# Add missing fields for current version compatibility
job['profile'] = job.get('profile', None)
job['no_agent'] = job.get('no_agent', False)
job['context_from'] = job.get('context_from', None)
job['enabled_toolsets'] = job.get('enabled_toolsets', None)
job['origin'] = job.get('origin', None)
```

**After restoring, verify kanban.db integrity:**
```bash
sqlite3 ~/.hermes/kanban.db "PRAGMA integrity_check;"
# Should return "ok"
```

## Cron Job Loss During Updates

**Problem:** Hermes Agent updates can reset `~/.hermes/cron/jobs.json`, losing all scheduled cron jobs.

**Evidence (2026-06-12):**
- State snapshot (20260611-082251-pre-update) had 8 jobs
- After update, only 1 job remained (喝水提醒)
- Lost jobs: 每日早报, 闪莉归档日报, 金融看板, Ping数据采集, AI周报, GitHub Trending周报, 金融看板发送

**Recovery from state snapshot:**
```bash
# Find the pre-update snapshot
ls -lt ~/.hermes/state-snapshots/

# Backup current jobs.json
cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak.$(date +%Y%m%d)

# Read the snapshot to identify lost jobs
cat ~/.hermes/state-snapshots/YYYYMMDD-HHMMSS-pre-update/cron/jobs.json | python3 -m json.tool

# Manually recreate jobs using hermes cron create or MCP cronjob tool
# Key fields to preserve: name, schedule, prompt, script, deliver, profile, skills
```

**Prevention:**
- Check jobs.json after any Hermes Agent update
- Keep state-snapshots directory (don't auto-clean)
- Consider backing up jobs.json before manual updates
