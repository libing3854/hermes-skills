# Kanban & Profile Pitfalls (2026-07-03)

## Profile Name Restrictions

Profile names can only contain `[a-z0-9_-]`. Dots are NOT allowed.

```
❌ mimo-v2.5    → "Invalid profile name 'mimov2.5'"
✅ mimo-v2-5    → works
✅ mimo-v25     → works
```

**Prevention:** Always use `hermes profile create` (validates name), never manually mkdir + write config.

## active_profile Corruption

`~/.hermes/active_profile` stores the current profile name. If it contains an invalid profile name, ALL hermes commands fail:

```
Error: Invalid profile name 'mimov2.5'. Must match [a-z0-9][a-z0-9_-]{0,63}
```

**Symptoms:** Every `hermes` command returns the same error, including `hermes profile list`, `hermes gateway restart`.

**Fix:**
```bash
echo "default" > ~/.hermes/active_profile
```

**Root cause:** Manually creating `~/.hermes/profiles/mimov2.5/` directory (with dots) and somehow setting it as active.

## Gateway Must Be Running for Kanban Dispatch

Creating kanban tasks when gateway is stopped shows:
```
⚠  No gateway is running — the task will sit in 'ready' until you start it.
```

**Fix:** Always start gateway before creating tasks:
```bash
hermes gateway start --profile default 2>&1
```

Gateway stops after profile changes or config edits. Always restart after:
- Profile create/delete
- Config.yaml edits
- Profile switch

## delegate_task Uses Its Own API Config

`delegate_task` uses the `delegation` config section, NOT the current session's model/provider.

**Symptoms:**
- Current session runs fine on mimo-v2.5-pro
- delegate_task fails with "HTTP 402: Insufficient Balance" (from Agnes API, not Xiaomi API)

**Config example:**
```yaml
delegation:
  key_env: AGNES_API_KEY  # ← delegate_task uses THIS, not XIAOMI_API_KEY
```

**Workarounds:**
1. Use `hermes -p <profile> chat -q` instead of delegate_task for model-specific work
2. Configure `delegation.provider` and `delegation.model` in config.yaml
3. Use kanban tasks with `--assignee <profile>` for writing tasks

## Adding New Profiles to Kanban Dispatch

When adding a new profile (e.g. mimo-v25), must also add it to kanban.profiles:

```bash
# Check current
grep "profiles:" ~/.hermes/config.yaml

# Add new profile
sed -i '' 's/profiles: '\''\["lili", "shanli", ...\]'\''/profiles: '\''["lili", "shanli", ..., "mimo-v25"]'\''/' ~/.hermes/config.yaml

# Restart gateway
hermes gateway start --profile default
```
