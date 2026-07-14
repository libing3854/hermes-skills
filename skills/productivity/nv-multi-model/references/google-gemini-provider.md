# Google Gemini API — 备选 Provider 参考

> 发现时间：2026-05-20
> 端点：`https://generativelanguage.googleapis.com/v1beta/openai`（OpenAI 兼容模式）
> 免费层级：多数模型输入输出全免费，仅限速

## 接入方式

### API Key
- 获取：https://aistudio.google.com/app/apikey
- 存储：已写入 macOS Keychain，服务名 `gemini_api_key`（注意不是 `google_gemini_api_key`）
- 读取：`security find-generic-password -w -s "gemini_api_key"`

### OpenAI 兼容用法
```python
from openai import OpenAI

client = OpenAI(
    api_key="GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-3.5-flash",
    messages=[{"role": "user", "content": "hello"}]
)
```

### 并发限制
- 免费层有速率限制（比 OpenRouter 宽松，比 NVIDIA NIM 严格）
- 建议 Semaphore(5) 起步，实测不触发 429 后再加
- 付费层无此限制

## 免费模型清单

### 🟢 免费文本/推理模型

| 模型 ID | 类型 | 特点 |
|---------|------|------|
| `gemini-3.5-flash` | ⚡ 最强免费 | 最新 Flash，Agent/编程很强 |
| `gemini-3.1-flash-lite` | ⚡ 轻量 | 最高性价比 |
| `gemini-3-flash-preview` | ⚡ 中等 | 预览版免费 |
| `gemini-2.5-pro` | 🧠 强推理 | 上代 Pro，免费 |
| `gemini-2.5-flash` | ⚡ 上代主力 | 1M 上下文 |
| `gemini-2.5-flash-lite` | ⚡ 最便宜 | 最低延迟 |

### 🖼️ 免费视觉/多模态模型

| 模型 ID | 类型 | 特点 |
|---------|------|------|
| `gemini-3.5-flash` | 🖼️ 视觉 | 多模态最强，免费！（NVIDIA 同级的要付费） |
| `gemini-3.1-flash-lite` | 🖼️ 视觉 | 轻量看图 |
| `gemini-2.5-flash` | 🖼️ 视觉 | 1M 上下文，支持图片/视频/音频 |

### 🎙️ 免费 TTS 模型

| 模型 ID | 类型 | 特点 |
|---------|------|------|
| `gemini-3.1-flash-tts-preview` | 🎙️ TTS | **免费文字转语音！** 闪莉终于有 TTS 了 |

### ❌ 非免费模型（不可用于免费层）

| 模型 | 理由 |
|------|------|
| `gemini-3.1-pro-preview` | 无免费层级 |
| `gemini-3.1-flash-image-preview` (Nano Banana) | 无免费层级 |
| `veo-3.1` | 视频生成，付费 |
| `imagen-4` | 图像生成，付费 |
| `lyria-3` | 音乐生成，付费 |

## 定价对比（付费后）

| 模型 | 输入/1M tokens | 输出/1M tokens |
|------|:--------------:|:--------------:|
| Gemini 3.5 Flash | $1.50 | $9.00 |
| Gemini 3.1 Flash-Lite | $0.25 | $1.50 |
| Gemini 2.5 Flash | $0.30 | $2.50 |
| Gemini 2.5 Pro | $1.25 | $10.00 |
| Gemini 3.1 Flash TTS | $1.00（文字） | $20.00（音频） |

## 三 Provider 对比

| 维度 | NVIDIA NIM | OpenRouter | Google Gemini |
|------|:----------:|:----------:|:-------------:|
| 费用 | 🟢 全免费 | 🟢 全免费 | 🟡 免费层限速 |
| 模型数 | 36 个 | 37 个 | 8+ 个免费 |
| 视觉模型 | 4 个 | 重复 NV | ✅ 3.5 Flash 免费 |
| TTS | ❌ 无 | ❌ 无 | ✅ 3.1 Flash TTS |
| 并发限制 | Semaphore(10) | Semaphore(5) | Semaphore(5) 起步 |
| API Key 位置 | macOS Keychain | macOS Keychain | macOS Keychain |
| 速度 | 🟢 快 | 🟡 中 | 🟡 中 |

## 已接入实现（2026-05-20 ✅）

Google Gemini 已作为第三 Provider 正式接入，详见 `nv-multi-model` 技能本体。以下是已完成的修改：

| 文件 | 修改内容 |
|------|---------|
| `nv_ping.py` | 新增 `google` provider 路由，读 Keychain 的 `gemini_api_key`，Semaphore(8) |
| `groups.json` | 新增 8 个 `provider: "google"` 的模型条目（A/B 组各 4 个） |
| `nv_daily_eval.py` | provider 字段现已支持 nv/or/google 三值 |
| 模型分类 | Google 模型分布在 mimi/light/deep/vision 四类 |
| 竞速分组 | Google 模型混入 A/B 组，蛇形分配 |
| TTS 模型 | 不参与 Ping（TTS 不走 chat/completions 端点），需要用 TTS 时直接调 `text_to_speech` 工具 |
