# MiMo Code Custom Provider Configuration

## Problem
MiMo Code (Xiaomi's OpenCode fork) only shows Xiaomi models by default. Users want to use external models like Agnes, DeepSeek, etc.

## Solution: Environment Variables

MiMo Code reads OpenAI-compatible providers via environment variables:

```bash
export OPENAI_API_KEY="your...port OPENAI_BASE_URL="https://apihub.agnes-ai.com/v1"
```

After setting these, `mimo models` will show models from the custom API with `openai/` prefix.

## Solution: --model Parameter

Start MiMo Code with a specific model:

```bash
mimo --model openai/agnes-2.0-flash
```

This overrides the default model for that session.

## Solution: Config File (Recommended)

Create `mimocode.json` at `~/Desktop/mimo/mimocode.json` (MiMo Code reads this path):

```json
{
  "provider": {
    "name": "agnes",
    "api": "https://apihub.agnes-ai.com/v1",
    "options": {
      "apiKey": "your-api-key"
    },
    "models": ["agnes-2.0-flash"]
  }
}
```

**Key points:**
- Model format in config: `agnes/agnes-2.0-flash` (provider/model)
- `mimo models` should show `agnes/agnes-2.0-flash` ✅
- Config path: `~/Desktop/mimo/mimocode.json`

## Limitations

1. **Model name format**: Custom providers show as `agnes/xxx` (provider/model format)
2. **Provider login bug**: `mimo providers login` fails for custom providers (TypeError)
3. **Rate limits**: Free tiers (like MiMo Auto) have rate limits; custom APIs may have their own limits
4. **Not all models work**: Some model names from custom APIs may not be recognized
5. **MiMo Code only supports Xiaomi models by default**: Must configure custom provider to use external models

## Agnes API Specifics

- Base URL: `https://apihub.agnes-ai.com/v1`
- API Key env: `AGNES_API_KEY`
- Available models: agnes-2.0-flash, agnes-1.5-flash, agnes-image-2.0-flash, agnes-video-v2.0
- OpenAI-compatible interface

## Verified Working (2026-06-13)

```bash
# Test with curl
curl -s https://apihub.agnes-ai.com/v1/chat/completions \
  -H "Authorization: Bearer ***" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-2.0-flash","messages":[{"role":"user","content":"你好"}],"max_tokens":50}'
```

Response: `{"choices":[{"message":{"content":"你好！有什么我可以帮你的吗？"}}]}`
