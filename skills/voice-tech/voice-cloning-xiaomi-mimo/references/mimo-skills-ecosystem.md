# MiMo 生态系统参考

## 已安装的仓库

### MiMo-Skills（已安装）
- **位置**: `~/.hermes/skills/mimo-skills/`
- **符号链接**: `~/.hermes/skills/mimo-v2-5-tts` → `mimo-skills/skills/mimo-v2-5-tts`
- **GitHub**: github.com/XiaomiMiMo/MiMo-Skills
- **许可证**: MIT
- **版本**: v0.1.2

### 提供的技能

| 技能 | 功能 | 脚本 |
|------|------|------|
| `mimo-v2-5-tts` | 预置音色语音合成 | `mimo_tts.py` |
| `mimo-v2-5-tts-voicedesign` | 文本描述定制音色 | `mimo_tts_voicedesign.py` |
| `mimo-v2-5-tts-voiceclone` | 音频样本复刻音色 | `mimo_tts_voiceclone.py` |

### 高级功能（超出基本TTS）

| 功能 | 说明 | 使用方式 |
|------|------|---------|
| **唱歌** | 支持歌词合成 | `(唱歌)歌词内容` |
| **方言** | 东北/四川/河南/粤语 | `(东北话)文本` |
| **导演模式** | 角色+场景+指导三维控制 | `--context` 参数 |
| **音频标签** | 句内情绪切换 | `(紧张，深呼吸)文本` |
| **音色设计** | 文本描述生成新音色 | `mimo_tts_voicedesign.py` |
| **音色克隆** | 用音频样本复刻 | `mimo_tts_voiceclone.py` |

### 预置音色（8种）

| 音色名 | 语言 | 性别 | 风格 |
|--------|------|------|------|
| 冰糖 | 中文 | 女性 | 活泼少女 |
| 茉莉 | 中文 | 女性 | 知性女声 |
| 苏打 | 中文 | 男性 | 阳光少年 |
| 白桦 | 中文 | 男性 | 成熟男声 |
| Mia | English | Female | Lively girl |
| Chloe | English | Female | Sweet Dreamy |
| Milo | English | Male | Sunny boy |
| Dean | English | Male | Steady Gentle |

## 其他MiMo仓库

### MiMo-Code（AI代码助手）
- **GitHub**: github.com/XiaomiMiMo/MiMo-Code
- **Star**: 2.9k
- **定位**: 小米版Claude Code/Cursor
- **特点**: 支持VS Code和Zed，内置Agent工作流

### MiMo-V2-Flash（旗舰推理模型）
- **GitHub**: github.com/XiaomiMiMo/MiMo-V2-Flash
- **Star**: 1.3k
- **参数**: 309B总参数，15B活跃参数（MoE架构）
- **架构**: 混合注意力 + Multi-Token Prediction (MTP)
- **性能**: AIME 2025数学推理94.1%，SWE-Bench 73.4%，超越OpenAI o1-mini
- **上下文**: 支持32K-262K长上下文检索，接近100%成功率
- **许可证**: Apache 2.0

### MiMo-V2.5 vs Qwen3.5-9B 性能对比（2026-06-11实测）

| 维度 | MiMo-V2.5 | Qwen3.5-9B | 差距 |
|------|-----------|------------|------|
| 智力(Intelligence) | ~49 | ~32 | MiMo高53% |
| 编码(Coding) | ~42 | ~25 | MiMo高68% |
| Agent能力 | ~66 | ~37 | MiMo高78% |
| 上下文长度 | 1.05M tokens | 262K tokens | 4倍 |
| 30天tokens使用量 | 5.56T | 125B | 44倍 |

**结论**: MiMo-V2.5全面碾压Qwen3.5-9B，唯一优势是Qwen延迟更低(1.29s vs 5.55s)

### MiMo-V2.5-Pro/UltraSpeed
- **特点**: 增强长程推理、更高Agent效率
- **模型**: mimo-v2.5-pro（当前默认模型）
- **注意**: MiMo-V2-Pro/Omni将于2026.6.30下线，需切换到V2.5系列

## API端点对比

| 服务 | 环境变量 | 端点 | 用途 |
|------|---------|------|------|
| Token Plan | `XIAOMI_API_KEY` | token-plan-cn.xiaomimimo.com | LLM推理 + TTS ✅ |
| MiMo开放平台 | `MIMO_API_KEY` | api.xiaomimimo.com | TTS高级功能（需要新Key） |

**已验证（2026-06-11）**：
- ✅ Token Plan 端点可用于 TTS（`mimo-v2.5-tts` 模型，返回 WAV 音频）
- ✅ Hermes 内置 `text_to_speech` 工具使用 Token Plan 端点，音色"茉莉"正常工作
- ❌ 直接用 `api.xiaomimimo.com` 端点 + XIAOMI_API_KEY 调用返回 401
- ⚠️ MiMo-Skills 脚本默认使用 `api.xiaomimimo.com`，需要修改为 `token-plan-cn.xiaomimimo.com` 才能用现有 Key

**MiMo-Skills 脚本端点修复**：修改 `~/.hermes/skills/mimo-v2-5-tts/scripts/mimo_tts.py` 中的 `base_url`，将 `api.xiaomimimo.com` 改为 `token-plan-cn.xiaomimimo.com`，即可用现有 XIAOMI_API_KEY 调用。

## 调用示例

### 基本TTS（使用现有Key）
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("XIAOMI_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)

completion = client.chat.completions.create(
    model="mimo-v2.5-tts",
    messages=[
        {"role": "assistant", "content": "冰哥你好！"}
    ],
    audio={"format": "wav", "voice": "茉莉"}
)
```

### 唱歌
```bash
python3 ~/.hermes/skills/mimo-v2-5-tts/scripts/mimo_tts.py \
  --text "(唱歌)原谅我这一生不羁放纵爱自由" \
  --voice "冰糖" \
  --output ~/Desktop/singing.wav
```

### 方言
```bash
python3 ~/.hermes/skills/mimo-v2-5-tts/scripts/mimo_tts.py \
  --text "(东北话)哎呀妈呀，这大雪片子" \
  --voice "白桦" \
  --output ~/Desktop/dialect.wav
```

### 导演模式
```bash
python3 ~/.hermes/skills/mimo-v2-5-tts/scripts/mimo_tts.py \
  --context "角色：百年门阀大当家。场景：祠堂阴影里。指导：冰冷慵懒的低音御姐。" \
  --text "你不该来这里。" \
  --voice "茉莉" \
  --output ~/Desktop/director.wav
```
