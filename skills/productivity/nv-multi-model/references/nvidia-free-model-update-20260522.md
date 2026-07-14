# NVIDIA NIM 免费模型更新（2026-05-22）

## 背景

按照 OpenRouter 同样的规则（只保留免费+工具调用模型），对 NVIDIA NIM API 的模型配置进行了更新。

## 移除的付费模型

| 模型 | 费用 | 原因 |
|------|:----:|------|
| `nvidia/nemotron-3-super-120b-a12b` | $0.2/$0.8 per M tokens | 付费（OpenRouter 上有 `:free` 版保留） |
| `deepseek-ai/deepseek-v4-pro` | $1.74/$3.48 per M tokens | 付费 |
| `deepseek-ai/deepseek-v4-flash` | $0.14/$0.28 per M tokens | 付费（OpenRouter 上有 `:free` 版保留） |

## 新增的 27 个免费模型

### ⚡ mimi 分类（+3）

| 模型 | 说明 |
|------|------|
| `meta/llama-3.1-8b-instruct` | 8B 轻量 |
| `microsoft/phi-4-mini-instruct` | 微软小模型 |
| `mistralai/mistral-7b-instruct-v03` | 7B 轻量 |

### 🚀 light 分类（+13）

| 模型 | 说明 |
|------|------|
| `bytedance/seed-oss-36b-instruct` | 字节 36B |
| `google/gemma-3-27b-it` | Gemma 3 27B |
| `google/gemma-4-31b-it` | Gemma 4 31B |
| `meta/llama-3.1-70b-instruct` | Llama 70B |
| `minimaxai/minimax-m2.5` | MiniMax M2.5 |
| `moonshotai/kimi-k2-instruct` | Kimi K2 |
| `nvidia/llama-3_3-nemotron-super-49b-v1_5` | Nemotron Super 49B v1.5 |
| `nvidia/nemotron-3-nano-30b-a3b` | Nemotron Nano 30B |
| `openai/gpt-oss-20b` | GPT-OSS 20B |
| `qwen/qwen2.5-coder-32b-instruct` | Qwen 编码 32B |
| `qwen/qwen3.5-122b-a10b` | Qwen 3.5 122B |
| `stepfun-ai/step-3.5-flash` | Step 3.5 Flash |
| `z-ai/glm4.7` | GLM 4.7 |

### 🧠 deep 分类（+11）

| 模型 | 说明 |
|------|------|
| `deepseek-ai/deepseek-v3.1-terminus` | DeepSeek V3.1 |
| `deepseek-ai/deepseek-v3.2` | DeepSeek V3.2 |
| `minimaxai/minimax-m2.7` | MiniMax M2.7 |
| `mistralai/devstral-2-123b-instruct-2512` | Devstral 2 123B |
| `mistralai/mistral-large-3-675b-instruct-2512` | Mistral Large 3 675B |
| `moonshotai/kimi-k2-instruct-0905` | Kimi K2 0905 |
| `moonshotai/kimi-k2-thinking` | Kimi K2 Thinking |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Nemotron Omni Reasoning |
| `qwen/qwen3-coder-480b-a35b-instruct` | Qwen 编码 480B |
| `qwen/qwen3.5-397b-a17b` | Qwen 3.5 397B |
| `z-ai/glm-5.1` | GLM 5.1 |

## Groups A/B 蛇形分配

| 组 | NVIDIA | Google | OpenRouter | 总计 |
|:-:|:------:|:------:|:----------:|:----:|
| **A** | 25 | 4 | 9 | **38** |
| **B** | 27 | 2 | 8 | **37** |

## 关键教训

1. **子代理写入时丢失 provider 格式** — 大莉将模型写为纯字符串，丢失了 Google/OpenRouter 的 provider 标记。修复后需人工校验格式。
2. **每模型只放一个分类** — 冰哥明确要求不跨分类重叠。
3. **大莉审核前置** — 写入前先让 Pro 模型审核方案。
4. **工作规范同步** — 所有配置变更后同步更新 `莉莉丝的工作规范.md`。
