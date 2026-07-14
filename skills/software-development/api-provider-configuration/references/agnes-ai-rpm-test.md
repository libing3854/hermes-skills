# Agnes AI RPM Limit Test (2026-06-11)

## Test Methodology

Using curl in a loop with `--noproxy` flag, sending sequential requests to `https://apihub.agnes-ai.com/v1/chat/completions` with model `agnes-2.0-flash`, prompt `"hi"`, `max_tokens=5`.

## Test Results

| Request # | HTTP Status | Notes |
|-----------|:-----------:|-------|
| 1-12 | 200 | Successful |
| 13 | timeout | Network blip |
| 14-21 | 200 | Successful |
| **22** | **429** | **RPM limit hit** |

## Error Response (429)

```json
{
  "error": {
    "code": "",
    "message": "You've reached the API rate limit for free users. Upgrade to a Token Plan to unlock higher limits and continue using the API without interruption. (request id: 20260611034543701338646BudYxiPE)",
    "type": "AgnesAI_error"
  }
}
```

## Conclusion

- **Effective RPM limit: ~20 requests/minute** for free tier (21 successful, 22nd → 429)

### Image Models: Different Endpoint Required

`agnes-image-2.0-flash` and `agnes-image-2.1-flash` cannot be called via `/v1/chat/completions`. They return:

```json
{"error":{"message":"NotFoundError: NotFoundError","type":"upstream_error","code":"404"}}
```

These models use a dedicated image generation endpoint (`/v1/images/generations`). A Hermes `image_gen` plugin has been created at `~/.hermes/plugins/image_gen/agnes/` — the `image_generate` tool now calls Agnes directly. For ad-hoc calls, use `terminal()` with curl.

### `.env` Key Corruption Path (High-Impact)

This session revealed a new key corruption vector beyond `read_file` truncation:

1. `write_file` path for shell scripts — the `write_file` tool may mangle embedded key strings containing
   characters like `$` or `\` inside shell heredocs, creating syntax errors on execution.
2. Shell variable assignment via `$(grep ... | cut ...)` — when the assignment fails silently due to
   shell quoting, `$KEY` evaluates to empty, sending `Bearer ` (empty token) → 401.
3. Recovery: always verify key length with `echo ${#KEY}` before curl. 51 chars = correct for Agnes.
   Anything shorter means the assignment failed.

### Full Debugging Trace (2026-06-11)

```
Symptom: delegate_task for image gen always fallback to Pillow
Step 1: execute_code with hardcoded key → 401
Step 2: execute_code os.getenv("AGNES_API_KEY") → "NOT_FOUND" (9 chars)
Step 3: Terminal `export $(grep...)` → key loaded (51 chars)
Step 4: Terminal curl → 200 OK ✅
Step 5: execute_code with same hardcoded key → 401 (sandbox truncation)
Root cause: Two layers of isolation — (a) shell env not inherited by
    subprocess, (b) execute_code sandbox modifies hardcoded strings
Fix: For ad-hoc calls, use terminal() with explicit curl + env var
- Limit resets after 60 seconds
- HTTP 429 with clear upgrade message
- 21 sequential requests succeeded; 22nd triggered rate limit

## Debugging Session Notes (2026-06-11)

### Issue Chain

1. Created profiles for all 5 Agnes AI models
2. Profile `shanli-agnes2.0flash` failed to dispatch — "Invalid profile name. Must match [a-z0-9][a-z0-9_-]{0,63}" — **dots (`.`) are NOT valid in profile names!**
3. Profile naming rule: only `[a-z0-9][a-z0-9_-]{0,63}` — no dots, no Chinese, no uppercase
4. All profiles had `AGNES_API_KEY` with correct key in `.env`
5. `delegate_task` repeatedly failed with HTTP 401 — "无效的令牌"
6. `execute_code` with hardcoded key also failed with HTTP 401
7. Terminal `curl` with `export AGNES_API_KEY=...` succeeded with HTTP 200
8. Root cause: subprocesses (`delegate_task`, `execute_code`) don't inherit shell `export` vars

### Key Takeaway

Never trust `execute_code` or `delegate_task` to read API keys. Only `terminal()` with explicit `export` + `curl` reliably passes credentials. For kanban tasks, copy keys to profile `.env` files.
