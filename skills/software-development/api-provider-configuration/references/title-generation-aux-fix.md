# Title Generation Auxiliary Fix (2026-06-01)

## Symptom
```
Auxiliary title generation failed: HTTP 401: Invalid API Key
```

## Root Cause
`title_generation` in `~/.hermes/config.yaml` had `provider: auto` and `model: ''`. 
With multiple providers configured (deepseek, xiaomi, longcat, omlx), the auto-resolver 
routed to the main provider (deepseek) but tried to call `mimo-v2.5` — a model that 
only exists on xiaomi. DeepSeek rejected it with 401.

## Fix Applied

### Before
```yaml
auxiliary:
  title_generation:
    api_key: ''
    base_url: ''
    extra_body: {}
    model: ''
    provider: auto
    timeout: 30
```

### After
```yaml
auxiliary:
  title_generation:
    model: mimo-v2.5
    provider: xiaomi
    timeout: 30
```

## Verification
Restart Hermes session. New session should generate titles without 401 errors.

## Other Auxiliary Features with Same Pattern
All 10 auxiliary features (`approval`, `compression`, `curator`, `flush_memories`, 
`kanban_decomposer`, `mcp`, `profile_describer`, `session_search`, `skills_hub`, 
`triage_specifier`) share the same default config of `provider: auto` + empty fields. 
They currently work because auto-resolver picks the main provider (deepseek) and the 
empty `model` defaults to the provider's default model. If they start failing with 
similar 401 errors, apply the same fix — explicitly set provider + model.

## Diagnosis Steps
1. Check which provider auto-resolver picked: look at the model name in the error message
2. Verify that model exists on that provider: `curl` the provider's `/v1/models` endpoint
3. If model doesn't exist on that provider, explicitly set `provider` and `model` in the auxiliary config
