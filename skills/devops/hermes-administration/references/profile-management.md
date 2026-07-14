# Hermes Profile Management

## Profile Locations

- **Default profile**: `~/.hermes/SOUL.md`
- **Other profiles**: `~/.hermes/profiles/<name>/SOUL.md`
- **Config**: `~/.hermes/config.yaml`

## Active Profiles (Current Setup)

| Profile | Model | Purpose | Status |
|---------|-------|---------|--------|
| default | mimo-v2.5 | Main (Lilith) | Active |
| lili | DeepSeek V4 Flash | Review/audit | Active |
| shanli | LongCat 2.0 Preview | Writing | Quota exhausted |
| shanliG | Gemini 3.5 Flash | Writing backup | Active |
| dalim | mimo-v2.5-pro | Deep review | Active |
| dalid | deepseek-v4-pro | Deep review | Active |

## SOUL.md Structure

Each profile's SOUL.md defines:
- **Identity**: Name, role, model
- **Style**: Communication style, tone
- **Principles**: Rules, workflows
- **Boundaries**: What to avoid

## Checking for Redundancy

When asked to check profiles:

1. **Read each SOUL.md**
   ```bash
   for f in ~/.hermes/profiles/*/SOUL.md; do
     echo "=== $f ==="
     cat "$f"
   done
   ```

2. **Compare with skills**
   - Check if profile defines functionality already in skills
   - Look for overlap with writing-guardrails, kanban-patterns, etc.

3. **Report findings**
   - List each profile's purpose
   - Identify any redundancy
   - Suggest consolidation if needed

## Common Issues

### Profile Not Found
**Symptom**: `hermes doctor` shows "profile not found"
**Fix**: Check `~/.hermes/profiles/` directory exists

### SOUL.md Missing
**Symptom**: Profile loads with default persona
**Fix**: Create SOUL.md in profile directory

### Profile Gateway Conflict
**Symptom**: Gateway crashes with lock errors
**Cause**: active_profile contains "shanli" causing default gateway override
**Fix**: Ensure plist uses `--profile default`

## User Preferences

- Profile name = character name (not model name)
- kanban tasks use profile names (lili, shanli, etc.)
- Do not use model names (DeepSeek, MiMo, etc.) in task assignments
