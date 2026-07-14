# LLM7.io 实测报告

> 测试日期: 2026-06-10
> 测试环境: macOS, 浏览器自动化 + curl

## 概述

LLM7.io 是目前发现的唯一**完全免费、无需注册、无需API Key**的OpenAI兼容LLM API。

- Base URL: `https://api.llm7.io/v1`
- 兼容格式: OpenAI SDK
- 注册要求: 无
- API Key要求: 无
- 信用卡要求: 无

## 可用模型 (2026-06-10)

| 模型ID | 类型 | 上下文窗口 | tools_calling |
|--------|------|-----------|---------------|
| qwen3-235b | Free | 240K | ✅ |
| mistral-small-3.2 | Free | - | - |
| codestral-latest | Free | 32K | - |
| devstral-small-2:24b | Free | - | - |
| kimi-k2.6 | Pro | 240K | ✅ |
| minimax-m2.7 | Pro | 180K | ✅ |
| GLM-4.6V-Flash | Pro | - | - |
| deepseek-v4-flash | Pro | - | - |
| deepseek-v3.1:671b-terminus | Pro | - | - |

## 延迟测试 (每模型3次取平均)

| 模型 | 平均延迟 | 最低 | 最高 |
|------|----------|------|------|
| Qwen3-235B (Free) | 3753ms | 2085ms | 5421ms |
| Mistral Small (Free) | 1173ms | 1054ms | 1241ms |
| Codestral (Free) | 1018ms | 936ms | 1154ms |
| Devstral Small (Free) | 1121ms | 1121ms | 1121ms |

### 对比 NVIDIA NIM

| 平台 | 典型延迟 |
|------|----------|
| LLM7.io (免费) | 1000-4000ms |
| NVIDIA NIM | 200-500ms |

**结论**: LLM7.io 比 NV 慢 2-7 倍，但完全免费且无需注册。

## API调用示例

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.llm7.io/v1",
    api_key="not-needed"  # 任意值即可
)

response = client.chat.completions.create(
    model="qwen3-235b",
    messages=[{"role": "user", "content": "What is 2+2?"}],
    max_tokens=10
)
print(response.choices[0].message.content)  # "4"
```

### curl

```bash
curl -X POST "https://api.llm7.io/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-235b",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 20
  }'
```

## 已知限制

1. **延迟较高**: 免费模型 1-4秒，不适合实时交互
2. **Pro模型可能需付费**: deepseek-v4-flash 等返回 402 Payment Required
3. **无官方文档**: API行为可能变化
4. **Rate Limit**: 未明确公布，但实测未遇到限流

## 适用场景

- ✅ 批量处理任务（不急的）
- ✅ 备用API（NV不可用时）
- ✅ 开发测试
- ❌ 实时对话（太慢）
- ❌ 生产环境（无SLA保证）
