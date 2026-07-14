# model-selector: Provider Priority Configuration

The `model-selector` plugin (`~/.hermes/scripts/model_selector.py`) is the active model routing engine. It consumes `ranking.json` (produced by `nv_ping.py`) and applies provider priority ordering to select the best model for each task category.

## Architecture

```
nv_ping.py (every 30min)     model_selector.py (on every request)
        │                              │
        ▼                              │
  ranking.json ────────────────────────►│
  (ping latencies)                      │
                                        │
  MIMO_FALLBACK_POOL (static) ─────────►│
  (MiMo models not in ranking)          │
                                        ▼
                                 Selected model
                                 (best match for task)
```

## Provider Priority Order

Priority is configured in `get_best_model()` as a dict:

```python
priority = {"longcat": 0, "xiaomi": 1, "nv": 2, "google": 3, "openrouter": 4}
```

Lower number = higher priority. Current order:

| Rank | Provider | Models |
|:----:|:---------|:-------|
| 0 | LongCat | LongCat-2.0-Preview |
| 1 | Xiaomi MiMo (Token Plan) | mimo-v2.5-pro, mimo-v2.5, mimo-v2-omni |
| 2 | NVIDIA NIM | ~52 models from ranking.json |
| 3 | Google Gemini | ~6 models from gropus.json |
| 4 | OpenRouter (free) | ~17 models from groups.json |

## Adding a New Provider

### Step 1: Add to nv_ping.py PROVIDERS (for Ping)
If the new provider should be pinged for latency data, add it to `nv_ping.py`:

```python
PROVIDERS = {
    "newprovider": {
        "url": "https://api.example.com/v1/chat/completions",
        "keychain": "newprovider_api_key",
        "expire": None,
        "format": "openai",
    },
}
```

### Step 2: Add to ranking via groups.json
Add model entries to appropriate categories in `groups.json`:
- `mimi` — lightweight (<5B or marked nano/tiny)
- `light` — everyday models (5-30B)
- `deep` — heavy models (>30B or thinking/reasoning)
- `vision` — multimodal models

### Step 3: Add to model_selector.py priority
```python
priority = {"longcat": 0, "xiaomi": 1, "newprovider": 2, "nv": 3, ...}
```

### Step 4: (Optional) Static Fallback Pool
If the provider isn't in ranking.json (e.g. no ping data), add a static fallback:

```python
MIMO_FALLBACK_POOL = {
    "deep": [
        {"id": "model-name", "provider": "newprovider"},
    ],
}
```

### Step 5: Verify Selection
```bash
python3 ~/.hermes/scripts/model_selector.py --task "test" --category deep
# Should show the new provider/model
```

## Pitfalls

### ❌ MiMo not in ranking.json
Xiaomi MiMo models are NOT in ranking.json (they aren't pinged by nv_ping.py). They only appear via `MIMO_FALLBACK_POOL`. This means they have no latency data and are selected purely by priority order.

### ❌ Provider name must match exactly
The provider string in `priority` dict, `MIMO_FALLBACK_POOL`, and ranking.json categories must match exactly. Case-sensitive: `"xiaomi"` not `"Xiaomi"` or `"XIAOMI"`.

### ❌ Fallback added at wrong position in list
`get_best_model()` does `available = available + mimo_fb` (append to end), then sorts by priority. If you change it to `mimo_fb + available` (prepend), priority ordering is defeated.

### ❌ Provider mismatch between model-selector and nv-ping
`nv_ping.py` has its own `PROVIDERS` dict with its own priority concept. model-selector's `priority` dict is independent. A provider can exist in one and not the other.

### ❌ active_profile affects which .env is read
When gateway spawns a worker, it reads the active profile's `.env`, not the main `~/.hermes/.env`. If the active profile lacks a provider's API key, that provider will be unavailable. Check `cat ~/.hermes/active_profile`.

## Configuration Files

| File | Purpose |
|:-----|:--------|
| `~/.hermes/scripts/model_selector.py` | Selection engine with priority + fallback |
| `~/.hermes/data/NVping/tmp/ranking.json` | Live ping latency data (read-only for model_selector) |
| `~/.hermes/config.yaml` | Provider definitions (api_key, base_url, model list) |
| `~/.hermes/.env` | API keys for all providers |
| `~/.hermes/active_profile` | Current active profile (affects which .env is loaded) |

## See Also

- `gateway-platform-diagnostics` skill — active_profile diagnosis for gateway connectivity
- `nv-multi-model` skill's main SKILL.md — ping system architecture and group classification
