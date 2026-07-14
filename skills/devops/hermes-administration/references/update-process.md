# Hermes Update Process

## Standard Update

```bash
# 1. Update
hermes update

# 2. Restart gateway
hermes gateway restart

# 3. Verify
hermes doctor
hermes --version
```

## What Happens During Update

1. **Git pull** — Fetches latest commits
2. **Dependency update** — Python packages, Node.js packages
3. **Web UI rebuild** — Vite build for dashboard
4. **Skills sync** — Bundled skills updated
5. **Config migration** — Config format updated if needed
6. **Gateway restart** — Service restarted

## Post-Update Checks

### Quick Check
```bash
hermes doctor  # Should show no critical issues
```

### Detailed Check
```bash
# Version
hermes --version

# Gateway status
hermes gateway status

# API connectivity
hermes doctor | grep -A5 "API Connectivity"
```

## Common Update Issues

### Config Version Outdated
**Symptom**: `hermes doctor` shows "Config version outdated"
**Fix**: Usually auto-migrated. If not, run `hermes setup`

### Skills Not Updated
**Symptom**: Bundled skills missing new features
**Fix**: `hermes update` should sync skills. Check `~/.hermes/skills/`

### Gateway Won't Start
**Symptom**: Gateway crashes after update
**Fix**: 
1. Check logs: `~/.hermes/logs/`
2. Try: `hermes gateway restart`
3. Nuclear: Delete pid file and restart

## Rollback

If update causes issues:
```bash
cd ~/.hermes/hermes-agent
git log --oneline -10  # Find last good commit
git checkout <commit-hash>
hermes gateway restart
```

## User Preferences

- Always run `hermes doctor` after update
- Report version change to user
- Check for new features/skills
