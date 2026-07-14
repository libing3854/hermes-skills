# case-study: model_selector.py — From Design Extraction to Implementation

## Background

冰哥 wanted to improve 闪莉's model selection system. Instead of installing `model-router` directly (which modifies Hermes core files), we:
1. Reviewed its source code (Stage 2 + 3 in the adoption workflow)
2. Extracted 9 design inspirations
3. Implemented a Python-only adaptation as `~/.hermes/scripts/model_selector.py`

## Design Inspirations Extracted from model-router

| # | Idea | Source | Our Implementation |
|---|------|--------|-------------------|
| 1 | Lightweight classifier | qwen3.5-flash triage model | Decided NOT to copy — 冰哥's free tier doesn't need a classifier per turn |
| 2 | Fast-path ACK | Regex `^(ok\|okay\|thanks\|...)` | Chinese-Aware regex: ≤2 chars direct, ≤4 chars + regex match → `mimi` category |
| 3 | Session state (pin/unpin) | `_session_pinned`, `_last_tier` dicts | JSON state file at `~/.hermes/data/model_selector_state.json` + fcntl file lock |
| 4 | Self-escalation | `_tool_errors` counter: 2 errors → +1 tier | Same logic: `session["errors"]` ≥ 2 → upgrade category (light→deep) |
| 5 | YAML config | `model_router.yaml` deep merge | Marked as TODO (CONFIG_PATH defined but not implemented yet) |
| 6 | `.bak` timestamp backup | `backup_path()` with datetime stamp | Added to nv_ping.py integration plan (not yet done) |
| 7 | Explicit tier detection | Regex for `T3`, `tier 4` in user text | Implemented via `--category` and `--pin` CLI flags |
| 8 | Status bar model info | Monkey-patch `cli._get_status_bar_snapshot` | Omitted — Hermes status bar not needed for backend script |
| 9 | Provider health filtering | Check consecutive failures per provider | Adapted to read `health.json` (existing in 冰哥's setup) |

## Architecture

```
User calls → model_selector.py (CLI tool)
  │
  ├── load_ranking()       → reads ~/.hermes/data/NVping/tmp/ranking.json
  ├── get_health_providers()→ reads health.json, excludes unhealthy providers
  ├── is_fast_path()       → checks message length + regex
  ├── get_session()        → loads state from model_selector_state.json
  └── select_model()       → core logic:
       ├── 去重检查 (last_msg)
       ├── escalation 处理
       ├── pin/unpin 固定
       ├── category 选择 (mimi→light→deep)
       └── get_best_model() → sort by provider priority (NV>GC>OR) + health filter
```

## CLI Usage

```bash
# Select best model for a task
python3 model_selector.py --task "今天天气怎么样？" --session mysession

# Pin session to a category (always use mimi for simple tasks)
python3 model_selector.py --pin mimi --session mysession

# Unpin
python3 model_selector.py --unpin --session mysession

# Report failure (triggers auto-upgrade: light → deep after 2 failures)
python3 model_selector.py --report-failure --session mysession

# View session state
python3 model_selector.py --status --session mysession

# Specify category hint
python3 model_selector.py --task "复杂分析..." --category deep --session mysession
```

## Output format (JSON)

```json
{
  "model": "mistralai/ministral-14b-instruct-2512",
  "provider": "nv",
  "category": "light",
  "reason": "✅ light → nv/mistralai/ministral-14b-instruct-2512",
  "fast_path": false,
  "escalated": false,
  "pinned": false,
  "session_id": "mysession"
}
```

## File Locations

| File | Path |
|------|------|
| Main script | `~/.hermes/scripts/model_selector.py` |
| Ranking data | `~/.hermes/data/NVping/tmp/ranking.json` |
| Session state | `~/.hermes/data/model_selector_state.json` |
| Provider health | `~/.hermes/data/NVping/tmp/health.json` |
| Fallback config | `~/.hermes/model_selector.yaml` (TODO) |
