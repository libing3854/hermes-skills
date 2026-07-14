# NV模型Kanban兼容性测试报告

**日期**: 2026-06-26
**测试目的**: 验证NV免费大模型是否能在Hermes kanban worker中正常执行任务

## 测试结论

**仅 qwen/qwen3.5-122b-a10b 成功执行kanban任务。** 916ms响应，44秒完成简单任务。

## 小模型测试结果

| 模型 | 简单对话 | kanban |
|------|:---:|:---:|
| llama-4-maverick-128k | ✅ | ❌ 调用browser_back |
| mistral-nemotron | ✅ | ❌ 输出乱码 |
| ministral-14b | ✅ "通过" | ❌ 卡住 |
| solar-10.7b | ❌ 误解 | N/A |

## 大模型测试结果

| 模型ID | 速度 | kanban |
|------|:---:|:---:|
| qwen/qwen3.5-122b-a10b | 916ms | ✅ 成功 |
| deepseek-ai/deepseek-v4-flash | 995ms | 未测(1M) |
| deepseek-ai/deepseek-v4-pro | 1101ms | 未测(1M) |
| z-ai/glm-5.1 | 19831ms | 太慢 |
| others | 404/超时 | 不可用 |

## 模型ID修正

| 错误 | 正确 |
|------|------|
| minimax/M2.7 | minimaxai/minimax-m2.7 |
| z-ai/glm-5.2 | z-ai/glm-5.1 |
| nvidia/nemotron-3-ultra | nvidia/nemotron-3-ultra-550b-a55b |
| qwen3-coder-480b | qwen/qwen3.5-122b-a10b |

## nvlinshi配置要点

1. SOUL.md: 闪莉风格（简短执行者）
2. task_completion_guidance: null
3. kanban profiles含nvlinshi
4. 当前仅qwen3.5可用
