# Profile Missing config.yaml — Full Diagnosis & Fix

> Session artifact: two shanli (闪莉) kanban tasks crashed 1010x + 96x due to missing profile `config.yaml`.

## Symptoms

1. **Task t_9e3985d7** (1010 crashes): `HTTP 400: No models provided` — Provider: openrouter, Model: (empty)
2. **Task t_6798ac40** (96 crashes, blocked 44h): `HTTP 401: incorrect api key` — Provider: custom, Model: LongCat-2.0-Preview
3. Both tasks were stuck in `running` status with `protocol_violation` crash loops (~60s each)

## Diagnosis Chain

### Step 1: Check profile status
```bash
hermes profile show shanli
# → Model: (not shown) — no config.yaml
# → .env: not configured
# → Gateway: stopped

hermes kanban assignees
# → shanli: ON DISK: no  ← gateway not running
```

### Step 2: Check profile directory
```bash
ls ~/.hermes/profiles/shanli/
# → No config.yaml! No .env!
# → Only: SOUL.md, state.db, sessions/, skills/, logs/
```

### Step 3: Check agent log
```bash
tail -30 ~/.hermes/profiles/shanli/logs/agent.log
```

**Task t_9e3985d7 log:**
```
No .env file found. Using system environment variables.
OpenAI client created (agent_init, shared=True) thread=MainThread provider=openrouter base_url=https://openrouter.ai/api/v1 model=
...
API call failed (attempt 1/3): BadRequestError [HTTP 400]
Provider: openrouter  Model:
Error: HTTP 400: No models provided
```

**Task t_6798ac40 kanban log:**
```
Provider: custom  Model: LongCat-2.0-Preview
Error: HTTP 401: incorrect api key
```

### Step 4: Check health.json for provider status
```json
// ~/.hermes/data/NVping/tmp/health.json
{
  "providers": {
    "nv": 12,
    "openrouter": 0,    // ← 0 success count → excluded by health filter
    "google": 3
  }
}
```

OpenRouter has 0 success count — even if the API key were correct, the health filter would exclude it. This makes the OpenRouter fallback a double failure.

### Step 5: Verify main config has valid credentials
```bash
grep LONGCAT_API_KEY ~/.hermes/.env
# → LONGCAT_API_KEY=ak_2JI...2q0z  (exists)
```

Main config's `providers.longcat.api_key` is set. But profile resolves as `custom` provider, bypassing the configured `providers` section.

### Step 6: Check kanban runtime config
```yaml
# ~/.hermes/config.yaml
kanban:
  max_runtime: 8m   # ← default, far too short for LongCat writing tasks
```

## Root Cause

Shanli profile was created via `hermes profile create shanli` which auto-generates `SOUL.md` but does NOT create `config.yaml` or `.env`. Without `config.yaml`:

1. **Model resolution collapses**: No `model.provider` / `model.default` → Hermes falls back through the model catalog → lands on OpenRouter with empty model name
2. **Provider routing breaks**: When model_selector returns `provider: longcat`, Hermes resolves it as `custom` (not matching the main config's `providers.longcat` entry) → `api_key` in the `providers` section is never read
3. **Env vars missing**: No profile `.env` → `key_env` references resolve to system env only (which may not have all keys)

## Fix Applied

### 1. Created `/Users/libing/.hermes/profiles/shanli/config.yaml`:
```yaml
model:
  provider: deepseek
  default: deepseek-v4-flash

# ⚠️ 必须显式设置 vision，否则 auto 路由到 deepseek → 不支持多模态 → 400
auxiliary:
  vision:
    provider: longcat
    model: LongCat-2.0-Preview

providers:
  longcat:
    name: LongCat
    api_key: ak_2JI8lE91l6Za45o0y89L81WL02q0z   # plaintext, bypasses .env
    api_mode: chat_completions
    base_url: https://api.longcat.chat/openai
    context_length: 1048576
    default_model: LongCat-2.0-Preview

  deepseek:
    name: DeepSeek
    key_env: DEEPSEEK_API_KEY
    api_mode: chat_completions
    base_url: https://api.deepseek.com
    default_model: deepseek-v4-flash

  nv:
    name: NVIDIA NIM
    key_env: NVIDIA_API_KEY
    api_mode: chat_completions
    base_url: https://integrate.api.nvidia.com/v1

  openrouter:
    name: OpenRouter
    key_env: OPENROUTER_API_KEY
    api_mode: chat_completions
    base_url: https://openrouter.ai/api/v1

  google:
    name: Google Gemini
    key_env: GOOGLE_API_KEY
    api_mode: chat_completions
    base_url: https://generativelanguage.googleapis.com/v1beta/openai

  xiaomi:
    name: Xiaomi MiMo
    key_env: XIAOMI_API_KEY
    api_mode: chat_completions
    base_url: https://token-plan-cn.xiaomimimo.com/v1
    default_model: mimo-v2.5-pro
    models:
    - mimo-v2.5-pro
    - mimo-v2.5
    - mimo-v2-pro
    - mimo-v2-omni
```

### 2. Raised kanban max_runtime
```bash
hermes config set kanban.max_runtime 2h
```

### 3. Started shanli gateway
```bash
hermes gateway start --profile shanli
```

### 4. Reclaimed tasks
```bash
hermes kanban block t_9e3985d7 "已修复根因..."
hermes kanban block t_6798ac40 "已修复根因..."
hermes kanban unblock t_9e3985d7
hermes kanban unblock t_6798ac40
hermes kanban dispatch
```

## Verification
After fixes, both tasks spawned, loaded their context, and started doing actual work (reading files, searching, writing) instead of crashing in 3s with API errors.

## Key Lessons

1. **`hermes profile create` does NOT create config.yaml or .env** — always check and create one manually for kanban execution profiles
2. **Profile without config.yaml → wrong provider fallback** — not just "uses parent config," but actively resolves to a broken provider
3. **Provider resolution as "custom" bypasses `providers.<name>.api_key`** — plaintext keys in main config are invisible to a profile without its own `providers` section
4. **health.json should be checked** — `openrouter: 0` success count means OpenRouter fallback is guaranteed to fail
5. **Check agent.log, not just kanban log** — the agent log (`~/.hermes/profiles/<name>/logs/agent.log`) reveals the actual provider/model used at client creation, which is often more informative than the kanban log's error message
6. **Never increase runtime for auth errors** — the `provider=openrouter model=` pattern is a config problem, not a timeout problem
7. **`auxiliary.vision` must be explicit** — without it, `auto` routes vision tasks to the main provider (e.g. deepseek) which may not support multimodal → HTTP 400. Always set `auxiliary.vision.provider` and `auxiliary.vision.model` in profile config
8. **`failure_limit` should be 5 for free model pools** — default `2` is too low for volatile free providers
