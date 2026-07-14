# NV Ping System Debugging

## Architecture

- `~/.hermes/scripts/nv_ping.py` — Pings NVIDIA NIM models every 30min (cron: `208e496a9d72`)
- `~/.hermes/scripts/nv_daily_eval.py` — Daily evaluation + group rebalancing (cron: `5e6b5900e26d`)
- `~/.hermes/data/NVping/tmp/groups.json` — Model groups A/B (alternating ping cycles)
- `~/.hermes/data/NVping/tmp/state.txt` — Current group (A or B)
- `~/.hermes/data/NVping/tmp/ping_log.jsonl` — Historical ping results

## Known Bugs Fixed (2026-06-26)

### Bug 1: URL Double-Append

**Symptom:** All models return HTTP 404 even though direct curl works.

**Root cause:** `API_URL` already contains `/chat/completions`, but line 26 appends it again:
```python
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# Bug: double path
req = urllib.request.Request(f"{API_URL}/chat/completions", ...)
```

**Fix:** Use `API_URL` directly without appending:
```python
req = urllib.request.Request(API_URL, data=data, ...)
```

### Bug 2: Empty Groups Death Spiral

**Symptom:** Ping log stops writing, groups.json has empty A/B arrays, cron runs every 30min but outputs "空组".

**Root cause chain:**
1. NVIDIA deprecates old model IDs → all models return HTTP 404
2. nv_ping writes ping_A.json with success=0/N
3. nv_daily_eval reads the all-failed records
4. `evaluate()` skips models with no ms data → `sl` is empty
5. `new_grouping = {"A": [], "B": []}` → overwrites groups.json
6. Next day: empty groups → no pings → eval finds no records → skips
7. But groups.json is already empty, stays empty forever

**Fix:** Add guard in nv_daily_eval.py before overwriting groups.json:
```python
new_a = ev.get("new_grouping", {}).get("A", [])
new_b = ev.get("new_grouping", {}).get("B", [])
if not new_a and not new_b:
    print("  ⚠️ 新分组为空，跳过 groups.json 覆盖")
else:
    cg["groups"] = ev["new_grouping"]
    # ... write groups.json
```

### Bug 3: Model Deprecation

**Symptom:** Models that worked yesterday return HTTP 404 today.

**Diagnosis:** Test with direct API call:
```bash
curl -s -k -w "\nHTTP %{http_code}" \
  -H "Authorization: Bearer $(security find-generic-password -w -s nvidia_api_key)" \
  -H "Content-Type: application/json" \
  -d '{"model":"meta/llama-3.1-8b-instruct","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' \
  "https://integrate.api.nvidia.com/v1/chat/completions"
```

**Recovery:** Run model discovery script to find currently available models, then update groups.json.

## Model Testing Script

Location: `~/.hermes/scripts/nv_model_test.py`

Tests all candidate models and reports available/unavailable. Run periodically to catch deprecation.

## Chinese Writing Capability

Not all NVIDIA models can write Chinese. Test with a Chinese prompt before assigning to novel writing tasks. Models confirmed working for Chinese novel writing (as of 2026-06-26):
- meta/llama-3.3-70b-instruct (best quality, slow ~13s)
- meta/llama-4-maverick-17b-128e-instruct (good, fast)
- mistralai/mistral-nemotron (good quality, fast)
- mistralai/mistral-small-4-119b-2603
- meta/llama-3.1-70b-instruct
- mistralai/ministral-14b-instruct-2512
- meta/llama-3.1-8b-instruct (acceptable, fast)

Models that fail Chinese: mixtral-8x7b (English only), solar-10.7b (garbled), sarvam-m (mixed English)
