# 真实示例：model-selector 插件

创建日期：2026-05-26
最后更新：2026-05-26（添加 tool 注册）

## 背景

冰哥需要将 `model_selector.py`（智能模型选择脚本）封装为 Hermes 插件，提供 `/pin`、`/unpin`、`/model-status` slash 命令 + `model_select` 工具（Agent 自动调用）。

## 目录结构

```
~/.hermes/plugins/model-selector/
├── plugin.yaml          # 元数据：名称、版本、命令+工具声明
└── __init__.py          # 插件入口：subprocess 调用外部脚本 + register(ctx)
```

外部逻辑脚本（不放在插件目录下，独立维护）：
```
~/.hermes/scripts/model_selector.py  # 核心逻辑
```

## 关键设计决策

### 1. subprocess 调用 vs 直接 import

选择 subprocess 调用的原因：
- `model_selector.py` 本身有完整的 CLI 接口（argparse）
- 可以独立测试、独立调试
- 插件保持轻量（__init__.py 约 220 行）
- 未来更新脚本无需修改插件

### 2. 命令分发模式

```python
_COMMANDS = {
    "pin": {"handler": _handle_pin, "description": "..."},
    "unpin": {"handler": _handle_unpin, "description": "..."},
}

def _handle_slash(cmd, raw_args, **ctx):
    entry = _COMMANDS.get(cmd)
    return entry["handler"](raw_args, **ctx)

def register(ctx):
    for cmd, info in _COMMANDS.items():
        ctx.register_command(cmd, handler=lambda raw, c=cmd: _handle_slash(c, raw), ...)
```

### 3. 工具注册（v2 新增）

Agent 在推理时自动调用 model_select 工具，无需用户输入。

Schema 定义：
```python
_MODEL_SELECT_SCHEMA = {
    "name": "model_select",
    "description": "⚡ 智能选择最适合当前任务的模型",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "任务描述"},
            "session_id": {"type": "string", "description": "会话 ID"},
            "hint_category": {"type": "string", "enum": ["mimi", "light", "deep"]},
        },
        "required": ["task"],
    },
}
```

Handler 返回字符串（Agent 会读取并用作推理上下文）：
```python
def _handle_model_select(task="", session_id="", hint_category="") -> str:
    args = ["--task", task, "--session", session_id or "default"]
    if hint_category:
        args += ["--category", hint_category]
    result = _call_selector(*args)
    if "error" in result:
        return f"选模失败: {result['error']}"
    return f"⚡ 推荐: `{result.get('model','?')}` | {result.get('category','?')}/{result.get('provider','?')}"
```

注册时注意**不要用 lambda 闭包**（register 中直接传 handler）：
```python
def register(ctx) -> None:
    ctx.register_tool(
        name="model_select",
        toolset="model_select",
        schema=_MODEL_SELECT_SCHEMA,
        handler=_handle_model_select,
        emoji="⚡",
    )
```

plugin.yaml 中声明：
```yaml
provides_tools:
  - model_select
```

### 4. 中文命令名

支持中文作为 slash 命令名：
```python
"闪莉": {"handler": _handle_model_status, "description": "查看闪莉当前选模状态"}
```

用户直接输入 `/闪莉` 即可触发。

### 5. 输出格式

slash 命令返回字符串文本给用户，推荐：
- `✅ / ❌` 开头表示成功/失败
- **markdown** 加粗显示关键词
- `` 反引号显示代码/模型名

## 安装步骤

```yaml
# config.yaml
plugins:
  enabled:
    - disk-cleanup
    - model-selector
```

```bash
# 验证
hermes plugins list  # 应看到 model-selector enabled
# 重启 Hermes 后生效
```

## 插件命令/工具

| 方式 | 名称 | 参数 | 功能 |
|:----|:----|:-----|:-----|
| 🔧 Tool | `model_select` | task, session_id, hint_category | Agent 自动选模 |
| 💬 Cmd | `/pin` | mimi/light/deep/vision | 固定模型分类 |
| 💬 Cmd | `/pin` | （无参） | 固定当前 session |
| 💬 Cmd | `/unpin` | — | 解除固定 |
| 💬 Cmd | `/model-status` | session名（可选） | 查看选模状态 |
| 💬 Cmd | `/闪莉` | — | 查看闪莉状态 |
