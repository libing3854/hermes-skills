# 模型列表更新（2026-06-22）

## 背景

NVIDIA NIM 端点大面积返回 404/410，groups.json 被 nv_daily_eval.py 清空，导致 ping 死循环。

## 移除的模型（HTTP 404/410）

| 模型 | 状态 | 原因 |
|------|------|------|
| deepseek-ai/deepseek-v3.1-terminus | 404 | 已下线 |
| deepseek-ai/deepseek-v3.2 | 404 | 已下线 |
| moonshotai/kimi-k2-thinking | 410 | 已废弃 |
| moonshotai/kimi-k2-instruct-0905 | 404 | 已下线 |
| qwen/qwen3-coder-480b-a35b-instruct | 410 | 已废弃 |
| mistralai/devstral-2-123b-instruct-2512 | 404 | 已下线 |
| nvidia/nemotron-nano-3-30b-a3b | 404 | 已下线 |
| nvidia/nvidia-nemotron-nano-9b-v2 | 404 | 已下线 |
| 01-ai/yi-large | 404 | 已下线 |
| writer/palmyra-creative-122b | 404 | 已下线 |
| baidu/cobuddy:free (OR) | 404 | 已下线 |

## 新增的可用模型

| 模型 | Provider | 说明 |
|------|----------|------|
| deepseek-ai/deepseek-v4-flash | NV | 新版 Flash |
| deepseek-ai/deepseek-v4-pro | NV | 新版 Pro |
| moonshotai/kimi-k2.6 | NV | Kimi 最新 |
| minimaxai/minimax-m3 | NV | MiniMax M3 |
| stepfun-ai/step-3.7-flash | NV | Step 新版 |
| nvidia/nemotron-3-ultra-550b-a55b | NV | 550B 超大 |
| nvidia/nemotron-4-340b-instruct | NV | 340B |
| openai/gpt-oss-120b | NV | GPT-OSS 大杯 |
| openai/gpt-oss-20b | NV | GPT-OSS 小杯 |

## 更新 groups.json 的流程

1. 查询 NVIDIA NIM 可用模型：`curl -s https://integrate.api.nvidia.com/v1/models -H "Authorization: Bearer $KEY"`
2. 查询 OpenRouter 免费模型：`curl -s https://openrouter.ai/api/v1/models | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data'] if m.get('pricing',{}).get('prompt','1')=='0']"`
3. 按 mimi/light/deep/vision 分类
4. 写入 groups.json，更新 `updated_at` 和 `effective_from`
5. 运行 `python3 nv_ping.py` 验证
6. 检查 `nv_daily_eval.py` 不会在空结果时覆盖 groups

## 教训

- groups.json 的 `groups.A/B` 和 `categories` 是两个独立字段，eval 脚本只写 groups，ping 脚本 fallback 到 categories
- 模型下线是常态，每月检查一次可用模型列表
- Google Gemini 在 cron 环境中容易触发 429 限流，不建议放入 ping 列表
