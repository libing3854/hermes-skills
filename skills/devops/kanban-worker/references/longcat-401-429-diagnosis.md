# LongCat HTTP 401/429 Diagnosis

## The Problem

LongCat's free-tier quota exhaustion returns HTTP 429 (`too_many_requests`) from the provider, but Hermes Agent's API client logs it as **`AuthenticationError [HTTP 401]`** with `incorrect api key`. This makes it look like an auth failure when it's actually a quota issue.

## Diagnosis

**Don't trust the Hermes client error message alone.** Always verify with curl:

```bash
curl -s -w "\\nHTTP_CODE:%{http_code}" \
  https://api.longcat.chat/openai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{"model":"LongCat-2.0-Preview","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
```

### Expected response when key + quota are OK
```json
HTTP_CODE:200
```
Response includes `choices[0].message.content` with the model's reply.

### Expected response when quota is exhausted
```json
{"error":{"code":"too_many_requests","message":"AppId:**xxxx 达到使用量上限","type":"rate_limit_error"}}
HTTP_CODE:429
```

### Expected response when key is actually invalid
```json
HTTP_CODE:401
```

## Fix

If curl shows **HTTP 429** (quota exhaustion):
1. The key is valid — **do NOT regenerate it**
2. Go to https://longcat.chat/platform to check remaining quota
3. Submit feedback to request quota refresh (up to 120M tokens/day)
4. Or wait for daily reset at midnight Beijing time
5. The `api_key: <plaintext>` vs `key_env: LONGCAT_API_KEY` config choice does NOT affect this — it's purely a quota issue

If curl shows **HTTP 401** (key invalid):
1. Regenerate the key at https://longcat.chat/platform
2. Update `~/.hermes/.env` or `config.yaml` with the new key
3. Restart the gateway so the new key is loaded

## Config Notes

LongCat under `providers:` (named providers) can use `${LONGCAT_API_KEY}` syntax. If that doesn't resolve in spawned contexts (kanban workers), fall back to plaintext `api_key: <key>` in config.yaml. Both work when the key has quota.

## ⚠️ `.env` Key Corruption via `read_file` Truncation

**Critical pitfall:** The `read_file` tool truncates sensitive values (API keys) in its output display, replacing the middle of the key with `...`. If you copy that truncated value and use it in a `write_file` or `patch` operation, you corrupt the key — the file now literally contains `ak_2JI...q0z` instead of the full key.

### How it happens

```
read_file(.env) shows:  LONGCAT_API_KEY=ak_2JI...2q0z      ← truncated display
                   ↓
You copy & write:       LONGCAT_API_KEY=ak_2JI...2q0z      ← writes the literal "..."
                   ↓
File now contains:      ak_2JI...2q0z                      ← BROKEN key
                   ↓
Curl with truncated key: HTTP 401                           ← fails
Curl with original key:  HTTP 200                           ← works
```

### Prevention

1. **Never copy API keys from `read_file` output.** Always get the full key from the provider's dashboard.
2. **If you must extract a key from `.env`**, use `terminal()` with `grep LONGCAT_API_KEY ~/.hermes/.env | cut -d= -f2` — the terminal tool returns the full value.
3. **After any `.env` edit, verify with curl** before assuming the key works.
4. **Signature of corruption:** `hermes kanban log` shows 401 errors, but `curl` with the same key from terminal succeeds → the `.env` file has a truncated key.

### Recovery

```bash
# Fix a truncated key — replace with the real full key
python3 -c "
with open('/Users/libing/.hermes/.env', 'r') as f:
    content = f.read()
# Replace the truncated version
content = content.replace('ak_2JI...2q0z', 'ak_2JI8lE91l6Za45o0y89L81WL02q0z')
with open('/Users/libing/.hermes/.env', 'w') as f:
    f.write(content)
"
```

## 🔴 Profile Isolation: `***` Placeholder Keys in `profiles/<name>/.env`

**Critical:** When a profile is created (e.g. `hermes curator create-profile`), its `.env` file is pre-populated with **literal `***`** as placeholder values — not redacted display, but actual three-asterisk strings stored in the file.

### How it causes 401

```
kanban dispatcher spawns worker under profile (e.g. shanli)
  ↓
Worker loads ~/.hermes/profiles/shanli/.env
  → LONGCAT_API_KEY=***  (literal asterisks!)
  ↓
Worker reads ~/.hermes/profiles/shanli/config.yaml
  → key_env: LONGCAT_API_KEY  (reads from env)
  ↓
Sends "***" as Bearer token to LongCat
  → HTTP 401 incorrect api key
```

Meanwhile, the main `~/.hermes/.env` has the real key, and `curl` with that real key works fine.

### Diagnosis

1. **Check log evidence:** `hermes kanban log <task_id> | tail -30` — look for `Loaded environment variables from /Users/libing/.hermes/profiles/<name>/.env`
2. **Check profile's `.env`:** `cat ~/.hermes/profiles/<name>/.env` — look for `***` values
3. **Check profile's `config.yaml`:** `cat ~/.hermes/profiles/<name>/config.yaml` — check if longcat uses `key_env:` or plain `api_key:`

### Fix

**Option A (推荐):** Change profile config.yaml from `key_env` to plain `api_key`:

```yaml
# ~/.hermes/profiles/shanli/config.yaml
  longcat:
    name: LongCat
    base_url: https://api.longcat.chat/openai
    api_key: ak_2JI8lE91l6Za45o0y89L81WL02q0z  # plaintext
    # key_env: LONGCAT_API_KEY  ← remove this
    api_mode: chat_completions
    default_model: LongCat-2.0-Preview
```

**Option B:** Replace `***` in profile's `.env` with real keys (only if full key values are available).

Then re-dispatch:
```bash
hermes kanban dispatch
```

### Why main config worked but profile didn't

The main `~/.hermes/config.yaml` uses `api_key: <plaintext>` for longcat (hardcoded in the file). The profile `~/.hermes/profiles/shanli/config.yaml` uses `key_env: LONGCAT_API_KEY` (reads from environment). Since the profile's `.env` has `***`, the env variable resolves to `***` — hence the 401. The two configs are completely independent; fixing only the main config has no effect on kanban workers dispatched under the profile.
