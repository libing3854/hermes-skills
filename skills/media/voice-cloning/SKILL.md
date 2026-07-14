---
name: voice-cloning
description: "语音克隆工作流 — 从参考音频到AI语音合成的完整流程。包括音频获取、预处理、TTS API调用、多版本生成。触发条件：用户要求克隆某个声音、制作专属语音、训练语音模型。"
version: 1.2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [voice, tts, cloning, audio, media]
    related_skills: [songsee, heartmula]
---

# 语音克隆工作流

> 完整的语音克隆流程，从参考音频获取到AI语音合成。

## 🎯 适用场景

- 用户想克隆某个名人的声音
- 制作专属语音用于TTS
- 创建自定义语音模型
- 声音特征研究

## 📋 工作流程

### 阶段1：音频资源获取

#### 1.1 寻找参考音频
- **优先级**：纯说话音频 > 访谈 > 新闻 > 音乐（仅念白部分）
- **要求**：
  - 清晰的人声
  - 无背景音乐或低背景噪音
  - 时长15-60秒
  - 覆盖不同时期（可选）

#### 1.2 资源来源
| 来源 | 特点 | 搜索关键词 |
|------|------|------------|
| YouTube | 海外资源 | `[名人名] interview audio` |
| Bilibili | 中文资源 | `[名人名] 访谈 说话` |
| 喜马拉雅 | 有声书 | `[名人名] 电台 访谈` |
| 学术数据库 | 高质量样本 | `voice database [语言]` |

#### 1.3 版权考虑
- **非商业用途**：可以使用公开资源
- **商业用途**：需要授权或使用AI生成的类似声音
- **建议**：优先使用无版权或CC协议的音频

### 阶段2：音频预处理

#### 2.1 工具要求
```bash
# 安装yt-dlp（下载YouTube/Bilibili视频）
pip3 install yt-dlp

# 安装ffmpeg（音频处理）
brew install ffmpeg  # macOS
apt install ffmpeg   # Linux
```

#### 2.2 下载视频音频
```bash
# YouTube下载
yt-dlp -x --audio-format wav -o "output.%(ext)s" "URL"

# Bilibili下载（必须带cookies，否则HTTP 412）
yt-dlp --ignore-config -x --audio-format wav --audio-quality 0 \
  -o "output.%(ext)s" --cookies-from-browser chrome "URL"

# Bilibili多P视频指定分P
yt-dlp --ignore-config -x --audio-format wav -o "output.%(ext)s" \
  --cookies-from-browser chrome "https://www.bilibili.com/video/BVxxx?p=21"
```

**⚠️ yt-dlp配置文件陷阱**：`~/.config/yt-dlp/config`可能包含旧选项（如`--js-runtimes node`），导致"no such option"报错。始终加`--ignore-config`绕过。

#### 2.3 音频截取
```bash
# 截取指定时间段（16kHz/16bit/mono）
ffmpeg -i input.wav -ss 00:01:30 -to 00:02:15 -ar 16000 -ac 1 output.wav

# 截取片段（保持原格式）
ffmpeg -i input.wav -ss 00:01:30 -to 00:02:15 -c copy output.wav
```

#### 2.4 音频质量检查
```bash
# 检查音频信息
ffprobe -v error -show_entries format=duration,bit_rate output.wav

# 检查音频波形（需要sox）
sox output.wav -n stat
```

### 阶段2.5：人声分离（可选）

从歌曲/音乐中提取纯人声，用于语音克隆参考音频。

#### 在线工具（通常被Cloudflare拦截）
- vocalremover.org、lalal.ai 等在线分离工具
- **⚠️ Cloudflare会拦截自动化浏览器**（内置browser工具和Chrome DevTools MCP都无法通过验证）
- 如需使用在线工具，让用户在本地浏览器手动操作

#### 本地工具：demucs（推荐）
```bash
# 安装
pip3 install demucs soundfile

# 分离人声（两轨：人声 + 伴奏）
demucs --two-stems=vocals -o . --mp3 input.wav

# 输出目录结构：
# htdemucs/<歌名>/vocals.mp3    ← 人声
# htdemucs/<歌名>/no_vocals.mp3 ← 伴奏
```

**⚠️ demucs依赖**：必须安装`soundfile`包，否则torchaudio报"Couldn't find appropriate backend"错误。`--mp3`输出比wav更稳定（避免torchaudio保存bug）。

### 阶段3：TTS API调用

#### 3.1 小米MiMo TTS模型选择

| 模型ID | 功能 | 音色 | 用途 |
|--------|------|------|------|
| `mimo-v2.5-tts` | 使用预置精品音色 | 预置音色列表 | 基础TTS |
| `mimo-v2.5-tts-voicedesign` | 通过文本描述定制音色 | 自动生成 | 自定义音色 |
| **`mimo-v2.5-tts-voiceclone`** | **基于音频样本复刻任意音色** | **通过音频样本复刻** | **语音克隆** ✅ |

**注意**：语音克隆模型不支持唱歌模式、预置音色与音色设计。

**唱歌模式**：仅`mimo-v2.5-tts`（预置音色模型）支持唱歌。**必须**在歌词开头加`<style>唱歌</style>`前缀，否则模型只会朗读歌词不会唱歌。

```python
lyrics = "在那苍茫大海的那一方\n现在有人正受着伤..."
content = "<style>唱歌</style>" + lyrics  # ← 关键前缀

data = {
    "model": "mimo-v2.5-tts",
    "messages": [
        {"role": "assistant", "content": content}
    ],
    "audio": {"format": "wav", "voice": "茉莉"}
}
```

**⚠️ 唱歌注意事项**：
- `<style>唱歌</style>`必须在文本最开头，不能和其他style混用
- 歌词要完整，残缺歌词会导致跑调、效果差
- 只支持中文歌词（茉莉、冰糖等预置音色不支持日文歌词）
- voiceclone模型不支持唱歌

#### 3.2 小米MiMo TTS调用
```python
import requests
import base64
import json

# 配置
API_KEY = "your_api_key"
BASE_URL = "https://token-plan-cn.xiaomimimo.com/v1"

# 调用TTS
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "mimo-v2.5-tts",
    "messages": [
        {
            "role": "assistant",
            "content": "要合成的文本"
        }
    ],
    "audio": {
        "format": "wav",
        "voice": "mimo_default"  # 或其他音色
    }
}

response = requests.post(f"{BASE_URL}/chat/completions", 
                        headers=headers, json=data)
result = response.json()

# 解码音频
audio_data = base64.b64decode(result['choices'][0]['message']['audio']['data'])
with open("output.wav", "wb") as f:
    f.write(audio_data)
```

#### 3.3 语音克隆调用（voiceclone模型）
```python
# 读取参考音频 → DataURL
with open("reference.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()
data_url = "data:audio/wav;base64," + audio_b64

data = {
    "model": "mimo-v2.5-tts-voiceclone",
    "messages": [{"role": "assistant", "content": "要合成的文本"}],
    "audio": {"format": "wav", "voice": data_url}  # ← 必须是DataURL
}
```
**⚠️ voiceclone的`voice`字段必须是DataURL**（`data:audio/wav;base64,...`），不能用`"custom"`或`"reference_audio"`字段，否则报400错误。详见 [references/xiaomi-mimo-tts.md](references/xiaomi-mimo-tts.md)。

**⚠️ DataURL体积控制**：参考音频越长，DataURL越大。30秒16kHz mono wav ≈ 1.2MB base64，10秒 ≈ 427KB。配置文件（如Hermes config.yaml）中嵌入DataURL时，用10秒切片足够（克隆质量不受影响），避免配置文件过大。

**⚠️ 10秒切片取中间段**：从30秒切片中截取10秒做DataURL参考时，取**中间10秒**（00:10-00:20）比取前10秒效果更好。前10秒可能有起音不稳或呼吸声，中间段节奏更稳定。命令：`ffmpeg -y -i slice.wav -ss 00:10 -t 10 -ar 16000 -ac 1 ref_mid.wav`

#### 3.4 设置voiceclone为Hermes默认TTS
将克隆声音写入`~/.hermes/config.yaml`的`tts`段，使所有`text_to_speech`调用自动使用该声音：
```yaml
tts:
  provider: mimo-clone  # ← 必须用插件注册名，不是"xiaomi"
  mimo-clone:
    voice_sample: ~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/voice_samples/nakajima_miyuki.wav
    model: mimo-v2.5-tts-voiceclone
```
步骤：`ffmpeg -y -i ref.wav -t 10 -ar 16000 -ac 1 /tmp/ref_short.wav` → base64 → 写入config.yaml。改前备份：`cp ~/.hermes/config.yaml ~/.hermes/config.yaml.bak.$(date +%Y%m%d%H%M)`

**⚠️ 关键陷阱：必须启用mimo-clone插件（2026-06-25验证）**
仅设置`provider: mimo-clone`不够！Hermes插件系统要求用户安装的插件必须显式加入`plugins.enabled`才能加载。否则TTS会fallback到Edge TTS（茉莉音色）。

调用链路：
```
text_to_speech → _get_provider() → "mimo-clone" ✅配置正确
  → _dispatch_to_plugin_provider()
    → tts_registry.get_provider("mimo-clone") → None ❌插件未注册
    → 回退到 DEFAULT_PROVIDER = "edge" → 茉莉音色
```

修复方法：
```bash
hermes plugins enable tts/mimo-clone
hermes gateway restart
```
验证：`hermes plugins list | grep mimo-clone` 应显示 ENABLED。

#### 3.5 使用Hermes text_to_speech工具
```python
text_to_speech(
    text="要合成的文本",
    output_path="output.mp3"
)
```
**⚠️ 输出格式陷阱**：`text_to_speech`工具实际输出**MP3格式**，即使路径写`.wav`扩展名。播放器可能无法识别。如需真WAV，用ffmpeg转换：
```bash
ffmpeg -y -i output.wav -c:a pcm_s16le output_real.wav && mv output_real.wav output.wav
```

### 阶段4：多版本生成

#### 4.0 情感变体测试
用不同语气测试同一段文本，验证克隆质量：
```python
emotions = {
    "normal": "",  # 无情感描述 = 正常语调
    "shenqing": "用深情温柔的语气，语速稍快，带着浓浓的眷恋和不舍。",
    "aishang": "用哀伤低沉的语气，语速缓慢，带着离别的悲伤和心碎。",
}
# role: user 放情感描述，role: assistant 放实际文本
messages = [
    {"role": "user", "content": emotion_desc},
    {"role": "assistant", "content": actual_text}
]
```

#### 4.1 三个时期的样本
| 版本 | 时期 | 用途 |
|------|------|------|
| 早期 | 10-20年前 | 年轻清脆的声音 |
| 中期 | 5-10年前 | 成熟稳重的声音 |
| 近期 | 1-5年前 | 最新的声音 |

#### 4.2 生成流程
```
1. 准备三个时期的参考音频
2. 为每个时期调用TTS API
3. 对比三个版本的效果
4. 选择最佳版本或混合使用
```

## ⚠️ 常见问题

### 1. API Key无效
**症状**：HTTP 401 Invalid API Key
**解决**：
1. 检查.env文件中的API Key是否完整（不要被截断）
2. 手动加载环境变量测试：`export XIAOMI_API_KEY=$(grep XIAOMI_API_KEY ~/.hermes/.env | grep -v "^#" | cut -d'=' -f2)`
3. 验证API Key是否过期

### 2. 音频质量差
**症状**：生成的音频有噪音或失真
**解决**：
1. 使用更高质量的参考音频
2. 增加参考音频时长（30-60秒）
3. 选择无背景噪音的片段

### 3. 语音不相似
**症状**：生成的语音与参考音频差异大
**解决**：
1. 使用更多时期的参考音频
2. 调整TTS参数（语速、音调等）
3. 尝试不同的TTS模型

### 4. Chrome DevTools限制
**症状**：无法自动下载需要验证的页面
**重要**：Chrome DevTools连接的是**代理端浏览器**，不是用户本地浏览器！用户看不到代理操作的页面。
**解决**：
1. 让用户在本地Chrome手动完成验证
2. 用户提供下载链接或文件位置
3. 使用在线下载工具（如savefrom.net）
4. 寻找其他可下载的资源

### 5. YouTube/Bilibili下载失败
**症状**：HTTP 403 Forbidden 或 Cloudflare验证
**解决**：
1. Bilibili必须加`--cookies-from-browser chrome`
2. 使用浏览器扩展（Video DownloadHelper）
3. 使用在线下载网站（savefrom.net）
4. 用户手动下载后放到指定目录

### 6. yt-dlp报"no such option: --js-runtimes"
**症状**：`~/.config/yt-dlp/config`包含旧选项导致报错
**解决**：加`--ignore-config`绕过配置文件

### 7. 人声分离工具被Cloudflare拦截
**症状**：vocalremover.org等在线工具无法通过安全验证
**解决**：使用本地demucs工具（见阶段2.5），需先`pip3 install demucs soundfile`

### 8. demucs报"Couldn't find appropriate backend"
**症状**：torchaudio保存音频时报backend错误
**解决**：`pip3 install soundfile`，并使用`--mp3`输出格式

### 9. voiceclone报"audio.voice must be a DataURL"
**症状**：`400 Param Incorrect: audio.voice must be a DataURL for voice clone model`
**原因**：voiceclone模型要求`voice`字段传DataURL格式（`data:audio/wav;base64,...`），不是字符串也不是单独的`reference_audio`字段
**解决**：`"voice": "data:audio/wav;base64," + base64.b64encode(audio_bytes).decode()`

### 10. mimo-clone 插件未启用导致回退到 Edge TTS（2026-06-25 发现）
**症状**：config.yaml 设置了 `tts.provider: mimo-clone`，但生成的音频是 Edge TTS 的茉莉音色
**原因**：mimo-clone 插件存在于 `~/.hermes/plugins/tts/mimo-clone/`，但未在 `plugins.enabled` 中注册
**调用链**：`text_to_speech → get_provider("mimo-clone") → None → 回退到 edge`
**解决**：
```bash
hermes plugins enable tts/mimo-clone
hermes gateway restart
```
**验证**：`hermes plugins list | grep mimo-clone` 应显示 ENABLED
**预防**：安装 TTS 插件后必须执行 `hermes plugins enable`，仅配置 `tts.provider` 不够

### 10. 参考音频截取不准确
**症状**：截取的片段包含杂音、音乐或非目标内容
**解决**：
1. 先让用户在视频中找到准确的时间点
2. 截取30秒片段，让用户确认质量
3. 多截取几个时间段供选择

### 11. 克隆语音拉长/拖沓
**症状**：生成的语音语速异常缓慢，像被拉长了
**原因**：参考音频切到了歌曲中拖长音/慢节奏的部分（如副歌长音、抒情段落）
**解决**：换一段节奏更紧凑的切片位置。歌曲中段（跳过前奏和副歌）通常更适合做克隆参考。每首歌多切几段（如01:00、02:30、04:00），逐个测试对比。

### 12. voiceclone生成时长与参考音频不匹配
**症状**：短文本（如"永远爱我"）生成4-5秒音频，正常应1-2秒
**原因**：参考切片节奏太慢或包含长音
**解决**：同#11，换切片位置。正常4字短句应生成1-2秒音频。

### 13. 多切片对比测试
每次克隆前，从歌曲不同位置切3-5段30秒切片，逐个测试。用户会指定"用哪个"，未选用的归档到`unused/`子目录。输出结构：
```
cese/
├── 美嘉/
│   ├── meijia_slice_new.wav  ← 用户选定的切片
│   ├── test_xxx.wav          ← 生成结果
│   └── unused/               ← 未选用的切片
└── 美雪/
    ├── meixue_slice_new.wav
    ├── test_xxx.wav
    └── unused/
```

## 📊 输出格式

### 完整输出结构
```
~/Desktop/语音克隆/
├── 原始视频/
│   ├── 早期_视频.mp4
│   ├── 中期_视频.mp4
│   └── 近期_视频.mp4
├── 音频片段/
│   ├── 早期_片段.wav
│   ├── 中期_片段.wav
│   └── 近期_片段.wav
└── 生成结果/
    ├── 早期_版本.wav
    ├── 中期_版本.wav
    └── 近期_版本.wav
```

## 🔧 高级技巧

### 1. 批量处理
```bash
# 批量截取多个时间段
for start in 00:01:00 00:03:00 00:05:00; do
  end=$(date -j -v+30S -f "%H:%M:%S" "$start" +%H:%M:%S)
  ffmpeg -i input.wav -ss $start -to $end -c copy "segment_${start//:/}.wav"
done
```

### 2. 音频增强
```bash
# 降噪
ffmpeg -i input.wav -af "afftdn" output.wav

# 音量标准化
ffmpeg -i input.wav -af "loudnorm" output.wav
```

### 3. 格式转换
```bash
# WAV转MP3
ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3

# 采样率转换
ffmpeg -i input.wav -ar 44100 output.wav
```

## 📚 参考资源

- [小米MiMo TTS文档](https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5)
- [小米MiMo TTS详细参考](references/xiaomi-mimo-tts.md) - 模型列表、预置音色、API调用示例
- [人声分离参考](references/vocal-separation.md) - demucs安装、使用、已知问题
- [音频收集工作流](references/audio-collection-workflow.md) - 资源搜索、下载、截取、质量检查
- [ffmpeg音频处理](https://ffmpeg.org/documentation.html)
- [yt-dlp使用指南](https://github.com/yt-dlp/yt-dlp)

## 🎯 最佳实践

1. **参考音频质量**：选择清晰、无噪音的纯人声片段
2. **时长控制**：15-60秒最佳，太短信息不足，太长可能有噪音
3. **多时期覆盖**：准备不同时期的参考音频，增加多样性
4. **版权意识**：非商业用途优先，商业用途需授权
5. **质量验证**：生成后务必试听，确认效果符合预期