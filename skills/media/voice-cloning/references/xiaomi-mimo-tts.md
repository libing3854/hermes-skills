# 小米MiMo TTS 语音合成参考

## 模型列表

| 模型ID | 功能 | 音色 | 注意事项 |
|--------|------|------|----------|
| `mimo-v2.5-tts` | 使用预置精品音色 | 预置音色列表 | 支持唱歌模式 |
| `mimo-v2.5-tts-voicedesign` | 通过文本描述定制音色 | 自动生成 | 不支持唱歌/预置/克隆 |
| `mimo-v2.5-tts-voiceclone` | 基于音频样本复刻音色 | 通过音频样本复刻 | 不支持唱歌/预置/设计 |

## 预置音色列表

| 音色名 | Voice ID | 语言 | 性别 |
|--------|----------|------|------|
| MiMo-默认 | mimo_default | 中文 | 女性 |
| 冰糖 | 冰糖 | 中文 | 女性 |
| 茉莉 | 茉莉 | 中文 | 女性 |
| 苏打 | 苏打 | 中文 | 男性 |
| 白桦 | 白桦 | 中文 | 男性 |
| Mia | Mia | 英文 | 女性 |

## API调用示例

### 基础TTS
```python
import requests, base64

API_KEY = "your_api_key"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "assistant", "content": "要合成的文本"}
    ],
    "audio": {
        "format": "wav",
        "voice": "mimo_default"
    }
}

response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
result = response.json()
audio_data = base64.b64decode(result['choices'][0]['message']['audio']['data'])
with open("output.wav", "wb") as f:
    f.write(audio_data)
```

### 语音克隆（voiceclone）
**⚠️ 关键：voiceclone模型的`voice`字段必须是DataURL格式，不能用`reference_audio`字段！**

```python
import requests, base64

API_KEY = "your_api_key"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

# 读取参考音频并转为DataURL
with open("reference.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()
data_url = "data:audio/wav;base64," + audio_b64

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "mimo-v2.5-tts-voiceclone",
    "messages": [
        {"role": "assistant", "content": "要合成的文本"}
    ],
    "audio": {
        "format": "wav",
        "voice": data_url  # ← 必须是DataURL，不是"custom"
    }
}

response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=data)
result = response.json()
audio_data = base64.b64decode(result['choices'][0]['message']['audio']['data'])
with open("cloned_output.wav", "wb") as f:
    f.write(audio_data)
```

**常见错误**：如果传`"voice": "custom", "reference_audio": audio_b64`，会报`400 Param Incorrect: audio.voice must be a DataURL for voice clone model`。

## 风格控制

### 自然语言控制
放在 `role: user` 的 `content` 中：
```
用轻快上扬的语调向领导报喜，语速稍快，带着查到成绩后压抑不住的激动与小骄傲，声音明亮有活力。
```

### 音频标签控制
放在 `role: assistant` 的 `content` 中：
```
(怅然)这么多年过去了，再走过那条街，心里一下子空了一块。
(磁性)夜已经深了，城市还在呼吸。我是今晚陪你的人，欢迎收听《午夜电台》。
```

### 情感变体测试
voiceclone + 情感控制组合用法（role:user放情感，role:assistant放文本）：
```python
emotions = {
    "normal": "",
    "shenqing": "用深情温柔的语气，语速稍慢，带着浓浓的眷恋和不舍。",
    "aishang": "用哀伤低沉的语气，语速缓慢，带着离别的悲伤和心碎。",
}
messages = [
    {"role": "user", "content": emotion_desc},
    {"role": "assistant", "content": actual_text}
]
```

### 唱歌模式（仅mimo-v2.5-tts支持）
**必须**在歌词最开头加`<style>唱歌</style>`前缀，否则只会朗读不会唱歌：
```python
lyrics = "原谅我这一生不羁放纵自由..."
content = "<style>唱歌</style>" + lyrics

data = {
    "model": "mimo-v2.5-tts",
    "messages": [{"role": "assistant", "content": content}],
    "audio": {"format": "wav", "voice": "茉莉"}
}
```
**注意**：
- `<style>唱歌</style>`必须在文本最开头
- 不能和其他style标签混用
- 歌词要完整，残缺会导致跑调
- 预置音色（茉莉、冰糖等）只支持中文歌词
- voiceclone模型不支持唱歌

## Hermes默认TTS配置
将voiceclone写入`~/.hermes/config.yaml`的`tts.xiaomi`段：
```yaml
tts:
  xiaomi:
    model: mimo-v2.5-tts-voiceclone
    voice: data:audio/wav;base64,<10秒参考音频的base64>
```
**注意**：用10秒切片（~427KB base64），避免配置文件过大。改前备份config.yaml。

## 文档链接
- [小米MiMo TTS文档](https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5)
