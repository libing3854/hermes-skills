# Vision Provider 路由诊断

## 症状

`browser_vision` 报错：
```
Gemini HTTP 400 (INVALID_ARGUMENT): * GenerateContentRequest.model: unexpected model name format
```

或 vision_analyze 返回空结果。

## 根因

`auxiliary.vision.provider` 设置为 `auto` 时，Hermes 会尝试用 main provider 处理 vision 任务。如果 main provider 不是多模态模型（如 deepseek-v4-flash），API 会拒绝图片输入。

## 诊断步骤

```bash
# 1. 检查当前 main provider 和 model
python3 -c "
from agent.auxiliary_client import _read_main_provider, _read_main_model
print('Provider:', _read_main_provider())
print('Model:', _read_main_model())
"

# 2. 检查 vision 会路由到哪个 provider
python3 -c "
from agent.auxiliary_client import resolve_vision_provider_client
p, c, m = resolve_vision_provider_client(provider='auto', async_mode=False)
print('Vision →', p, m, 'available:', c is not None)
"
```

## 修复方案

### 方案 A：指定多模态 provider（推荐）

在 `~/.hermes/config.yaml` 中：
```yaml
auxiliary:
  vision:
    provider: longcat
    model: LongCat-2.0-Preview
```

### 方案 B：改用 OpenRouter 的多模态模型

```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-3-flash-preview
```

### 方案 C：切换 main provider 为多模态模型

```bash
hermes model set longcat/LongCat-2.0-Preview
```

## 常见 provider 的多模态支持

| Provider | 多模态 | 默认模型 | 备注 |
|----------|--------|----------|------|
| longcat | ✅ | LongCat-2.0-Preview | 原生多模态 |
| openrouter | ✅ | gemini-3-flash-preview | 自动选择 |
| deepseek | ❌ | deepseek-v4-flash | 不支持图片输入 |
| anthropic | ✅ | claude-sonic-4 | 需确认 |

## 验证修复

1. 重启 gateway 使配置生效
2. 在 agent 中调用 browser_navigate 然后 browser_vision 测试
