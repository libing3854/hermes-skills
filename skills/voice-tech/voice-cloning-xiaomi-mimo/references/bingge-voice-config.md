# 冰哥的语音配置方案

## 两级TTS系统

### 默认语音：中岛美雪早期（1980年）
- **参考音频**：`早期_1980年_片段_final.wav`（07:05-07:35，30秒）
- **脚本**：`early_clone_tts.py`
- **特点**：年轻清脆，充满活力

### 多对话语音：茉莉（小米MiMo预置音色）
- **Voice ID**：茉莉
- **脚本**：`deep_conversation_tts.py`
- **特点**：温柔、沉稳、女性

## 文件位置

### 原始文件（桌面目录）
```
~/Desktop/中岛美雪语音克隆/
├── 早期_1980年_片段_final.wav  # 早期参考音频
├── 中期_1995年_片段_v2.wav     # 中期参考音频（备用）
├── 近期_2026年_片段.wav        # 近期参考音频
├── early_clone_tts.py          # 默认语音脚本
├── deep_conversation_tts.py    # 多对话脚本
└── voice_clone.py              # 通用语音克隆脚本
```

### MiMo-Skills集成版（推荐）
```
~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/
├── voice_samples/
│   └── nakajima_miyuki.wav     # 中岛美雪参考音频（近期版本）
├── scripts/
│   ├── nakajima_clone.py       # 中岛美雪专用克隆脚本
│   ├── mimo_tts.py             # 基本TTS脚本
│   ├── mimo_tts_voiceclone.py  # 通用克隆脚本
│   └── mimo_tts_voicedesign.py # 音色设计脚本
└── SKILL.md
```

## 使用方法

### 默认语音（早期版本）
```bash
cd ~/Desktop/中岛美雪语音克隆/
python3 early_clone_tts.py "要合成的文本"
```

### 多对话场景（茉莉）
```bash
cd ~/Desktop/中岛美雪语音克隆/
python3 deep_conversation_tts.py "要合成的文本"
```

## 配置详情

```yaml
# config.yaml
tts:
  provider: xiaomi
  xiaomi:
    model: mimo-v2.5-tts
    voice: 茉莉  # 默认音色
```

## 参考音频来源

| 版本 | 来源 | 链接 |
|------|------|------|
| 早期 | YouTube 1980年All Night Nippon | https://www.youtube.com/watch?v=Z_IqWN6jOAA |
| 中期 | YouTube 1995年お時間拝借 | https://www.youtube.com/watch?v=-lZSHid1byk |
| 近期 | Bilibili 2026年全时代点播 | https://www.bilibili.com/video/BV1PtAAzkE1k/ |
