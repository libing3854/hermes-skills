# Skill File Recovery from Session History

> Discovered: 2026-06-20
> Scenario: `daily-morning-report` SKILL.md was deleted, only reference files remained. Cron job failed daily for 4 days before detection.

## Problem

A skill directory exists (`~/.hermes/skills/<category>/<name>/`) but the `SKILL.md` file is missing. Only `references/` files remain. Cron jobs referencing this skill fail with:
```
⚠️ Skill(s) were listed for this job but could not be found and were skipped: <skill-name>
```

## Diagnosis

1. `skill_view(name='...')` returns "Skill not found" but `search_files` finds the directory
2. Check if `SKILL.md` exists: `ls ~/.hermes/skills/<cat>/<name>/SKILL.md`
3. If missing → proceed to recovery

## Recovery Technique: Session History Extraction

Hermes stores full session transcripts as JSON files in `~/.hermes/sessions/`. When `skill_view()` was called in any past session, the complete SKILL.md content is embedded in the tool response within that JSON file.

### Step 1: Find sessions that loaded the skill

```bash
grep -rl '<skill-name>' ~/.hermes/sessions/ | head -10
```

Or use `session_search(query='<skill-name> SKILL.md')`.

### Step 2: Extract the SKILL.md content

Session JSON files contain messages with `tool_calls` and `content` fields. The `skill_view` response includes the full skill content in a JSON structure:

```python
import json
with open('session_XXXXXXXX_XXXXXX_XXXXXXXX.json') as f:
    data = json.load(f)
for msg in data.get('messages', []):
    content = msg.get('content', '')
    if '<skill-name>' in content and 'SKILL.md' in content and len(content) > 2000:
        inner = json.loads(content)
        skill_content = inner.get('content', '')
        if skill_content and len(skill_content) > 500:
            with open('/tmp/recovered-SKILL.md', 'w') as f:
                f.write(skill_content)
            print(f'Recovered {len(skill_content)} chars')
            break
```

### Step 3: Apply patches from reference files

The recovered content may be an older version. Check `references/` files in the skill directory for patch history:

- `references/media-tag-delivery.md` → may document version-to-version changes
- `references/tts-integration-patterns.md` → may have upgrade notes
- Other reference files may contain `v3.5 → v3.6` style changelog entries

Apply patches manually or via script:
```python
content = content.replace(old_string, new_string)
```

### Step 4: Update stale references

- Update task IDs (old cron job ID → new cron job ID)
- Update version numbers in YAML frontmatter
- Verify all reference file paths still exist

### Step 5: Write and verify

```bash
cp /tmp/recovered-SKILL.md ~/.hermes/skills/<cat>/<name>/SKILL.md
```

Then verify with `skill_view(name='<skill-name>')` — should return `success: true`.

## Pitfalls

- **Session files are large** (10MB+). Use `grep -l` to narrow before loading.
- **Multiple versions may exist** across sessions. Prefer the most recent session's version.
- **Patches may not be in session history** — they're often in reference files or applied via `skill_manage patch`. Check both sources.
- **Line endings may differ** between the extracted content and what `str.replace()` expects. Test with `in` operator first.

## Prevention

- After any skill modification, the content is automatically versioned in the skill directory
- Consider periodic backups: `cp -r ~/.hermes/skills/<cat>/<name>/SKILL.md ~/.hermes/backups/`
- The `~/.hermes/state-snapshots/` directory may contain skill backups from before updates
