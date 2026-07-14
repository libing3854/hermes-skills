---
name: mimo-tts-voiceclone
description: MiMo TTS声音克隆配置和使用指南
version: 1.0
tags: [tts, mimo, 声音克隆, 中岛美雪, 语音]
---

# MiMo TTS声音克隆

## 概述

使用小米MiMo V2.5 TTS VoiceClone模型进行声音克隆。

## 配置信息

### API配置
- **Provider**: xiaomi (Token Plan)
- **Base URL**: https://token-plan-cn.xiaomimimo.com/v1
- **环境变量**: XIAOMI_API_KEY

### TTS配置（config.yaml）
```yaml
tts:
  provider: mimo-clone
  mimo-clone:
    voice_sample: /Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav
    model: mimo-v2.5-tts-voiceclone
```

## 参考音频

- **文件**: `/Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav`
- **来源**: 早期_clone.wav（1980年代中岛美雪声音克隆）
- **大小**: 585KB

## 使用方法

### 内置text_to_speech工具
```python
text_to_speech(
    text="要说的文本",
    output_path="/Users/libing/Desktop/中岛美雪语音克隆/定期清除/output.wav"
)
```

### Python脚本
```python
from openai import OpenAI
import base64

client = OpenAI(api_key=api_key, base_url="https://token-plan-cn.xiaomimimo.com/v1")

# 读取参考音频
with open("nakajima_miyuki.wav", "rb") as f:
    voice_base64 = base64.b64encode(f.read()).decode("utf-8")

# 调用API
completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[{"role": "assistant", "content": "要说的文本"}],
    audio={"format": "wav", "voice": f"data:audio/wav;base64,{voice_base64}"}
)
```

## MiMo-Skills安装

### 安装位置
- **插件**: `~/.hermes/plugins/tts/mimo-clone/`
- **技能**: `~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/`
- **参考音频**: `/Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav`

### 脚本
- `nakajima_clone.py` - 中岛美雪专用克隆脚本
- `mimo_tts_voiceclone.py` - 通用声音克隆脚本

## 文件输出

- **语音输出目录**: `/Users/libing/Desktop/中岛美雪语音克隆/定期清除/`
- **参考音频**: 保留在上一级目录，不会被定期清理

## 注意事项

1. VoiceClone模型每次请求都需要传参考音频（Base64编码）
2. 参考音频文件不能超过10MB
3. 输出格式默认为WAV
4. Cron任务中不能用terminal执行Python脚本，需要插件方式

## ⚠️ 关键Pitfall：插件必须在plugins.enabled中注册（2026-06-25 验证）

**问题：** 配置了 `tts.provider: mimo-clone`，但实际TTS输出仍然是Edge TTS（茉莉音色）。

**根因：** Hermes插件系统要求用户安装的插件（`~/.hermes/plugins/`）必须显式加入 `plugins.enabled` 配置才能加载。仅设置 `tts.provider: mimo-clone` 不够——这只告诉工具要用哪个provider，但如果插件本身没加载，provider不会出现在registry中，调度时就会回退到默认的Edge TTS。

**调用链路：**
```
text_to_speech("你好")
  → _get_provider() → "mimo-clone"  ✅ 配置正确
  → _dispatch_to_plugin_provider()
    → tts_registry.get_provider("mimo-clone") → None  ❌ 插件未注册
    → 回退到 DEFAULT_PROVIDER = "edge"
    → Edge TTS zh-CN-XiaoxiaoNeural 茉莉音色  ← 问题所在
```

**修复：**
```bash
hermes plugins enable tts/mimo-clone
```

**验证：**
```bash
# 检查插件是否启用
hermes plugins list | grep mimo-clone
# 应显示: tts/mimo-clone: ENABLED

# 检查provider是否注册
python3 -c "
from hermes.agent.tts_registry import get_provider
p = get_provider('mimo-clone')
print(f'Provider: {p}')
print(f'Available: {p.is_available if p else False}')
"
# 应显示: Provider: <MiMoCloneTTSProvider>, Available: True
```

**症状：** 配置正确但TTS输出是茉莉音色（Edge TTS）→ 几乎可以肯定是插件未注册。

## 参考音频路径变更记录

- **旧路径**: `/Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav`
- **新路径**: `~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/voice_samples/nakajima_miyuki.wav`
- config.yaml中应使用新路径
