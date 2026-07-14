# Gemini Reverse-Engineered API Tools

Research from 2026-06-17 session. User has Gemini Pro subscription ($19.99/mo).

## Gemini Pro Subscription vs API

- Pro subscription does NOT include API access (separate billing systems)
- Pro subscription: Gemini App + Google Workspace integrations only
- API: accessed via ai.google.dev, free tier available, pay-as-you-go beyond
- Google testing subscription ↔ AI Studio link but not rolled out yet

## Reverse-Engineered Gemini Web → API Projects (ranked by safety + stars)

### 1. Sophomoresty/gemini-web2api ⭐ 1.8k, Fork 420
- **Safest option**: single Python file, zero dependencies (only httpx for streaming)
- Converts Gemini web to OpenAI-compatible API
- **Works WITHOUT authentication** for basic text generation (anonymous access)
- Fully local, minimal attack surface
- github.com/Sophomoresty/gemini-web2api

### 2. HanaokaYuzu/Gemini-API ⭐ 3.2k, Fork 506
- Most mature: async Python wrapper, PyPI package (`gemini-webapi`)
- Features: persistent cookies, image/video/audio gen, Deep Research, Gems
- Dependencies: curl-cffi, loguru, orjson, pydantic (all reputable)
- License: AGPL-3.0
- 257 commits, 67 tags, active maintenance (2+ years)
- Risk: single maintainer, Google反制随时可能
- **Safety audit passed**: all HTTP requests go to Google domains only, no telemetry
- **Requires Python 3.10+** (uses `type | type` union syntax)
- **Auth is fragile**: PSIDTS cookies expire frequently, library strict about validation
- github.com/HanaokaYuzu/Gemini-API

### 3. Amm1rr/WebAI-to-API ⭐ 1.3k
- FastAPI server, Apache 2.0
- Multi-provider via gpt4free integration
- More dependencies = larger attack surface
- github.com/Amm1rr/WebAI-to-API

### 4. ntthanh2603/gemini-web-to-api ⭐ 240
- Smaller, less mature
- Compatible with OpenAI/Gemini/Claude formats
- github.com/ntthanh2603/gemini-web-to-api

## Setup: gemini-web2api (Recommended)

### Quick Start
```bash
# Clone and setup
cd /tmp && git clone --depth 1 https://github.com/Sophomoresty/gemini-web2api.git
cd gemini-web2api
python3.12 -m venv venv && source venv/bin/activate
pip install httpx

# Create config (optional - defaults work fine)
cat > config.json << 'EOF'
{
  "port": 8081,
  "host": "0.0.0.0",
  "default_model": "gemini-3.5-flash",
  "api_keys": [],
  "log_requests": true
}
EOF

# Start server
python3 gemini_web2api.py
```

### Available Models
| Model | Description |
|-------|-------------|
| gemini-3.5-flash | Fast general-purpose |
| gemini-3.5-flash-thinking | Deep thinking, longest output (~20k chars) |
| gemini-3.1-pro | Pro model (needs cookie for real routing) |
| gemini-auto | Auto model selection |
| gemini-flash-lite | Lightweight fast model |

### Test
```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-3.5-flash","messages":[{"role":"user","content":"Hello"}]}'
```

### Use in Hermes
Add to config.yaml:
```yaml
custom_providers:
- base_url: http://localhost:8081/v1
  key_env: ""
  model: gemini-3.5-flash
  name: Gemini Local
```

## Setup: gemini-webapi (HanaokaYuzu)

### Requirements
- Python 3.10+ (uses `type | type` union syntax)
- Cookies: `__Secure-1PSID` and `__Secure-1PSIDTS` from browser

### Quick Start
```bash
python3.12 -m venv venv && source venv/bin/activate
pip install gemini-webapi browser-cookie3
```

### Known Issues
- PSIDTS cookies expire frequently, causing AuthError
- browser-cookie3 may not decrypt macOS Chrome cookies properly
- Cookie injection via CDP Network.setCookie fails for Google (detected)

## Recommendation for User

**For simplicity**: Use Sophomoresty/gemini-web2api (works without auth, single file)
**For features**: Use HanaokaYuzu/Gemini-API (multi-turn, streaming, Gems, but fragile auth)
**Always**: Use a dedicated Google account (not primary) to reduce ban risk
**Backup**: Keep official Gemini API (free tier) as fallback
