# Agnes AI API — Alternative Image Generation

When `image_generate` (fal.ai) fails or ChatGPT browser approach is unavailable,
the Agnes AI API is a viable alternative for image generation.

## Source
GitHub: `Yacey/agnes-ai-generation-skill`
Script: `https://raw.githubusercontent.com/Yacey/agnes-ai-generation-skill/master/scripts/agnes_api.py`

## Setup
1. Download the script: `curl -s https://raw.githubusercontent.com/Yacey/agnes-ai-generation-skill/master/scripts/agnes_api.py -o /tmp/agnes_api.py`
2. Set API key: `export AGNES_API_KEY="your-key"` (or `AGNES_API_TOKEN` or `APIHUB_AGNES_API_KEY`)
3. Requires: `python3` (no extra pip packages — uses only stdlib)

## Models
- `agnes-2.0-flash` — text generation
- `agnes-image-2.1-flash` — image generation (text-to-image, image-to-image)
- `agnes-video-v2.0` — video generation

## Usage

### Text-to-image
```bash
python3 /tmp/agnes_api.py image --prompt "A luminous floating city above a misty canyon at sunrise, cinematic realism" --size 1024x768
```

### Image-to-image
```bash
python3 /tmp/agnes_api.py image --prompt "Turn the scene into a rainy cyberpunk night" --image https://example.com/input.png --size 1024x768
```

### Smoke test (no API key check)
```bash
python3 /tmp/agnes_api.py smoke-test
python3 /tmp/agnes_api.py smoke-test --include-image-edit
```

## Key Notes
- API base: `https://apihub.agnes-ai.com`
- English prompts recommended for image/video generation (more stable)
- Output is URL-based when `extra_body.response_format` is `url`
- Script validates image sizes before sending
- For high-quality images, include: subject hierarchy, environment, secondary details, lighting, composition, quality requirements

## When to Use
- fal.ai balance exhausted (image_generate tool returns "Exhausted balance")
- ChatGPT browser not logged in or unavailable
- Need image-to-image transformation
- Need specific model control (agnes-image-2.1-flash)
