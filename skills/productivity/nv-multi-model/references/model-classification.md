# 模型分类与分组（完整清单）

> 数据来源：2026-05-17 NVIDIA NIM 实测
> 基准：小莉 = 4B / 80K 上下文

---

## 一、🐣 闪莉mimi（小莉替补）— 15 个

**条件**：< 4B 或 <10B + 响应<5s
**用途**：小莉忙时顶替，高峰期首选
**兜底**：→ 🏠 小莉（本地）

### A组（整点 ping）— 8 个

| 模型 | 参数量 | 延迟 | 特长 |
|------|:------:|:----:|------|
| `meta/llama-3.2-1b-instruct` | 1B | 722ms | 极简问答 |
| `google/gemma-2-2b-it` | 2B | 781ms | 轻量聊天 |
| `nvidia/ising-calibration-1-35b-a3b` | 1.35B | 882ms | 简单推理 |
| `nvidia/nemotron-mini-4b-instruct` | 4B | 894ms | 通用轻量 |
| `nvidia/riva-translate-4b-instruct-v1.1` | 4B | 770ms | 翻译专用 |
| `nvidia/nemotron-content-safety-reasoning-4b` | 4B | 854ms | 安全审核 |
| `nvidia/llama-3.1-nemotron-nano-8b-v1` | 8B | 813ms | 通用文本 |
| `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | 8B | 923ms | 🖼️ 基础视觉 |

### B组（半点 ping）— 7 个

| 模型 | 参数量 | 延迟 | 特长 |
|------|:------:|:----:|------|
| `meta/llama-3.2-3b-instruct` | 3B | 1283ms | 轻量聊天 |
| `google/gemma-3n-e2b-it` | ~2B | 1257ms | 轻量聊天 |
| `google/gemma-3n-e4b-it` | ~4B | 1266ms | 轻量聊天 |
| `nvidia/gliner-pii` | ？ | 776ms | 🔍 实体提取 |
| `nvidia/llama-3.1-nemoguard-8b-content-safety` | 8B | 1238ms | 🛡️ 内容安全 |
| `nvidia/llama-3.1-nemoguard-8b-topic-control` | 8B | 1121ms | 🛡️ 话题控制 |
| `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | 8B | 1252ms | 🛡️ 安全检测 |

---

## 二、🚀 轻量模型（闪莉日常主力）— 20 个

**条件**：> 4B 且响应 < 5s
**用途**：闪莉日常对话、搜索、看图
**兜底**：→ deepseek-v4-flash

### A组（整点 ping）— 10 个

| 模型 | 延迟 | 特长 |
|------|:----:|------|
| `mistralai/ministral-14b-instruct-2512` | 795ms | 💬 聊天最快 |
| `meta/llama-3.2-11b-vision-instruct` | 832ms | 🖼️ **图片理解首选** |
| `mistralai/mistral-nemotron` | 912ms | 💬 聊天 |
| `meta/llama-4-maverick-17b-128e-instruct` | 932ms | 💬 **日常默认** |
| `mistralai/mixtral-8x22b-instruct-v0.1` | 912ms | 💬 聊天 |
| `nvidia/nemotron-nano-12b-v2-vl` | 923ms | 🖼️ 视觉备选 |
| `nvidia/nemotron-3-super-120b-a12b` | 1295ms | 🧠 深度推理 |
| `meta/llama-guard-4-12b` | 746ms | 🛡️ 安全过滤 |
| `mistralai/mixtral-8x7b-instruct-v0.1` | 1152ms | 💬 聊天 |
| `nvidia/nemotron-3-content-safety` | 1194ms | 🛡️ 安全审核 |

### B组（半点 ping）— 10 个

| 模型 | 延迟 | 特长 |
|------|:----:|------|
| `qwen/qwen3-next-80b-a3b-thinking` | 830ms | 🧠 快速推理思考 |
| `mistralai/mistral-small-4-119b-2603` | 867ms | 💬 聊天 |
| `meta/llama-3.3-70b-instruct` | 947ms | 💬 **强聊天** |
| `moonshotai/kimi-k2.6` | 1033ms | 🖼️ **多模态** |
| `upstage/solar-10.7b-instruct` | 1025ms | 💬 聊天 |
| `sarvamai/sarvam-m` | 1037ms | 💬 聊天 |
| `stockmark/stockmark-2-100b-instruct` | 1088ms | 💬 聊天 |
| `nvidia/llama-3.3-nemotron-super-49b-v1` | 1163ms | 💬 中等复杂 |
| `qwen/qwen3-next-80b-a3b-instruct` | 3484ms | 🧠 深度推理 |
| `abacusai/dracarys-llama-3.1-70b-instruct` | 4817ms | 🧠 深度兜底 |

---

## 三、🧠 强模型（深度任务）— 4 个

已含于轻量组，单独列出便于深度任务时优先调用。

| 组 | 模型 | 延迟 | 用途 |
|:-:|------|:----:|------|
| A | `nvidia/nemotron-3-super-120b-a12b` | 1295ms | 重推理、长文本 |
| A | `meta/llama-4-maverick-17b-128e` | 932ms | 深度MoE推理 |
| B | `qwen/qwen3-next-80b-a3b-instruct` | 3484ms | 复杂推理 |
| B | `abacusai/dracarys-llama-3.1-70b-instruct` | 4817ms | 深度兜底 |

---

## 四、Ping 时间轴

```
00:00 ── A组（8 mimi + 10 轻量 = 18 个）
00:30 ── B组（7 mimi + 10 轻量 = 17 个）
01:00 ── A组
01:30 ── B组
...每半小时交替...
每个模型 1 小时 ping 一次 ✅
每 30 分钟都有新数据 ✅
```

## 五、竞速排名评分公式

```python
score = avg_ms × 0.6 + last_ms × 0.4 + std_ms × 0.2
```

评分越低越好。选评分最低的 3 个并发竞速。波动大的模型因 std_ms 高而被惩罚。
