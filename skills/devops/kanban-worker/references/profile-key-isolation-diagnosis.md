# Profile API Key Isolation — Diagnosis & Fix

> When a kanban worker returns HTTP 401 but `curl` with the same key succeeds, the root cause is often **profile-level key isolation**: the worker loaded a profile `.env` containing literal `***` placeholders, or the profile's `config.yaml` uses `key_env` that resolves to a stale/incomplete environment variable.

## Symptoms

- `hermes kanban log <task_id>` shows repeated `HTTP 401: incorrect api key`
- Model list query (`curl /v1/models`) or direct API call succeeds with the expected key
- Worker exits ~60s after start with `protocol_violation` (rc=0, no `kanban_complete`)
- The crash loop repeats every ~60s as the dispatcher retries

## Diagnosis Commands

```bash
# 1. Check which .env the worker loaded
hermes kanban log <task_id> | grep "Loaded environment variables from"
# → e.g. "Loaded environment variables from /Users/libing/.hermes/profiles/shanli/.env"
#      This confirms profile isolation is in effect — NOT the root ~/.hermes/.env

# 2. Check the profile's .env for placeholder values
cat ~/.hermes/profiles/<profile_name>/.env
# If you see:
#   LONGCAT_API_KEY=***
#   DEEPSEEK_API_KEY=***
# That's the problem — literal three-asterisk placeholders.

# 3. Check the profile's config.yaml to see how it reads the key
cat ~/.hermes/profiles/<profile_name>/config.yaml | grep -A3 "longcat:"
# If you see key_env: LONGCAT_API_KEY, it reads from env → gets "***"
# If you see api_key: sk-xxxxx, it uses the hardcoded value directly

# 4. Verify the real key works independently
curl -s https://api.longcat.chat/openai/v1/models \
  -H "Authorization: Bearer <real_key>" | head -3
# Should return HTTP 200 with model list
```

## Why This Happens

When `hermes profile create <name>` generates a new profile, it populates the profile's `.env` with **literal `***` placeholder values** for all standard API keys:

```bash
# ~/.hermes/profiles/<name>/.env — auto-generated
DEEPSEEK_API_KEY=***
LONGCAT_API_KEY=***
NVIDIA_API_KEY=***
OPENROUTER_API_KEY=***
GOOGLE_API_KEY=***
```

These need to be **manually replaced** with real key values. The kanban worker loads ONLY the profile's `.env` (not the root `~/.hermes/.env`), so `key_env: LONGCAT_API_KEY` in the profile's `config.yaml` resolves to `***`.

## Fix Options

### Option A (Recommended for kanban workers)

Change the profile's `config.yaml` to use plaintext `api_key` instead of `key_env`. This bypasses the broken `.env` entirely:

```yaml
# ~/.hermes/profiles/<profile_name>/config.yaml
providers:
  longcat:
    name: LongCat
    base_url: https://api.longcat.chat/openai
    api_key: ak_2JI8lE91l6Za45o0y89L81WL02q0z  # ← plaintext, NOT key_env
    api_mode: chat_completions
    default_model: LongCat-2.0-Preview
```

Pros: Simple, one-line change, no `.env` editing needed.
Cons: Key stored in plaintext in `config.yaml` (acceptable for local-only profiles).

### Option B

Replace the `***` placeholders in the profile's `.env` with real keys. Copy values from the root `~/.hermes/.env` using `terminal()` with `grep` + `cut` (never use `read_file` — it truncates API keys):

```bash
grep LONGCAT_API_KEY ~/.hermes/.env
# Copy the full value, then:
echo "LONGCAT_API_KEY=ak_2JI8lE91l6Za45o0y89L81WL02q0z" >> ~/.hermes/profiles/<name>/.env
```

### After Fix

Re-dispatch to retry with the new config:

```bash
hermes kanban dispatch
# Verify: hermes kanban list → task should show running
```

## `.env` Corruption — Literal `\n` from Patch

**Symptom:** Python `repr()` shows `\\n` (backslash-n as two characters) inside the `.env` file instead of a real line break.

**Detection:**
```bash
python3 -c "
with open('/Users/libing/.hermes/.env', 'rb') as f:
    data = f.read()
# Look for literal backslash-n sequence
idx = data.find(b'\\\\n')
if idx >= 0:
    context = data[max(0,idx-20):idx+30]
    print('Found literal \\\\n at byte', idx)
    print('Context:', context)
"
```

**Fix:** Use Python to replace the literal `\n` with a real newline:
```python
content = content.replace('\\n', '\n')
# Then write back
```

**Prevention:** Never use `read_file` output (which truncates/escapes values) as input to `patch` or `write_file` for credential files. Always retrieve keys via `terminal()` with shell commands (`grep`, `cut`, `cat` with `-v`).
