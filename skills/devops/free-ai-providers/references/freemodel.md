# FreeModel API Reference

## Overview
FreeModel provides access to GPT and Claude models through two separate API endpoints. Used for multi-AI analysis when internal models need external validation.

## Two Endpoints (Important!)

FreeModel has TWO separate APIs with different formats:

| Format | Endpoint | Models | Use Case |
|--------|----------|--------|----------|
| **OpenAI** | `https://api.freemodel.dev/v1` | GPT-5.5, GPT-5.4, GPT-5.4-mini, GPT-5.3-codex | ChatGPT SDK, Cursor, Hermes custom_provider |
| **Anthropic** | `https://cc.freemodel.dev` | Claude Opus 4.8, Claude Opus 4.7, Claude Sonnet 4.6, etc. | Claude Code, Cline, Anthropic SDK |

⚠️ **Pitfall:** Mixing formats fails:
- `cc.freemodel.dev` + OpenAI format → HTTP 305 error
- `api.freemodel.dev` + Anthropic format → HTTP 403 "restricted to official Claude Code client"

## Available Models (verified 2026-06-15)

### OpenAI Format (api.freemodel.dev)
| Model | Model ID | Context | Output | Price (input/output per M tokens) |
|-------|----------|---------|--------|-----------------------------------|
| GPT-5.3 Codex | gpt-5.3-codex | 400K | 128K | $1.75 / $14 |
| GPT-5.4 | gpt-5.4 | 1.05M | 128K | $2.50 / $15 |
| GPT-5.4 mini | gpt-5.4-mini | 400K | 128K | $0.75 / $4.50 |
| GPT-5.5 | gpt-5.5 | 1.05M | 128K | $5 / $30 |

### Anthropic Format (cc.freemodel.dev)
- Claude Opus 4.8 (claude-opus-4-8)
- Claude Opus 4.7 (claude-opus-4-7)
- Claude Opus 4.6 (claude-opus-4-6)
- Claude Sonnet 4.6 (claude-sonnet-4-6)
- Claude Haiku 4.5 (claude-haiku-4-5-20251001)
- Claude Fable 5 (claude-fable-5)

⚠️ **Anthropic endpoint restriction:** `cc.freemodel.dev` returns HTTP 403 for generic API calls. It only works with:
1. Claude Code CLI (`claude --print`)
2. Official Anthropic SDK with proper client headers

To use Claude models from Hermes, you must install Claude Code CLI and configure it with FreeModel's API key.

## Hermes Config Format

### GPT-5.5 (OpenAI format - works directly)
```yaml
custom_providers:
- api_key: <your-key>
  base_url: https://api.freemodel.dev/v1
  model: gpt-5.5
  name: FreeModel GPT-5.5
```

### Claude Opus 4.8 (Anthropic format - requires api_mode)
```yaml
custom_providers:
- api_key: <your-key>
  base_url: https://cc.freemodel.dev
  model: claude-opus-4-8
  name: FreeModel Claude Opus 4.8
  api_mode: anthropic_messages
```

⚠️ **Note:** The `api_mode: anthropic_messages` setting tells Hermes to use Anthropic's message format instead of OpenAI's chat completions format.

## Claude Code CLI Setup

To use FreeModel's Claude models:

1. Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code --prefix ~/.local
```

2. Set environment variables in `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY="<your-freemodel-key>"
export ANTHROPIC_BASE_URL="https://cc.freemodel.dev"
```

3. Test:
```bash
claude --print --model claude-opus-4-8 "Hello"
```

## Usage in delegate_task

```python
# Use FreeModel's GPT-5.5 (OpenAI format)
delegate_task(model="custom:FreeModel GPT-5.5", ...)

# Use FreeModel's Claude Opus 4.8 (Anthropic format)
delegate_task(model="custom:FreeModel Claude Opus 4.8", ...)
```

## API Key Notes
- Keys have ~29 day validity from creation
- Key prefix: `fe_oa_`
- Can list models via `GET /v1/models` (OpenAI format only)
- Chat completions via `POST /v1/chat/completions` (OpenAI format)
- Messages via `POST /v1/messages` (Anthropic format)

## Multi-AI Analysis Pattern

When facing complex architecture decisions, use multiple AI models independently:

1. **Internal analysis** — 大莉M (mimo-v2.5-pro) for deep analysis
2. **Internal review** — 大莉D (deepseek-v4-pro) for validation
3. **External analysis** — FreeModel GPT-5.5 or Claude Opus 4.8 for independent perspective
4. **Consolidate** — Compare findings, identify consensus and disagreements

This pattern catches blind spots that single-model analysis misses.
