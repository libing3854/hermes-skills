# NVIDIA NIM 当前可用模型清单

> 最后更新：2026-06-26
> 测试时间：00:47 ~ 01:00
> 可用：25个（已排除超时/502模型）

## 按延迟排序（Group A 实测，00:58）

| 排名 | 模型 | 延迟 | 分类 |
|------|------|------|------|
| 1 | nvidia/riva-translate-4b-instruct-v1.1 | 1299ms | mimi |
| 2 | google/gemma-2-2b-it | 1304ms | mimi |
| 3 | nvidia/nemotron-mini-4b-instruct | 1318ms | mimi |
| 4 | meta/llama-guard-4-12b | 1339ms | light |
| 5 | nvidia/llama-3.1-nemoguard-8b-content-safety | 1356ms | light |
| 6 | nvidia/llama-3.1-nemotron-safety-guard-8b-v3 | 1391ms | light |
| 7 | mistralai/mixtral-8x7b-instruct-v0.1 | 1787ms | deep |
| 8 | meta/llama-3.2-3b-instruct | 2222ms | mimi |
| 9 | google/gemma-3n-e2b-it | 2425ms | mimi |
| 10 | meta/llama-3.1-8b-instruct | 2628ms | light |
| 11 | mistralai/mistral-nemotron | 2634ms | light |
| 12 | meta/llama-3.3-70b-instruct | 12860ms | deep |

## 完整25个模型

### mimi（小模型，6个）
- nvidia/nemotron-mini-4b-instruct
- meta/llama-3.2-3b-instruct
- google/gemma-3n-e2b-it
- google/gemma-2-2b-it
- nvidia/gliner-pii
- nvidia/riva-translate-4b-instruct-v1.1

### light（日常模型，9个）
- meta/llama-3.1-8b-instruct
- mistralai/mistral-nemotron
- upstage/solar-10.7b-instruct
- meta/llama-guard-4-12b
- nvidia/llama-3.1-nemoguard-8b-content-safety
- nvidia/llama-3.1-nemoguard-8b-topic-control
- nvidia/llama-3.1-nemotron-safety-guard-8b-v3
- sarvamai/sarvam-m
- stockmark/stockmark-2-100b-instruct

### deep（大模型，8个）
- meta/llama-3.1-70b-instruct
- meta/llama-3.3-70b-instruct
- meta/llama-4-maverick-17b-128e-instruct
- mistralai/mistral-small-4-119b-2603
- nvidia/llama-3.3-nemotron-super-49b-v1
- mistralai/mixtral-8x7b-instruct-v0.1
- mistralai/ministral-14b-instruct-2512
- nvidia/ising-calibration-1-35b-a3b

### vision（视觉模型，3个）
- meta/llama-3.2-90b-vision-instruct
- meta/llama-4-maverick-17b-128e-instruct
- nvidia/llama-3.1-nemotron-nano-vl-8b-v1

## 已排除的模型

以下模型测试时返回错误，未纳入当前列表：

| 模型 | 错误 | 原因 |
|------|------|------|
| meta/llama-3.2-11b-vision-instruct | HTTP 502 | 网关错误（间歇性？） |
| meta/llama-3.2-1b-instruct | 超时 | 响应过慢 |
| google/gemma-3n-e4b-it | 超时 | 响应过慢 |
| google/gemma-3-27b-it | HTTP 410 | 已下线 |
| mistralai/mixtral-8x22b-instruct-v0.1 | HTTP 410 | 已下线 |
| qwen/qwen2.5-coder-32b-instruct | HTTP 410 | 已下线 |
| 其他 ~20个 | HTTP 404 | 不存在 |

## 更新工具

`~/.hermes/scripts/nv_model_test.py` — 批量测试 NVIDIA NIM 模型可用性
