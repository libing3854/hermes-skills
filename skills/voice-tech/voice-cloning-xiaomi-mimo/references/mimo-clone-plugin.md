# MiMo-V2.5-TTS-VoiceClone 插件配置

## 插件位置
`~/.hermes/plugins/tts/mimo-clone/`

## 文件结构
```
~/.hermes/plugins/tts/mimo-clone/
├── __init__.py      # 插件入口，注册TTS provider
├── provider.py      # TTSProvider接口实现
├── plugin.yaml      # 插件元数据
└── README.md        # 使用说明
```

## config.yaml配置
```yaml
tts:
  provider: mimo-clone
  mimo-clone:
    voice_sample: /Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav
    model: mimo-v2.5-tts-voiceclone
```

## plugins.enabled配置（关键！）
插件必须在 `plugins.enabled` 列表中显式启用，否则不会被加载：
```yaml
plugins:
  enabled:
    - tts/mimo-clone
```

## 输出路径约定
- 参考音频：`/Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav`（保留，不清理）
- 生成的语音：`/Users/libing/Desktop/中岛美雪语音克隆/定期清除/`（定期清理）

## 工作原理
1. `text_to_speech`工具调用时，Hermes加载`mimo-clone` provider
2. Provider读取`voice_sample`指定的参考音频文件
3. 将参考音频转为Base64编码
4. 调用小米MiMo API（`mimo-v2.5-tts-voiceclone`模型）
5. 返回生成的WAV音频

## API调用格式
```python
from openai import OpenAI

client = OpenAI(api_key=api_key, base_url="https://token-plan-cn.xiaomimimo.com/v1")

completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[
        {"role": "user", "content": context},  # 可选的风格控制
        {"role": "assistant", "content": text}
    ],
    audio={
        "format": "wav",
        "voice": f"data:audio/wav;base64,{voice_base64}"
    }
)
```

## 参考音频
- 位置：`~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/voice_samples/nakajima_miyuki.wav`
- 来源：中岛美雪1980年代声音克隆（早期_clone.wav）
- 大小：599KB

## 测试
```bash
# 重启Gateway加载插件
hermes gateway restart

# 测试text_to_speech工具
# 应该使用中岛美雪克隆声音
```

## 注意事项
- 需要`XIAOMI_API_KEY`环境变量（已在`~/.hermes/.env`中配置）
- 输出格式为WAV（voiceclone模型原生格式）
- 参考音频Base64编码后不超过10MB
