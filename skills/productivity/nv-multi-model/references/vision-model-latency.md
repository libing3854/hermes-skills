# 🖼️ 视觉/多模态模型延迟实测数据

> 数据来源：NVIDIA NIM Ping 系统实时采样 — 2026-05-20 11:00 (UTC+8)
> A 组整点 Ping，所有模型 100% 成功率

## 实时延迟

| 模型 | 本次(ms) | 定位 |
|------|:--------:|------|
| `nvidia/nemotron-nano-12b-v2-vl` | 698 | 🏆 最快（视觉速度王） |
| `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | 712 | 轻量视觉 |
| `meta/llama-3.2-11b-vision-instruct` | 828 | 能力最强 |

## 延迟趋势说明

| 模型 | 文档标注 | 实测 | 差异 |
|------|:--------:|:----:|:----:|
| nemotron-nano-12b-v2-vl | 923ms | **698ms** | 🟢 快 24% |
| llama-3.1-nemotron-nano-vl-8b-v1 | 923ms | **712ms** | 🟢 快 23% |
| llama-3.2-11b-vision-instruct | 832ms | **828ms** | 🟢 基本一致 |

文档延迟偏高，实际 Ping 系统数据显示视觉模型普遍更快。

## OpenRouter 多模态

| 模型 | 典型延迟 | 提供方 |
|------|:--------:|:------:|
| `moonshotai/kimi-k2.6` | ~1033ms | OpenRouter 免费 |

## Google Gemini 视觉模型（🆕 2026-05-20）

| 模型 | 类型 | 状态 |
|------|------|:----:|
| `gemini-2.5-flash-image` | 🖼️ 视觉（B组） | ⏳ 已接入 Ping，等待延迟数据 |
| `gemini-3.5-flash` | 🖼️ 视觉+文本（A组） | ✅ 已接入 Ping，多模态最强免费模型，等待延迟数据 |
| `gemini-2.5-flash` | 🖼️ 视觉+文本 | ✅ 支持图片/视频/音频理解 |

> 注：Google 视觉模型通过 OpenAI 兼容端点调用，同一 `chat/completions` 接口支持图片输入。延迟数据将在下一轮 Ping 后自动采集。

## 诊断命令

```bash
# 查看最新 A 组 Ping 数据
cat ~/.hermes/data/NVping/tmp/ping_A.json | python3 -c '
import json,sys; d=json.load(sys.stdin)
for mid, info in d.get("models",{}).items():
    if any(k in mid.lower() for k in ["vision","vl","kimi"]):
        print(mid, "->", info.get("ms","?"), "ms", "✅" if info.get("ok") else "❌")
'

# 查看 ranking 中的视觉模型排名
cat ~/.hermes/data/NVping/tmp/ranking.json | python3 -c '
import json,sys; d=json.load(sys.stdin)
# ranking 数据格式因版本可能不同，直接 grep
'

# 查看健康状态
cat ~/.hermes/data/NVping/tmp/health.json | python3 -m json.tool
```
