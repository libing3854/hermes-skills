# 中岛美雪声音克隆配置

## 概述

使用小米MiMo TTS API克隆中岛美雪的声音，已集成到MiMo-Skills中。

## 文件位置

### 参考音频
- **路径**: `~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/voice_samples/nakajima_miyuki.wav`
- **来源**: 早期_clone.wav（599 KB）— 1980年代声音克隆版
- **时长**: 约30秒
- **特点**: 1980年代年轻声音，清脆有活力，冰哥确认为默认参考

### 克隆脚本
- **路径**: `~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/scripts/nakajima_clone.py`
- **使用API**: XIAOMI_API_KEY（Token Plan端点）
- **模型**: mimo-v2.5-tts-voiceclone

## 使用方法

### 基本用法
```bash
# 设置API Key
export XIAOMI_API_KEY=$(grep "^XIAOMI_API_KEY=" ~/.hermes/.env | cut -d= -f2- | tr -d "'\"")

# 运行克隆
python3 ~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/scripts/nakajima_clone.py \
  "要说的文本" \
  ~/Desktop/output.wav
```

### 带风格控制
```bash
python3 ~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/scripts/nakajima_clone.py \
  "要说的文本" \
  ~/Desktop/output.wav \
  "温柔地说"
```

### 示例输出
```
✅ 克隆成功: /Users/libing/Desktop/nakajima_test.wav
   大小: 352.5 KB
```

## 技术细节

### API调用
```python
client = OpenAI(
    api_key=os.environ.get("XIAOMI_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)

completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[
        {"role": "user", "content": ""},
        {"role": "assistant", "content": text}
    ],
    audio={
        "format": "wav",
        "voice": f"data:audio/wav;base64,{voice_base64}"
    }
)
```

### 参考音频要求
- 格式: WAV或MP3
- 大小: Base64编码后不超过10MB
- 质量: 清晰、无背景音乐的纯人声片段效果最佳
- 时长: 15-60秒（推荐30秒）

## 相关文件

### 原始文件（桌面目录）
```
~/Desktop/中岛美雪语音克隆/
├── 近期_2026年_片段.wav        # 参考音频来源
├── voice_clone.py              # 原始克隆脚本
├── deep_conversation_tts.py    # 茉莉音色脚本
└── 中岛美雪_克隆测试.wav       # 测试输出
```

## 注意事项

1. **API Key**: 使用XIAOMI_API_KEY（Token Plan），不是MIMO_API_KEY
2. **端点**: token-plan-cn.xiaomimimo.com/v1（不是api.xiaomimimo.com）
3. **模型**: mimo-v2.5-tts-voiceclone（不是mimo-v2.5-tts）
4. **随机性**: TTS有随机性，同样输入的效果可能不同，可多生成几次挑选
