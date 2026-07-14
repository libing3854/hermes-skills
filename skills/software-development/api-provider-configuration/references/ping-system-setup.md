# Ping System Integration for Custom Providers

> How to add a custom API provider to the NV Ping system so it's available for 闪莉 (Shanli) model selection in kanban tasks.

## When to Use This

- You've added a new provider to Hermes config.yaml (via `providers:`), and you also want it available for the kanban worker's model selection pool
- You want 闪莉 (the kanban worker) to be able to pick this model based on ping speed

## The Ping System

The NV Ping system (`~/.hermes/scripts/nv_ping.py`) periodically (every 30 minutes) tests API model speeds across multiple providers, saves results to `~/.hermes/data/NVping/tmp/`, and ranks models by latency into categories:

| Category | Purpose | Model Size |
|----------|---------|------------|
| `mimi` | Lightweight tasks | <15B params |
| `light` | Daily tasks | 15B-119B params |
| `deep` | Heavy analysis | 70B+ params |
| `vision` | Multimodal | Vision-capable |

Model configuration is in `groups.json` at `~/.hermes/data/NVping/tmp/groups.json`.

The ranking system (`ranking.json`) produces `top_by_category` — the fastest N models per category. Models from each category are also periodically pinged in **A/B rotation groups** (Group A one cycle, Group B the next).

### Provider Priority in Model Selection

When 闪莉 selects a model from the ping ranking, she uses **provider priority** for tie-breaking when models have similar speeds. The priority is embedded in `nv_ping.py`'s `get_fastest()` function:

| Priority | Provider | Code Name |
|:--------:|----------|:---------:|
| 1 (highest) | NVIDIA NIM | `nv` |
| 2 | LongCat | `longcat` |
| 3 | Google Gemini | `google` |
| 4 | OpenRouter | `openrouter` |

The `get_fastest()` function sorts by `(provider_priority, latency_ms)` — meaning a slightly slower NVIDIA model will be preferred over a slightly faster OpenRouter model. This is the key difference from a pure-speed sort.

## Step-by-Step Setup

### 1. Add the Provider to `nv_ping.py`

Edit `PROVIDERS` dict in `~/.hermes/scripts/nv_ping.py`:

```python
PROVIDERS = {
    # ... existing providers ...
    "longcat": {
        "url": "https://api.longcat.chat/openai/v1/chat/completions",
        "keychain": "longcat_api_key",    # ← macOS Keychain service name
        "expire": None,
        "format": "openai",                # "openai" or "gemini"
    },
}
```

> ⚠️ The `url` for LongCat uses the full path `/openai/v1/chat/completions` — NOT just `/openai`. The Hermes config uses `api.longcat.chat/openai` (without the `/v1/chat/completions` suffix since Hermes appends it), but the ping script needs the full endpoint.

### 2. Write API Key to macOS Keychain

The ping script reads keys from Keychain, not from `.env`:

```bash
# Read from .env and write to Keychain
KEY=$(grep "PROVIDER_API_KEY" ~/.hermes/.env | cut -d'=' -f2 | tr -d ' \t\n')
security add-generic-password -s "longcat_api_key" -a "$USER" -w "$KEY" -U
```

The `-s` value must match the `keychain` field in the PROVIDERS dict.

### 3. Add Model to `groups.json`

Two places to update in `~/.hermes/data/NVping/tmp/groups.json`:

**a) Categories (for model selection):**

```json
"deep": [
  // ... existing entries ...
  {
    "id": "LongCat-2.0-Preview",
    "provider": "longcat"
  }
]
```

> ⚠️ **Must use dict format** `{"id": "...", "provider": "..."}` — do NOT use plain string `"LongCat-2.0-Preview"` as it defaults to the NVIDIA provider and will fail.

**b) Groups (for ping rotation — A/B alternation):**

```json
"B": [
  // ... existing entries ...
  {"id": "LongCat-2.0-Preview", "provider": "longcat"}
]
```

Same dict format requirement. The A/B groups alternate ping cycles so each model is tested roughly once per hour.

> ⚠️ **Critical: categories models must be in A/B groups to get pinged.** Adding a model to `categories.deep` alone does NOT cause it to be pinged — the ping script only tests models listed in `groups.A` and `groups.B`. A model in `categories` but not in either group will never have speed data and won't appear in `ranking.json.top_by_category`. Always add new models to at least one ping group.

### 4. Set Up Google's OpenAI-Compatible Endpoint (If Using Google)

If adding Google models (Gemini/Gemma) to the ping system and the kanban profile, use Google's OpenAI-compatible endpoint to avoid `api_mode: gemini` compatibility issues with tool calling:

```python
# In nv_ping.py PROVIDERS:
"google": {
    "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    "keychain": "gemini_api_key",
    "expire": None,
    "format": "gemini",   # Uses Gemini native format for ping
}

# But in the kanban profile's config.yaml, use the OpenAI-compatible endpoint:
providers:
  google:
    name: Google Gemini
    base_url: https://generativelanguage.googleapis.com/v1beta/openai  # ← OpenAI-compat
    key_env: GOOGLE_API_KEY
    api_mode: chat_completions  # ← NOT "gemini" — avoids tool-call format issues
    default_model: gemini-3.5-flash
```

The ping script uses the native Gemini format (since it's just a speed test with no tool calls), while the kanban profile uses OpenAI-compatible format (so tool calling works correctly when the model is selected for actual tasks).

### 5. Verify the Setup

```bash
# Test keychain read
security find-generic-password -w -s "longcat_api_key"

# Test direct API call
curl -s "https://api.longcat.chat/openai/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(security find-generic-password -w -s longcat_api_key)" \
  -d '{"model":"LongCat-2.0-Preview","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('choices',[{}])[0].get('message',{}).get('content','FAIL'))"

# Wait for next ping cycle or run manually
python3 ~/.hermes/scripts/nv_ping.py

# Check ping results
cat ~/.hermes/data/NVping/tmp/ping_A.json | python3 -c "import json,sys;d=json.load(sys.stdin);[print(k,v) for k,v in d.get('models',{}).items() if 'LongCat' in k]"
```

### 6. Verify Kanban Can Use It

```bash
hermes kanban create "Test: LongCat ping" --assignee shanli --max-runtime 300
hermes kanban list | grep "Test"
```

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Ping returns ❌ for LongCat | Plain string in groups.json (no provider field) | Use dict format `{"id": "...", "provider": "longcat"}` |
| Keychain read fails | Wrong service name in PROVIDERS keychain field | Match exactly: `security find-generic-password -w -s "longcat_api_key"` |
| 401 from API | Key not written to Keychain | Run `security add-generic-password` step |
| 404 from API | Wrong URL path | Ensure full path includes `/v1/chat/completions` |
| Model in categories but never pinged | Only in categories, not in A/B groups | Add to `groups.A` or `groups.B` |
| Google tool-calling fails in kanban worker | `api_mode: gemini` used instead of `chat_completions` | Use OpenAI-compatible endpoint `base_url/.../openai` with `api_mode: chat_completions` |
| Provider priority not respected | Old `get_fastest()` sorts by pure speed | Ensure nv_ping.py's `get_fastest()` has the `(provider_priority, ms)` sort |

## Updating get_fastest() with Provider Priority

If the existing `get_fastest()` function sorts purely by speed, update it to include provider priority:

```python
def get_provider_priority(provider):
    """Provider 优先级：NV > LongCat > Google > OpenRouter"""
    priorities = {"nv": 1, "longcat": 2, "google": 3, "openrouter": 4}
    return priorities.get(provider, 99)

def get_fastest(category_ids, n=3):
    provider_map = {}
    for m in category_ids:
        if isinstance(m, dict):
            provider_map[m["id"]] = m.get("provider", "nv")
        else:
            provider_map[m] = "nv"
    
    candidates = []
    for r in results:
        if r["model"] in provider_map and r["ok"]:
            pri = get_provider_priority(r.get("provider", provider_map.get(r["model"], "nv")))
            candidates.append((pri, r["ms"], r["model"]))
    
    candidates.sort(key=lambda x: (x[0], x[1]))
    return [{"model": m, "ms": ms, "priority": pri} for pri, ms, m in candidates[:n]]
```

This ensures that among similarly-fast models, the preferred provider wins.
