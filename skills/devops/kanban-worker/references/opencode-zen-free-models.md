# OpenCode Zen 免费模型配置指南

## 概述

OpenCode Zen 是 OpenCode 团队提供的精选模型服务，包含多个免费模型可用于 Kanban 任务执行。

## 免费模型列表（2026-06-08）

| 模型 | Model ID | 上下文 | 推荐用途 |
|------|----------|:------:|----------|
| MiMo-V2.5 Free | `mimo-v2.5-free` | 1M | 写作/编码 |
| DeepSeek V4 Flash Free | `deepseek-v4-flash-free` | 1M | 日常任务/审核 |
| Nemotron 3 Ultra Free | `nemotron-3-ultra-free` | 1M | 深度推理 |
| Nemotron 3 Super Free | `nemotron-3-super-free` | 1M | 深度推理 |
| MiniMax M3 Free | `minimax-m3-free` | 1.05M | 多模态任务 |
| Qwen3.6 Plus Free | `qwen3.6-plus-free` | 262K | 通用任务 |
| Big Pickle | `big-pickle` | - | 隐身模型 |

## API 端点

```
https://opencode.ai/zen/v1/chat/completions
```

OpenAI 兼容格式，支持所有免费模型。

## Profile 配置示例

```yaml
model:
  provider: opencode
  default: mimo-v2.5-free
providers:
  opencode:
    name: OpenCode Zen
    key_env: OPENROUTER_API_KEY
    api_mode: chat_completions
    base_url: https://opencode.ai/zen/v1
    default_model: mimo-v2.5-free
    models:
    - mimo-v2.5-free
toolsets:
- hermes-cli
agent:
  max_turns: 90
```

## 已创建的 Profiles

| Profile 名称 | 模型 | 路径 |
|-------------|------|------|
| `mimo-free` | MiMo-V2.5 Free | `~/.hermes/profiles/mimo-free/` |
| `deepseek-free` | DeepSeek V4 Flash Free | `~/.hermes/profiles/deepseek-free/` |
| `nemotron-ultra-free` | Nemotron 3 Ultra Free | `~/.hermes/profiles/nemotron-ultra-free/` |
| `nemotron-super-free` | Nemotron 3 Super Free | `~/.hermes/profiles/nemotron-super-free/` |
| `minimax-m3-free` | MiniMax M3 Free | `~/.hermes/profiles/minimax-m3-free/` |
| `qwen-free` | Qwen3.6 Plus Free | `~/.hermes/profiles/qwen-free/` |

## 使用方式

```bash
# 切换到免费模型 profile
hermes profile use mimo-free

# 或在看板任务中指定
hermes kanban create "任务名称" --assignee mimo-free
```

## 注意事项

1. 免费模型为限时免费，无明确额度限制
2. API Key 使用 `OPENROUTER_API_KEY`（与 OpenRouter 共用）
3. 上下文长度：大部分为 1M，Qwen 为 262K
4. 适合用于轻量级 Kanban 任务、审核、日常操作
5. 与闪莉（shanli）profile 的动态选模机制配合使用时，可作为免费模型池的补充
