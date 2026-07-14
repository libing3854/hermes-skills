# gemini-web2api Setup Guide

## What It Is
Reverse-engineered proxy that converts Gemini web interface to OpenAI-compatible API.
User's Gemini Advanced membership ($19.99/mo) → local API server → usable by Hermes kanban workers.

## Key Advantage
- Gemini Advanced membership does NOT include API access (separate billing)
- gemini-web2api bridges this gap — uses the web session, not the API
- Free (no additional cost beyond existing membership)
- No rate limits beyond what Gemini web enforces

## Setup (Verified 2026-06-23)

```bash
# Clone
cd /tmp && git clone --depth 1 https://github.com/Sophomoresty/gemini-web2api.git
cd gemini-web2api

# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt  # Only needs httpx

# Config (SECURITY: bind to localhost + set api_key)
cat > config.json << 'EOF'
{
  "port": 8081,
  "host": "127.0.0.1",
  "default_model": "gemini-3.5-flash",
  "api_keys": ["gemini-local-key"],
  "log_requests": false,
  "request_timeout_sec": 120
}
EOF

# Start (background)
source venv/bin/activate && python3 gemini_web2api.py
```

## ⚠️ Security Hardening (Critical)

**This is a reverse-engineered proxy, not an official API.** Treat it accordingly.

### Mandatory Config Changes
1. **`host: "127.0.0.1"`** — Default is `0.0.0.0` (exposes to network). Always bind to localhost.
2. **`api_keys: ["your-key"]`** — Default is empty (no auth). Set a key to prevent unauthorized access.
3. **Don't use Google account cookies** — Cookie-based Pro routing gives the script your full Google login session. High risk.

### Risk Assessment
| Risk | Severity | Mitigation |
|------|----------|------------|
| Google bans the proxy | Medium | Use dedicated Google account, not primary |
| Auth bypass vulnerability (issue #37) | High | Bind to 127.0.0.1, set api_keys |
| Cookie theft if 0.0.0.0 exposed | Critical | Always use 127.0.0.1 |
| No official SLA | Low | Keep DeepSeek as backup provider |
| Pro model falls back to Flash (no cookie) | Expected | Accept Flash quality, or use cookie (risky) |

### Verified Security State (2026-06-23)
- ✅ Bound to 127.0.0.1 (verified via `lsof -i :8081`)
- ✅ API key required (no key = `{"error": {"message": "invalid api key"}}`)
- ✅ Works with key
- ⚠️ Repo created 2026-05-28, very new
- ⚠️ Has open security audit issue (#37) mentioning SSRF, auth bypass

## Available Models
| Model | Description |
|-------|-------------|
| gemini-3.5-flash | Fast general-purpose (recommended for writing) |
| gemini-3.5-flash-thinking | Deep thinking, longer output |
| gemini-3.1-pro | Pro model (needs cookie) |
| gemini-auto | Auto model selection |

## Hermes Integration

### shanliG Profile (Already Configured)
```yaml
# ~/.hermes/profiles/shanliG/config.yaml
model:
  provider: gemini-local
  default: gemini-3.5-flash
providers:
  gemini-local:
    name: Gemini Local
    api_key: none
    api_mode: chat_completions
    base_url: http://localhost:8081/v1
    context_length: 1048576
    default_model: gemini-3.5-flash
```

### Custom Provider in main config.yaml
```yaml
custom_providers:
- base_url: http://localhost:8081/v1
  key_env: ""
  model: gemini-3.5-flash
  name: Gemini Local
```

## Usage for Novel Writing
```bash
# Assign writing tasks to shanliG instead of shanli
hermes kanban create "写作任务" --assignee shanliG ...

# Or use in delegate_task
delegate_task(goal="...", model="custom:Gemini Local")
```

## Caveats
- Server must be running (not auto-started) — add to login items or launchd for persistence
- **Reverse-engineered, not official** — Google can break it anytime
- **Pro model is fake without cookies** — Anonymous access routes to Flash, not Pro
- Use a dedicated Google account (not primary) to reduce ban risk
- Anonymous access works for basic text generation (no cookie needed)
- For advanced features (Deep Research, Gems), cookies required — fragile and risky
- Restart server if responses become slow/errors increase
- **Not a replacement for official API** — use as fallback, not primary
- **Gemini only expands, never trims** — asking Gemini to "精简到5000字" is ineffective; it removes almost nothing. Use Python regex to strip banned/high-frequency words instead.
- **Server dies on Mac sleep/reboot** — must restart manually: `cd /tmp/gemini-web2api && source venv/bin/activate && python3 gemini_web2api.py &`

### ❌ Does NOT Support Function Calling (Critical)

**Problem:** gemini-web2api does not support OpenAI function/tool calling. Kanban workers REQUIRE tools (kanban_show, kanban_complete, file operations, etc.). When the worker sends a tool-using prompt, Gemini returns empty content → worker crashes with "Model returned empty after tool calls".

**This means:** You CANNOT use gemini-web2api as the provider for kanban workers. The shanliG profile will crash every time a kanban worker tries to use tools.

**Workaround — Hybrid workflow:**
1. **Writing:** Python script calls Gemini API directly (no tools needed)
2. **Review:** kanban worker with lili (DeepSeek) or shanli (LongCat)
3. **Fix:** Python script calls Gemini API again

**Script-based writing approach:**
```python
import urllib.request, json
data = json.dumps({
    "model": "gemini-3.5-flash",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 8000
}).encode()
req = urllib.request.Request(
    "http://localhost:8081/v1/chat/completions",
    data=data,
    headers={"Content-Type": "application/json"}
)
resp = urllib.request.urlopen(req, timeout=180)
content = json.loads(resp.read())["choices"][0]["message"]["content"]
```

**Why this works:** Direct API calls don't need tools. The script handles file I/O itself.

**Batch size limit:** Max 2 chapters per Gemini call (output tends to be 7000-10000 chars instead of target 4500-5500). Larger batches hit output limits or produce very low quality.

## Test Command
```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3.5-flash","messages":[{"role":"user","content":"hello"}]}'
```

## Pitfalls

### Empty Responses with Long Task Bodies (2026-06-23 verified)

**Problem:** Gemini returns empty content (`"content": null` or empty string) when the kanban task body is very long (detailed tables, multiple sections, 500+ words).

**Symptom:** Worker crashes with "Model returned empty after tool calls" or "Empty response from model — retrying (3/3)".

**Root cause:** Gemini web API has input length limits that differ from the official API. Very long prompts with complex formatting may exceed internal limits.

**Fix:** Shorten the task body significantly. Keep only essential instructions:
```
❌ LONG: 500+ word body with tables, multiple sections, detailed requirements
✅ SHORT: 100-200 word body with core instructions only
```

**Example shortened body:**
```
修复第七卷第336/337/339/340/341章字数不足，扩充至4500-5500字。
目录：/path/to/chapters/
要求：不改剧情，Python统计汉字数，禁用词0次，高频词≤3次/章。
覆盖原文件。
```

**Workaround:** If the task requires detailed context, include it in files the worker reads rather than in the task body itself.

### API Key Mismatch Between Profile and Server

**Problem:** shanliG profile has `api_key: none` but gemini-web2api config has `api_keys: ["gemini-local-key"]`. Worker gets 401.

**Fix options:**
1. Set gemini-web2api to anonymous mode: `"api_keys": []` (matches `api_key: none`)
2. Or set shanliG profile `api_key` to match the server key

**Recommended:** Use anonymous mode (`api_keys: []`) for simplicity.

### Config Change Requires Server Restart

**Problem:** Changing `config.json` doesn't take effect until the gemini-web2api server is restarted.

**Fix:** Kill and restart after config changes:
```bash
kill $(lsof -t -i :8081) 2>/dev/null; sleep 1
cd /tmp/gemini-web2api && source venv/bin/activate && python3 gemini_web2api.py &
```

## Alternatives (If gemini-web2api Breaks)
1. Google AI Studio free tier (separate API key from aistudio.google.com)
   - Gemini 2.5 Flash: 1000 RPM, 1M tokens/day
   - Needs new key (current GOOGLE_API_KEY may be invalid)
2. DeepSeek V4 Flash ($0.28/M output) — already configured
3. Groq free tier (uncomment GROQ_API_KEY in .env)
