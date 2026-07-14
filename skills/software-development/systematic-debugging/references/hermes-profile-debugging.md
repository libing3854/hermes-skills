# Hermes Agent Multi-Profile & Gateway Debugging

## Overview

Hermes Agent supports multiple profiles (default, shanli, dali, xiaoli), each with its own `.env` and `config.yaml`. When things break, the active profile determines which config the gateway and workers actually load — and it's often **not** the one you expect.

## The Active Profile Trap

### How it works

```bash
~/.hermes/active_profile  # ← THIS file controls everything
```

When gateway starts:
1. Reads `active_profile` → determines which profile to load
2. Loads `~/.hermes/profiles/<active_profile>/.env` — **NOT** `~/.hermes/.env`
3. Loads `~/.hermes/profiles/<active_profile>/config.yaml`
4. The main `~/.hermes/.env` is **only read if no active profile is set or if the profile's .env is missing**

### Symptoms of wrong active profile

| Symptom | Likely Cause |
|---------|--------------|
| "No messaging platforms enabled" | Profile's .env has no TELEGRAM/QQ/DISCORD/WEIXIN keys |
| LongCat 401 even though key is correct | Profile's config uses `key_env` but profile's `.env` has `***` placeholder |
| kanban worker fails with protocol violation | Worker can't load model → silent exit |

### Debugging checklist

```bash
# 1. Check which profile is active
cat ~/.hermes/active_profile

# 2. Check what keys the active profile has
cat ~/.hermes/profiles/$(cat ~/.hermes/active_profile)/.env

# 3. Compare with main .env
grep TELEGRAM_BOT_TOKEN ~/.hermes/.env
grep TELEGRAM_BOT_TOKEN ~/.hermes/profiles/$(cat ~/.hermes/active_profile)/.env

# 4. Check profile config for key_env vs api_key
grep -A3 "longcat:" ~/.hermes/profiles/$(cat ~/.hermes/active_profile)/config.yaml
# key_env: LONGCAT_API_KEY → reads from profile's .env
# api_key: xxx → plaintext, ignores .env
```

### Fixing

```bash
# Switch active profile
echo "default" > ~/.hermes/active_profile

# Or fix the profile's .env with real keys
# Or change config.yaml from key_env to plaintext api_key
```

## Gateway Platform Connectivity

### "No messaging platforms enabled" loop

The gateway starts → finds zero enabled platforms → SIGTERMs itself → launchd restarts → loop.

**Root causes (in order of likelihood):**

1. **Wrong active profile** (see above) — the loaded .env has no platform keys
2. **Corrupted .env** — literal `\n` characters, missing line breaks, truncated keys
3. **GATEWAY_ALLOW_ALL_USERS not set** — gateway denies all users, platforms refuse to enable
4. **Multiple gateway instances** — PID file race between launchd and manual instances

### Launchd management

```bash
# View running gateway
launchctl list | grep hermes

# Stop completely (bootout, not just kill)
launchctl bootout gui/501/ai.hermes.gateway

# Remove stale PID/lock files
rm -f ~/.hermes/gateway.lock /tmp/hermes-gateway*.lock
rm -f ~/.hermes/profiles/*/gateway.pid ~/.hermes/profiles/*/gateway_state.json

# Clean reinstall
hermes gateway stop
hermes gateway install --profile default
hermes gateway start --profile default
```

### Launchd plist location

```bash
# Default profile
~/Library/LaunchAgents/ai.hermes.gateway.plist

# Named profile
~/Library/LaunchAgents/ai.hermes.gateway-<profile>.plist
```

KeepAlive is configured as `SuccessfulExit → false` — meaning gateway restarts immediately on any exit. This is normally fine but creates infinite loops when the gateway keeps failing.

## Kanban Worker Model Routing

### Why the model you specify ≠ the model that runs

```yaml
# delegate_task model parameter does NOT override subagent model!
# Subagent always inherits the current session's model.
```

**Delegate_task model parameter is a PIN, not an OVERRIDE.** It pins the current parent model, it does not switch to a different model/provider.

### How kanban workers pick their model

1. Worker starts with the profile's configured model
2. `shanli` profile → reads `model.default` and `model.provider` from **shanli's config.yaml**
3. If the profile's LongCat key is `***` (placeholder), worker gets 401 and crashes

### Fixing kanban worker model issues

```bash
# Option A: Fix the profile's .env with real keys
# Option B: Change profile's config.yaml from key_env to plaintext api_key
# Option C: Switch active_profile to default (if that profile has working keys)
```

## Quick Diagnostic Commands

```bash
# Active profile
cat ~/.hermes/active_profile

# Profile env
cat ~/.hermes/profiles/$(cat ~/.hermes/active_profile)/.env

# Gateway logs
tail -30 ~/.hermes/logs/gateway.log
tail -30 ~/.hermes/logs/gateway.error.log

# Gateway status
hermes gateway status
launchctl list | grep hermes

# Profile config
cat ~/.hermes/profiles/$(cat ~/.hermes/active_profile)/config.yaml | grep -A5 longcat

# Kanban task log
hermes kanban log <task_id>
