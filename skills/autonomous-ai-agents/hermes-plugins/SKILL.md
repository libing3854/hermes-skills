---
name: hermes-plugins
description: Full lifecycle of Hermes Agent plugins — authoring custom plugins (slash commands, tools, hooks), security review of third-party plugins, and adoption workflow (discovery, design extraction, review loop).
version: 1.0.0
author: Lily (莉莉丝)
tags: [hermes, plugins, authoring, security, review, adoption, development]
related_skills: [hermes-agent-skill-authoring]
---

# Hermes Plugins

Comprehensive guide covering the full lifecycle of Hermes Agent plugins: **authoring** your own, **reviewing** third-party ones, and **adopting** design patterns from the community.

> **What's the difference between a plugin and a skill?**
> - **Plugins** = Python code registered into the Hermes runtime (slash commands, tools, hooks)
> - **Skills** = knowledge/workflow files loaded into the prompt
> - This skill covers the **plugin** side.

---

## Section A: Authoring Plugins

Creating plugins that extend Hermes with slash commands, tools, and event hooks.

### Plugin Directory Structure

```
~/.hermes/plugins/<plugin-name>/
├── plugin.yaml          # Metadata declaration (REQUIRED)
└── __init__.py          # Entry point + register(ctx) (REQUIRED)
```

Optional support files:
- `tools.py` — Tool schemas and handlers
- `utils.py` — Utility functions
- `references/` — Documentation

### plugin.yaml Template

```yaml
name: my-plugin
version: 1.0.0
description: "Brief description shown in hermes plugins list"
author: "Author Name"
# Optional fields:
# kind: backend          # Auto-load without user enabling
# hooks:
#   - post_tool_call
#   - on_session_end
# commands:
#   - my-command
#   - 闪莉               # Chinese names supported
# provides_tools:
#   - my_tool
# requires_env:
#   - MY_API_KEY
```

### register() Entry Point

```python
def register(ctx) -> None:
    """Called by Hermes plugin manager at startup"""
    # Register slash commands
    ctx.register_command("command-name",
        handler=my_handler,
        description="Command description",
    )
    # Register hooks
    ctx.register_hook("post_tool_call", on_tool_call)
    # Register tools (agent auto-calls them)
    ctx.register_tool(name="my_tool", toolset="my_tools",
        schema=MY_SCHEMA, handler=my_handler, emoji="⚡")
```

### Slash Command Handler Signature

```python
def my_handler(
    raw_args: str,                # Raw text after command name
    task_id: str = "",
    session_id: str = "",
    **ctx,                        # Other context
) -> Optional[str]:               # Return text reply; None = no output
```

### Tool (Agent-Called) Handler Signature

```python
# ⚠️ CRITICAL: First param must be params: dict, NOT individual args
def my_tool_handler(params: dict, **kwargs) -> str:
    """Dispatch calls entry.handler(args, **kwargs)
    where args is the ENTIRE params dict"""
    task = params.get("task", "")
    session_id = params.get("session_id", "")
    ...
```

> **Trap**: Writing `def handler(task: str, session_id: str = "")` means `task` receives the entire dict object, not a string. Always use `params: dict` as the first parameter and unpack with `.get()`.

### Tool Schema Definition

```python
_MY_SCHEMA = {
    "name": "my_tool",
    "description": "What the tool does — agent reads this to decide when to call",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": "Description of the parameter",
            },
        },
        "required": ["task"],
    },
}
```

### External Script Calling Pattern

For existing standalone scripts, call via subprocess rather than duplicating code:

```python
def _call_script(script_path: str, *args: str, timeout: int = 10) -> dict:
    try:
        result = subprocess.run(
            [sys.executable, script_path] + list(args),
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip() or f"exit {result.returncode}"}
        return json.loads(result.stdout.strip())
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except json.JSONDecodeError:
        return {"error": f"parse failed: {result.stdout[:200]}"}
```

### Tool vs Slash Command Comparison

| Method | Trigger | User Awareness | Best For |
|:-------|:--------|:--------------:|:---------|
| **Tool** | Agent auto-calls | 🟢 Invisible | Model selection, auto-optimization, background analysis |
| **Slash cmd** | User types `/cmd` | 🟡 Visible | Manual control, status queries, config changes |
| **Hooks** | Event-triggered | 🟢 Invisible | Auto-cleanup, logging, monitoring |

### Plugin Activation

```bash
# Add to config.yaml
plugins:
  enabled:
    - my-plugin

# Verify
hermes plugins list

# Restart Hermes or /reset to reload
```

### ⚠️ Authoring Pitfalls

1. **Tool handler signature mismatch**: First param must be `params: dict`, not individual args. Always add `**kwargs` to absorb framework extras (`task_id`, etc.).
2. **Forgetting to restart**: Plugin code loads at Hermes startup. Modify `__init__.py` → must `/reset` or restart.
3. **Concurrent config writes**: Plugins that modify `config.yaml` delegation section (e.g. `delegate-duo`) are not concurrent-safe — fine for single-threaded CLI, risky with kanban workers.
4. **`delegate_task` model param is PIN not SWITCH**: Passing `model` in `delegate_task()` does NOT route the subagent to a different provider. The subagent always inherits the parent session's model. Use `delegate-duo` plugin or kanban profiles to switch models.

---

## Section B: Security Review (五维度审查)

**Core rule**: Never install a third-party plugin without completing this 5-dimension review. This is the user's security baseline.

### 5 Dimensions

| Dimension | What to Check | Rating |
|-----------|--------------|:------:|
| ① **Source** | Author reputation, stars, commit history, community recognition | 🟢🟡🔴 |
| ② **Code** | File-by-file: backdoors, data exfiltration, command injection, core file modification | 🟢🟡🔴 |
| ③ **Dependencies** | Third-party pip packages, supply chain risk, Hermes internal deps | 🟢🟡🔴 |
| ④ **License** | MIT/Apache/AGPL/GPL — personal vs commercial restrictions | 🟢🟡🔴 |
| ⑤ **Permissions** | File I/O, network, process management, launcher replacement, sudo | 🟢🟡🔴 |

### Review Process

```bash
# Clone to temp dir
cd /tmp && git clone --depth 1 <repo-url>

# Check directory structure
ls -la && find . -name "*.py" | head -20

# Read core files
cat plugin.yaml; cat __init__.py; cat install.py

# Check for dangerous patterns
grep -rn "eval\|exec\|os.system\|subprocess\|requests.post\|urllib.request" *.py

# Check dependencies
grep -rn "import\|from" *.py | grep -v "os\|sys\|json\|re\|pathlib\|datetime"
```

### 🔴 Danger Signals

- Modifies Hermes core files (cli.py, commands.py)
- Replaces `~/.local/bin/hermes` launcher
- Auto-update mechanism (remote code fetch)
- README and LICENSE file inconsistency
- Hardcoded remote addresses or donation wallets

### Known Security Patterns

| Pattern | Risk | Example |
|:--------|:----:|:--------|
| **model-router** 🟡 | Modifies core files + replaces launcher | open-world-project/model-router |
| **evey-plugins** 🟡 | AGPL license conflict, zero external deps | 42-evey/hermes-plugins |
| **Built-in plugins** 🟢 | Bundled with Hermes, zero risk | disk-cleanup, spotify |

### Conclusion Format

```
安装建议：🟢 推荐 / 🟡 谨慎推荐 / 🔴 不推荐
理由：...
```

### Post-Review Actions

| Decision | Action |
|:---------|:-------|
| 🟢 **Install** | Standard installation |
| 🟡 **Extract design** | Read code for patterns, implement with attribution (see Section C) |
| 🔴 **Reject** | Document reasons, block installation |

---

## Section C: Adoption Workflow (Design Extraction)

When a third-party plugin is useful but too invasive to install directly, extract its design patterns for adapted implementation.

### Step 1 — Discovery Sources

| Priority | Source | Query Pattern |
|:--------:|--------|---------------|
| 1 | `hermes plugins list` | Built-in and already enabled |
| 2 | GitHub high-star | `hermes-agent plugin stars:>50` |
| 3 | Skills Hub | `hermes skills browse` / `hermes skills search <keyword>` |
| 4 | Community maps | hermesatlas.com, get-hermes.ai/community |
| 5 | Official repo | NousResearch/hermes-agent/plugins/ |

### Step 2 — Design Extraction

Focus on reading code for patterns:

| Pattern | What to Look For |
|:--------|:-----------------|
| 🧠 **Algorithm** | Core logic, decision rules, state management |
| 🧠 **Error handling** | Fallback chains, degradation strategies, timeouts |
| 🧠 **Configuration** | YAML structure, deep merge, multi-profile support |
| 🧠 **Safety** | Backup mechanisms, validation, permission checks |

### Step 3 — Implementation with Attribution

```python
"""
Design source:
  Referenced <upstream-repo> (<license>):
  - 🧠 #1 Classifier: see function/line
  - 🧠 #2 Fast-path: see function/line

  Upstream repo: <URL>
  Review date: <YYYY-MM-DD>
"""
```

### Step 4 — Review Loop (大莉审查)

Standard workflow: Lily writes → 大莉 reviews → Lily fixes → 大莉 re-reviews → Approved

### Output Ranked by Priority

| Priority | Description |
|:--------:|:------------|
| 🔴 High | User experience leap, cost savings, fault tolerance |
| 🟡 Medium | Configuration flexibility, safety backups |
| 🟢 Low | UI improvements, visual hints, nice-to-haves |

---

## Section D: Image Gen Backend Plugins

Backend plugins that provide image generation providers for the `image_generate` tool. Different from tool/command plugins — these implement `ImageGenProvider` ABC and register via `ctx.register_image_gen_provider()`.

### Directory Structure

```
~/.hermes/plugins/image_gen/<name>/
├── plugin.yaml          # kind: backend, requires_env for API key
└── __init__.py          # ImageGenProvider subclass + register(ctx)
```

### plugin.yaml Template

```yaml
name: agnes
version: 1.0.0
description: "Agnes AI image generation backend"
author: "Author Name"
kind: backend                    # CRITICAL: must be 'backend' for auto-loading
requires_env:
  - AGNES_API_KEY
```

### __init__.py Pattern

```python
from agent.image_gen_provider import (
    DEFAULT_ASPECT_RATIO, ImageGenProvider,
    error_response, resolve_aspect_ratio,
    save_b64_image, save_url_image, success_response,
)

class MyImageGenProvider(ImageGenProvider):
    @property
    def name(self) -> str: return "my-provider"

    @property
    def display_name(self) -> str: return "My Provider"

    def is_available(self) -> bool:
        return bool(os.environ.get("MY_API_KEY"))

    def list_models(self) -> list:
        return [{"id": "model-1", "display": "Model 1", "speed": "fast", "strengths": "..."}]

    def default_model(self): return "model-1"

    def get_setup_schema(self) -> dict:
        return {"name": "My Provider", "badge": "free",
                "env_vars": [{"key": "MY_API_KEY", "prompt": "...", "url": "..."}]}

    def generate(self, prompt, aspect_ratio=DEFAULT_ASPECT_RATIO, **kwargs) -> dict:
        # 1. Validate prompt, check API key
        # 2. Call API (requests.post or SDK)
        # 3. Return success_response(image=path, model=id, prompt=prompt,
        #        aspect_ratio=aspect, provider=name) or error_response(...)

def register(ctx) -> None:
    ctx.register_image_gen_provider(MyImageGenProvider())
```

### Aspect Ratio to Size Mapping

```python
_SIZES = {
    "landscape": "1024x1024",  # or "1536x1024" for wide
    "square": "1024x1024",
    "portrait": "768x1024",    # or "1024x1536" for tall
}
```

### Response Helpers

- `save_url_image(url, prefix="provider")` — downloads URL image to `$HERMES_HOME/cache/images/`, returns Path
- `save_b64_image(b64_data, prefix="provider")` — decodes base64 image, returns Path
- `success_response(image=path_or_url, model=id, prompt=prompt, aspect_ratio=aspect, provider=name)`
- `error_response(error=msg, error_type=type, provider=name)`

### ⚠️ Image Gen Backend Pitfalls

1. **User plugins require `plugins.enabled`** — Unlike bundled backends (fal, openai, krea) which auto-load, user-installed backends in `~/.hermes/plugins/image_gen/` MUST be added to `plugins.enabled` in config.yaml:
   ```yaml
   plugins:
     enabled:
       - image_gen/agnes    # key = "image_gen/<name>"
   ```

2. **`config.yaml` must set `image_gen.provider`** — After enabling the plugin:
   ```bash
   hermes config set image_gen.provider agnes
   hermes config set image_gen.model agnes-image-2.0-flash
   ```

3. **URL vs b64 response** — Some APIs return image URLs (Agnes, xAI), others return b64_json (OpenAI). Handle both with fallback:
   ```python
   if b64:
       saved = save_b64_image(b64, prefix=f"agnes_{model_id}")
   elif url:
       saved = save_url_image(url, prefix=f"agnes_{model_id}")
   else:
       return error_response(error="No image data", ...)
   ```

4. **OpenAI-compatible image endpoints use `/v1/images/generations`** — NOT `/v1/chat/completions`. Custom providers configured for chat won't work for image gen. Must use dedicated image_gen plugin or direct API call.

5. **`os.environ` may not have API keys in tool processes** — The plugin's `generate()` runs inside the Hermes tool subprocess. If `load_hermes_dotenv()` hasn't populated `os.environ` before the tool call, `os.environ.get("MY_API_KEY")` returns `None` even though the key exists in `~/.hermes/.env`. **Fix**: Add a `_get_api_key()` helper with dual-path resolution:
   ```python
   def _get_api_key() -> Optional[str]:
       key = os.environ.get("AGNES_API_KEY")
       if key:
           return key
       try:
           from hermes_cli.config import get_env_value
           return get_env_value("AGNES_API_KEY")
       except Exception:
           return None
   ```
   Use this in both `is_available()` and `generate()`. Pattern applies to ANY plugin that reads API keys from `.env`.

### Existing Image Gen Backends

| Backend | Models | API Key | Notes |
|---------|--------|---------|-------|
| `fal` | flux-2-pro, flux-2-dev, etc. | `FAL_KEY` | Default bundled backend |
| `openai` | gpt-image-2 (low/medium/high) | `OPENAI_API_KEY` | Quality tiers |
| `openai-codex` | gpt-image-2 via Codex | `OPENAI_API_KEY` | Codex proxy |
| `krea` | krea-flux-2 | `KREA_API_KEY` | Krea AI |
| `xai` | grok-image-2 | `XAI_API_KEY` | xAI/Grok |
| `agnes` | agnes-image-2.0/2.1-flash | `AGNES_API_KEY` | Free, user plugin |

---

## Reference Files

- `references/tool-handler-signature-pitfalls.md` — Handler signature gotchas with dispatch calling convention
- `references/model-selector-plugin.md` — model-selector plugin design extraction case study
- `references/case-study-model-selector.md` — Adoption workflow case study: model-selector from discovery to implementation
- `references/42-evey-case-study.md` — Full 5-dimension security review of 23-plugin collection
- `references/model-router-case-study.md` — Security review + design extraction of core-modifying plugin
- `references/agnes-image-gen-plugin.md` — Agnes Image plugin: API spec, implementation details, testing notes
