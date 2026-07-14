# Agnes Image Generation Plugin — Implementation Details

## Agnes AI Image API Spec

- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **Endpoint**: `POST /v1/images/generations`
- **Auth**: Bearer token via `AGNES_API_KEY`
- **Free tier**: Yes, unlimited (as of June 2026)
- **Models**: `agnes-image-2.0-flash` (default), `agnes-image-2.1-flash`

### Request Format (OpenAI-compatible)

```json
{
  "model": "agnes-image-2.0-flash",
  "prompt": "description text",
  "n": 1,
  "size": "1024x1024"
}
```

### Response Format

```json
{
  "created": 1781157892,
  "data": [
    {
      "b64_json": null,
      "revised_prompt": null,
      "url": "https://platform-agnes-ai.space/images/text-to-image/..."
    }
  ],
  "usage": {"total_tokens": 0, ...}
}
```

- Returns **URL** (not b64_json) — use `save_url_image()` to cache locally
- URLs may be ephemeral — always cache before sending to platforms

## Implementation File Locations

- Plugin: `~/.hermes/plugins/image_gen/agnes/__init__.py`
- Config: `~/.hermes/plugins/image_gen/agnes/plugin.yaml`
- Generated images: `~/.hermes/cache/images/agnes_*.png`

## Configuration (config.yaml)

```yaml
image_gen:
  provider: agnes
  model: agnes-image-2.0-flash

plugins:
  enabled:
    - image_gen/agnes
```

## Testing

### Direct curl test (bypasses Hermes)

```bash
source ~/.hermes/.env
curl -s https://apihub.agnes-ai.com/v1/images/generations \
  -H "Authorization: Bearer $AGNES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"agnes-image-2.0-flash","prompt":"a cat","n":1,"size":"1024x1024"}'
```

### Via Hermes (after plugin installed + enabled)

```bash
hermes chat -q "使用 image_generate 工具生成一张图片：描述" -Q
```

## Pitfall: custom_providers vs image_gen plugin

The `custom_providers` config (in `config.yaml`) routes requests through `/v1/chat/completions`. This works for TEXT models but NOT for image generation, which uses `/v1/images/generations`. 

**Wrong approach**: Configure Agnes Image in `custom_providers` → `hermes chat` sends to wrong endpoint → 404.

**Correct approach**: Create an image_gen plugin that calls `/v1/images/generations` directly via `requests.post()`.

## Pitfall: os.environ not populated in tool subprocess

**Symptom**: `image_generate` tool reports "AGNES_API_KEY not set" even though the key is in `~/.hermes/.env` and `echo $AGNES_API_KEY` works in terminal.

**Root cause**: The plugin runs inside Hermes's tool subprocess. `load_hermes_dotenv()` may not have been called before the tool invocation, so `os.environ` doesn't contain the key.

**Fix**: Replace `os.environ.get("AGNES_API_KEY")` with a dual-path helper:

```python
def _get_api_key() -> Optional[str]:
    """Resolve API key from os.environ or ~/.hermes/.env directly."""
    key = os.environ.get("AGNES_API_KEY")
    if key:
        return key
    try:
        from hermes_cli.config import get_env_value
        return get_env_value("AGNES_API_KEY")
    except Exception:
        return None
```

Use `_get_api_key()` in both `is_available()` and `generate()`. This pattern works for ANY plugin reading API keys from `.env`.

## Plugin Development Notes

- Built-in backends (fal, openai, krea, xai) auto-load — no `plugins.enabled` needed
- User-installed backends (`~/.hermes/plugins/image_gen/<name>/`) require explicit `plugins.enabled` entry
- Plugin key format: `image_gen/<name>` (e.g., `image_gen/agnes`)
- After adding to enabled list, `image_generate` tool automatically discovers the provider
- Session must be restarted (`/reset` or new process) for plugin changes to take effect

## OpenAI-Compatible API Pattern

Many providers (Agnes, SiliconFlow, etc.) use the same `/v1/images/generations` endpoint. The plugin template works for any of them — just change:
1. `API_BASE_URL`
2. Model names in `_MODELS`
3. `requires_env` in plugin.yaml
4. `AGNES_API_KEY` → provider's env var name
