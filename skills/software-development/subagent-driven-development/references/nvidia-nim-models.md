# NVIDIA NIM Multi-Model Reference

> API Key: macOS Keychain (`nvidia_api_key`)
> Expires: **2027-05-17**
> Rate limit: ~15 concurrent req/s
> Endpoint: `https://integrate.api.nvidia.com/v1/chat/completions`

---

## Overview

闪莉 and 闪莉mimi use the NVIDIA NIM API with **concurrent request racing**: multiple models are called in parallel, and the first response wins. This provides the lowest possible latency with built-in fault tolerance.

---

## Model Classification (37 working models)

All models are classified into 3 tiers based on size and latency, relative to 小莉 (4B/80K local model):

### 🐣 闪莉mimi — 小莉's Cloud Backup (15 models)

**Criteria**: < 4B (smaller than 小莉) OR < 10B with response < 5s
**Fallback**: If all racing models fail → 小莉 (local)

| Group | Model | Latency | Specialty |
|:-----:|-------|:-------:|-----------|
| A | `meta/llama-3.2-1b-instruct` | 722ms | Minimal Q&A |
| A | `google/gemma-2-2b-it` | 781ms | Lightweight chat |
| A | `nvidia/ising-calibration-1-35b-a3b` | 882ms | Simple reasoning |
| A | `nvidia/nemotron-mini-4b-instruct` | 894ms | General light |
| A | `nvidia/riva-translate-4b-instruct-v1.1` | 770ms | Translation |
| A | `nvidia/nemotron-content-safety-reasoning-4b` | 854ms | Safety |
| A | `nvidia/llama-3.1-nemotron-nano-8b-v1` | 813ms | General text |
| A | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | 923ms | 🖼️Basic vision |
| B | `meta/llama-3.2-3b-instruct` | 1283ms | Lightweight chat |
| B | `google/gemma-3n-e2b-it` | 1257ms | Lightweight chat |
| B | `google/gemma-3n-e4b-it` | 1266ms | Lightweight chat |
| B | `nvidia/gliner-pii` | 776ms | 🔍Entity/PII extraction |
| B | `nvidia/llama-3.1-nemoguard-8b-content-safety` | 1238ms | 🛡️Content safety |
| B | `nvidia/llama-3.1-nemoguard-8b-topic-control` | 1121ms | 🛡️Topic control |
| B | `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | 1252ms | 🛡️Safety guard |

### 🚀 闪莉 — Daily Driver / 轻量 Models (20 models)

**Criteria**: > 4B, response < 5s
**Fallback**: deepseek-v4-flash (original flash model)

| Group | Model | Latency | Specialty |
|:-----:|-------|:-------:|-----------|
| A | `mistralai/ministral-14b-instruct-2512` | 795ms | 💬Fastest chat |
| A | `meta/llama-3.2-11b-vision-instruct` | 832ms | 🖼️**Image understanding** |
| A | `mistralai/mistral-nemotron` | 912ms | 💬Chat |
| A | `meta/llama-4-maverick-17b-128e-instruct` | 932ms | 💬**Default daily** |
| A | `mistralai/mixtral-8x22b-instruct-v0.1` | 912ms | 💬Chat |
| A | `nvidia/nemotron-nano-12b-v2-vl` | 923ms | 🖼️Vision backup |
| A | `nvidia/nemotron-3-super-120b-a12b` | 1295ms | 🧠Deep reasoning |
| A | `meta/llama-guard-4-12b` | 746ms | 🛡️Safety filter |
| A | `mistralai/mixtral-8x7b-instruct-v0.1` | 1152ms | 💬Chat |
| A | `nvidia/nemotron-3-content-safety` | 1194ms | 🛡️Safety |
| B | `qwen/qwen3-next-80b-a3b-thinking` | 830ms | 🧠**Fast reasoning** |
| B | `mistralai/mistral-small-4-119b-2603` | 867ms | 💬Chat |
| B | `meta/llama-3.3-70b-instruct` | 947ms | 💬**Strong chat** |
| B | `moonshotai/kimi-k2.6` | 1033ms | 🖼️Multimodal |
| B | `upstage/solar-10.7b-instruct` | 1025ms | 💬Chat |
| B | `sarvamai/sarvam-m` | 1037ms | 💬Chat |
| B | `stockmark/stockmark-2-100b-instruct` | 1088ms | 💬Chat |
| B | `nvidia/llama-3.3-nemotron-super-49b-v1` | 1163ms | 💬Medium complex |
| B | `qwen/qwen3-next-80b-a3b-instruct` | 3484ms | 🧠Deep reasoning |
| B | `abacusai/dracarys-llama-3.1-70b-instruct` | 4817ms | 🧠Deep fallback |

### 🧠 Deep Models (subset of 轻量, 4 models)

| Group | Model | Latency | Use |
|:-----:|-------|:-------:|-----|
| A | `nvidia/nemotron-3-super-120b-a12b` | 1295ms | Heavy reasoning |
| A | `meta/llama-4-maverick-17b-128e` | 932ms | Deep MoE reasoning |
| B | `qwen/qwen3-next-80b-a3b-instruct` | 3484ms | Complex reasoning |
| B | `abacusai/dracarys-llama-3.1-70b-instruct` | 4817ms | Deep fallback |

---

## Ping System

小莉 runs the ping script (`~/.hermes/scripts/nv_ping.py`) via cron every 30 minutes:

```
00:00 → Group A (18 models pinged)
00:30 → Group B (19 models pinged)  
01:00 → Group A
... alternating ...
```

Each model is pinged once per hour. Results stored in:

```
~/.hermes/data/NVping/
  tmp/ping_A.json        ← latest Group A results
  tmp/ping_B.json        ← latest Group B results  
  tmp/ranking.json       ← current racing rankings (top-3 per category)
  tmp/groups.json        ← current group assignment (dynamically updated daily)
  tmp/health.json         ← health check (last success, success rate)
  day/YYYY-MM-DD.json     ← daily archive (48 records + evaluation)
  week/YYYY-Www.json      ← weekly summary
  month/YYYY-MM.json      ← monthly archive
```

---

## Racing Strategy

### Per-request Flow

```
莉莉丝 assigns task
  → reads tmp/ranking.json (latest ping data)
  → determines task type (chat/vision/deep)
  → selects top-3 models from matching category
  → launches 3 concurrent requests
  → whichever returns first → deliver result
  → remaining threads discarded
```

### Traffic-Aware Decision

闪莉 reads `health.json` before racing to check platform load:

| Load Level | Strategy |
|:----------:|----------|
| 🌙 **Low** (off-peak) | Race normally, use any category |
| ☀️ **Normal** | Race normally per task type |
| 🚥 **High** (peak hour) | Race only mimi models (smallest/fastest) |
| ⚠️ **Spike** (anomaly) | Skip NVIDIA entirely → fallback to Flash or 小莉 |

### Fallback Chain

| Agent | Primary | Fallback 1 | Fallback 2 |
|-------|---------|-----------|-----------|
| 🐣 **闪莉mimi** | 3 mimi models concurrent | → 小莉 (local) | — |
| ⚡ **闪莉** | 3 轻量/vision/deep models concurrent | → deepseek-v4-flash | → 小莉 |
| 🧠 **大莉** | deepseek-v4-pro | → 闪莉 (NVIDIA racing) | → 小莉 |

---

## Dynamic Regrouping

Every day at 00:00, `nv_daily_eval.py` runs:

1. **Merge** all 48 ping records from the day into `day/YYYY-MM-DD.json`
2. **Evaluate** each model: avg_ms, std_ms, success_rate, trend (stable/improving/degrading/unstable)
3. **Snake-redistribute** A/B groups: rank 1→A, 2→B, 3→B, 4→A, 5→A, 6→B...
4. **Identify** peak/off-peak hours from platform-wide latency
5. **Clean up** data older than 90 days (day), 52 weeks (week), 24 months (month)
6. **Check** API key expiry (warn at 30/7/1 days remaining)
7. Update `tmp/groups.json` with new assignments and `effective_from` timestamp
