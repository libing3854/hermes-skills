# Holographic Memory Provider — Internal Details

Source path: `~/.hermes/hermes-agent/plugins/memory/holographic/`

## Files

| File | Purpose |
|------|---------|
| `__init__.py` | Plugin bootstrap, MemoryProvider ABC implementation, tool registration |
| `holographic.py` | HRR (Holographic Reduced Representations) — phase vector math |
| `store.py` | SQLite-backed fact storage with FTS5 full-text search |
| `retrieval.py` | Fact retrieval, trust scoring, entity resolution, temporal decay |

## HRR Algebra (from `holographic.py`)

Uses **phase vectors** — each concept is a vector of phase angles in [0, 2π).

### Operations

| Operation | Math | Description |
|-----------|------|-------------|
| `bind(a, b)` | `(a + b) % 2π` | Associates two concepts into a composite vector. Result is quasi-orthogonal to both inputs. |
| `unbind(memory, key)` | `(memory - key) % 2π` | Retrieves a bound value. `unbind(bind(a, b), a) ≈ b` |
| `bundle(*vectors)` | Circular mean | Merges multiple concepts. The result is similar to all of them. |

### Deterministic Atom Generation

```python
def encode_atom(word: str, dim: int = 1024) -> np.ndarray:
    # SHA-256 of f"{word}:{i}" for i=0,1,2,...
    # Interpret digests as uint16, scale to [0, 2π)
    # Result is reproducible across processes, machines, and languages
```

- Uses `hashlib` (not numpy RNG) for cross-platform determinism
- Each SHA-256 digest = 32 bytes = 16 uint16 values
- Default dimension: 1024

### Dependencies

- NumPy is **optional** and auto-detected
- Without NumPy: core SQLite storage works, but HRR algebra operations are unavailable
- Check: `_HAS_NUMPY` flag in `holographic.py`

## Tool: `fact_store`

### Actions

| Action | Required Params | Description |
|--------|----------------|-------------|
| `add` | `content`, optional: `category`, `tags`, `entity` | Store a fact |
| `search` | `query` | Keyword lookup (FTS5) |
| `probe` | `entity` | All facts about a person/thing |
| `related` | `entity` | What connects to an entity? Structural adjacency |
| `reason` | `entities[]` | Compose: facts connected to MULTIPLE entities |
| `contradict` | — | Memory hygiene: conflicting claims |
| `update` | `fact_id` + optional: `content`, `category`, `tags`, `trust_delta` | Update a fact |
| `remove` | `fact_id` | Delete a fact |
| `list` | optional: `category`, `limit` | List recent facts |

### Categories

- `user_pref` — User preferences, habits, personal info
- `project` — Project context, file paths, commands
- `tool` — Tool usage patterns, CLI tricks
- `general` — General knowledge (default)

## Tool: `fact_feedback`

Rate facts to train trust scores:

| Parameter | Description |
|-----------|-------------|
| `fact_id` | ID of the fact to rate |
| `rating` | `"helpful"` (boost trust) or `"unhelpful"` (decrease trust) |

Trust scores decay facts with low confidence, keeping the memory store clean.

## Config (in `plugins.hermes-memory-store`)

| Key | Default | Notes |
|-----|---------|-------|
| `db_path` | `$HERMES_HOME/memory_store.db` | SQLite database; created lazily |
| `auto_extract` | `false` | Set `true` to auto-extract facts from conversations |
| `default_trust` | `0.5` | New facts start at this trust level |
| `min_trust_threshold` | `0.3` | Facts below this threshold are filtered from results |
| `temporal_decay_half_life` | `0` | In seconds; 0 = no decay. Positive value causes facts to decay over time |

## Usage Pattern

```yaml
# config.yaml
memory:
  provider: holographic
plugins:
  hermes-memory-store:
    db_path: ~/.hermes/memory_store.db
    auto_extract: true
    default_trust: 0.5
```

Best practice workflow:
1. User says something memorable → auto-extract (if enabled) or manual `fact_store(action="add", content="...")`
2. Before answering a personal question → `fact_store(action="probe", entity="user_name")` 
3. After recalling a fact → `fact_feedback(fact_id=X, rating="helpful")` to train trust
