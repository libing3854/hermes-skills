# Multi-Agent Profile Setup

> Concrete walkthrough of setting up multi-agent profiles for Kanban, with ping-based dynamic model selection.

## Architecture Overview

```
Kanban Dispatcher
  └── default profile (deepseek-v4-flash) — coordination worker
       └── delegate_task → 闪莉 (dynamic model selection)
            ├── NV NVIDIA NIM (priority 1)
            ├── LongCat (priority 2)
            ├── Google Gemini (priority 3)
            └── OpenRouter (priority 4)
```

**Key principle:** Profiles are NOT the same as delegation targets. A profile is a technical config (model + provider + API keys). A delegation target is a conceptual role that may use a different model dynamically.

## Step 1: Create the Execution Profile

```bash
hermes profile create shanli --description "闪莉：免费模型动态选，看板任务执行者"
```

This creates `~/.hermes/profiles/shanli/` with a `config.yaml`, `.env`, and `SOUL.md`.

## Step 2: Configure the Profile

Write `~/.hermes/profiles/shanli/config.yaml`:

```yaml
# 闪莉 = 动态选模，无固定默认模型
# 根据 ping 排名从 deep/light 分类中选择最快的免费模型
# 优先级：NV > LongCat > Google > OpenRouter
# 无 ping 数据时降级到 LongCat-2.0-Preview 兜底
model:
  default: LongCat-2.0-Preview
  provider: longcat
providers:
  deepseek:
    name: DeepSeek
    base_url: https://api.deepseek.com
    key_env: DEEPSEEK_API_KEY
    api_mode: chat_completions
    default_model: deepseek-v4-flash
  longcat:
    name: LongCat
    base_url: https://api.longcat.chat/openai
    key_env: LONGCAT_API_KEY
    api_mode: chat_completions
    default_model: LongCat-2.0-Preview
  nv:
    name: NVIDIA NIM
    base_url: https://integrate.api.nvidia.com/v1
    key_env: NVIDIA_API_KEY
    api_mode: chat_completions
    default_model: meta/llama-3.1-8b-instruct
  google:
    name: Google Gemini
    base_url: https://generativelanguage.googleapis.com/v1beta/openai
    key_env: GOOGLE_API_KEY
    api_mode: chat_completions
    default_model: gemini-3.5-flash
  openrouter:
    name: OpenRouter
    base_url: https://openrouter.ai/api/v1
    key_env: OPENROUTER_API_KEY
    api_mode: chat_completions
    default_model: deepseek/deepseek-v4-flash:free
delegation:
  provider: deepseek
  model: deepseek-v4-pro
  key_env: DEEPSEEK_API_KEY
```

Set the `.env` with the keys from the user's main `.env`.

**Gotcha — Google api_mode:** Use `api_mode: chat_completions` with the OpenAI-compatible endpoint (`/v1beta/openai`) rather than `api_mode: gemini`. The Gemini-native format can cause tool-calling compatibility issues.

## Step 3: Register in Kanban

Add to `~/.hermes/config.yaml`:

```yaml
kanban:
  profiles:
    - default       # coordination worker
    - shanli        # 闪莉 — dynamic model selection
```

Tasks are assigned via `--assignee shanli`.

## Step 4: Set Up the Ping System

The ping system (`~/.hermes/scripts/nv_ping.py`) measures model latency across providers and produces rankings.

### 4a. Add a New Provider

```python
PROVIDERS = {
    "longcat": {
        "url": "https://api.longcat.chat/openai/v1/chat/completions",
        "keychain": "longcat_api_key",   # macOS Keychain service name
        "expire": None,
        "format": "openai",
    },
}
```

The API key must be in macOS Keychain, not just `.env`:

```bash
KEY=$(grep "LONGCAT_API_KEY" ~/.hermes/.env | cut -d'=' -f2)
security add-generic-password -s "longcat_api_key" -a "$USER" -w "$KEY" -U
```

### 4b. Register Models in Ping Groups

In `~/.hermes/data/NVping/tmp/groups.json`:

```json
{
  "groups": {
    "A": [ "...", {"id": "LongCat-2.0-Preview", "provider": "longcat"} ],
    "B": [ "...", {"id": "LongCat-2.0-Preview", "provider": "longcat"} ]
  },
  "categories": {
    "deep": [
      { "id": "LongCat-2.0-Preview", "provider": "longcat" }
    ]
  }
}
```

**Gotcha — dict vs string format:** Ping groups support both plain strings (`"model-name"` defaults to `nv` provider) and dicts (`{"id": "model", "provider": "longcat"}`). Always use the dict format for non-NVIDIA models, otherwise they get routed to the NVIDIA API and fail.

### 4c. Provider Priority in Ranking

The `get_fastest()` function in `nv_ping.py` should sort by `(provider_priority, ms)`:

```python
def get_provider_priority(provider):
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
            pri = get_provider_priority(r.get("provider", provider_map[r["model"]]))
            candidates.append((pri, r["ms"], r["model"]))
    
    candidates.sort(key=lambda x: (x[0], x[1]))
    return [{"model": m, "ms": ms, "priority": pri} for pri, ms, m in candidates[:n]]
```

This ensures NV models are preferred over LongCat at similar speeds.

## Step 5: Route Cron Jobs to the Profile

Use the `profile` parameter on cron jobs:

```bash
hermes cron update <job_id> --profile shanli
```

Or set it via the cronjob tool:
```python
cronjob(action="update", job_id="...", profile="shanli")
```

## Agent Role Definitions

Document the complete agent roster in `~/.hermes/莉莉丝的工作规范.md`:

| Agent | Model | Role |
|-------|-------|------|
| 🧠 莉莉丝 | Current session model (not fixed) | Main conversation window |
| ⚡ 闪莉 | Dynamic free model selection (NV→LongCat→Google→OpenRouter) | Kanban executor |
| 🚀 大莉 | deepseek-v4-pro (DeepSeek official) | Deep review via delegation |
| 🧐 莉莉 | deepseek-v4-flash (DeepSeek official) | Normal review via delegation |
| 🛠️ 小莉 | Huihui-Qwen3.5-4B (oMLX local) | Pure local operations |

## Common Pitfalls

- **Custom provider delegation bug:** When the main session model is a custom provider (LongCat, oMLX), `delegate_task` ignores the `delegation.provider` config and routes subagents through the main provider's URL. Fix: set the main model to a system provider (e.g. DeepSeek) before delegating, or use `execute_code` with direct API calls.
- **Google api_mode gemini format:** Avoid `api_mode: gemini` for the Google provider in profiles. Use `api_mode: chat_completions` with the OpenAI-compatible endpoint to ensure tool-calling works.
- **Keychain for ping scripts:** The ping system reads API keys from macOS Keychain, not from `.env`. Each provider must have its key added to Keychain separately.
- **Kanban profile model.default is only a fallback:** For dynamically-selecting profiles, `model.default` is used when no ping data is available. The actual task execution may use a different model from the ping pool.
