# FreeModel API Configuration

## Two Endpoints

FreeModel has TWO separate API endpoints with different formats:

| Format | Endpoint | Models | Auth Header |
|--------|----------|--------|-------------|
| OpenAI | `https://api.freemodel.dev/v1` | GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.3-codex | `Authorization: Bearer <key>` |
| Anthropic | `https://cc.freemodel.dev` | Claude Opus 4.8, Opus 4.7, Sonnet 4.6, Haiku 4.5 | `x-api-key: <key>` + `anthropic-version: 2023-06-01` |

⚠️ **Anthropic endpoint ONLY works with Claude Code client.** Generic API calls return `403: This service is restricted to the official Claude Code client.`

## Config in Hermes

### OpenAI format (works with custom_providers)
```yaml
custom_providers:
- api_key: fe_oa_...
  base_url: https://api.freemodel.dev/v1
  model: gpt-5.5
  name: FreeModel GPT-5.5
  # 到期: 2026-07-14
```

### Anthropic format (requires api_mode)
```yaml
custom_providers:
- api_key: fe_oa_...
  base_url: https://cc.freemodel.dev
  model: claude-opus-4-8
  name: FreeModel Claude Opus 4.8
  api_mode: anthropic_messages
  # 到期: 2026-07-14
```

## Claude Code Integration

For using FreeModel's Claude models via Claude Code:

```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code --prefix ~/.local

# Set environment variables (add to ~/.zshrc)
export ANTHROPIC_API_KEY="fe_oa_..."
export ANTHROPIC_BASE_URL="https://cc.freemodel.dev"

# Test
claude --print --model claude-opus-4-8 "What model are you?"
```

⚠️ **Claude Code with FreeModel may require OAuth** — the `ANTHROPIC_API_KEY` environment variable alone may not be sufficient. Claude Code uses its own authentication flow that FreeModel recognizes. Setting `ANTHROPIC_API_KEY` and `ANTHROPIC_BASE_URL` may fail with `Invalid API key` even if the key is valid for the OpenAI endpoint.

## Common Pitfalls

1. **cc.freemodel.dev returns 305 error** if you try OpenAI format (`/v1/chat/completions`). Must use Anthropic format (`/v1/messages`).

2. **api.freemodel.dev only returns GPT models** in `/v1/models`. Claude models are NOT listed there.

3. **API key expires** — check expiry date and renew before it lapses.

4. **Base URL must NOT include `/v1`** for the Anthropic endpoint (it's appended automatically by the SDK).

5. **Anthropic endpoint returns 403 for direct API calls** — even with correct headers (`x-api-key`, `anthropic-version`), the endpoint returns `This service is restricted to the official Claude Code client.` The `api_mode: anthropic_messages` config in Hermes custom_providers will NOT work for Claude models via FreeModel.

## Kanban Worker Protocol Violation (2026-06-15)

**Problem:** Worker exits cleanly (rc=0) without calling `kanban_complete` or `kanban_block`, causing task to be marked as "gave up after repeated spawn failures."

**Symptoms:**
- Task status shows `running` but worker process is gone
- Error: `worker exited cleanly (rc=0) without calling kanban_complete or kanban_block — protocol violation`
- Task may auto-retry and fail again

**Common causes:**
1. Worker hit iteration limit (90/90 turns) before completing
2. Worker encountered an error but didn't call kanban_block
3. Worker completed work but forgot to call kanban_complete
4. Prompt was too complex, worker got confused

**Fix:**
```bash
# 1. Archive the failed task
hermes kanban archive <task_id>

# 2. Create a new task with clearer/simpler prompt
# - Break into smaller chunks
# - Add explicit "完成後調用 kanban_complete" instruction
# - Reduce scope per task

# 3. If worker wrote partial results, check files before re-dispatching
ls -la /path/to/正文/第*章_*.md | tail -10
```

**Prevention:** Add to task body:
```
⚠️ 完成后必须调用 kanban_complete 或 kanban_block。
不要直接退出，否则任务会被标记为失败。
```
