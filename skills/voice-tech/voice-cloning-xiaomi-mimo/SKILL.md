---
name: voice-cloning-xiaomi-mimo
description: 使用小米MiMo TTS API进行语音克隆的完整工作流。包括寻找参考音频、提取片段、调用API、配置两级TTS系统。
version: 2.0.0
tags: [tts, voice-cloning, xiaomi, mimo, audio, 语音克隆]
---

# 小米MiMo语音克隆工作流

## 核心流程

### 1. 寻找参考音频
- **YouTube/Bilibili**：搜索访谈、电台节目、采访视频
- **关键词**：`[人名] インタビュー 音声`、`[人名] interview audio`
- **优先级**：电台访谈 > 电视采访 > 纪录片旁白 > 歌曲念白
- **注意**：避免使用版权音乐，优先选择非商业用途的公开内容

### 2. 提取音频片段
```bash
# 安装工具
pip3 install yt-dlp

# 下载视频
yt-dlp -x --audio-format wav "视频链接"

# 截取片段（30秒为佳）
ffmpeg -i input.wav -ss 00:07:05 -to 00:07:35 -c copy output.wav
```

**关键参数**：
- 片段时长：15-60秒（推荐30秒）
- 格式：WAV或MP3
- 大小限制：Base64编码后不超过10MB

### 3. 调用语音克隆API

**支持的模型**：
| 模型ID | 功能 | 注意事项 |
|--------|------|----------|
| `mimo-v2.5-tts` | 预置音色 | 支持唱歌 |
| `mimo-v2.5-tts-voicedesign` | 文本设计音色 | 不支持唱歌/克隆 |
| `mimo-v2.5-tts-voiceclone` | 音频样本克隆 | 不支持唱歌/设计 |

**调用示例**：
```python
import base64
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("XIAOMI_API_KEY"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)

with open("reference.wav", "rb") as f:
    voice_base64 = base64.b64encode(f.read()).decode("utf-8")

completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "要合成的文本"}
    ],
    audio={
        "format": "wav",
        "voice": f"data:audio/wav;base64,{voice_base64}"
    }
)
```

**预置音色**（mimo-v2.5-tts）：
| 音色名 | 语言 | 性别 |
|--------|------|------|
| 茉莉 | 中文 | 女性 |
| 冰糖 | 中文 | 女性 |
| 苏打 | 中文 | 男性 |
| 白桦 | 中文 | 男性 |

### 4. 配置两级TTS系统

**方案**：默认音色 + 多对话语音克隆

```yaml
# config.yaml
tts:
  provider: xiaomi
  xiaomi:
    model: mimo-v2.5-tts
    voice: 茉莉  # 默认音色
```

**创建两个脚本**：
1. `default_tts.py` - 默认音色脚本
2. `deep_conversation_tts.py` - 多对话场景语音克隆脚本

### 5. 音频标签控制（高级）

**风格标签格式**：`(风格)文本内容`
- 基础情绪：开心/悲伤/愤怒/平静
- 整体语调：温柔/高冷/活泼/深沉
- 音色定位：磁性/醇厚/清亮/甜美

**音频标签**：在文本中插入控制标签
- 吸气/深呼吸/叹气
- 笑/轻笑/冷笑/抽泣
- 语速控制

## Pitfalls

1. **Base64大小限制**：音频文件Base64编码后不能超过10MB，大文件需要截取更短片段
2. **API Key配置**：必须在`.env`文件中正确设置`XIAOMI_API_KEY`
3. **模型版本更新**：MiMo-V2-Pro/Omni将于2026.6.30下线，需切换到V2.5系列
4. **参考音频质量**：选择清晰、无背景音乐的纯人声片段效果最佳
5. **openai模块**：需要`pip3 install openai`安装依赖
6. **yt-dlp路径问题**：在Python 3.9环境下，`yt-dlp`可能不在PATH中，需要手动指定路径（如`/Users/libing/Library/Python/3.9/bin/yt-dlp`）或通过`python3 -m yt_dlp`调用
7. **API Key环境变量**：在shell中直接`export XIAOMI_API_KEY=xxx`后调用Python脚本可能失败，建议在Python代码中用`os.environ.get("XIAOMI_API_KEY")`读取，或使用`dotenv`库加载`.env`文件
8. **config.yaml的voice字段**：要使用自定义克隆的音频作为默认音色，voice字段需要包含完整的`data:audio/wav;base64,...`格式，不能只写文件名
9. **音频片段选择**：参考音频中应避免包含背景音乐、多人对话或噪音，选择15-60秒的纯人声片段效果最佳
10. **VoiceClone无状态设计**：`mimo-v2.5-tts-voiceclone`模型每次请求都需要传参考音频（Base64），**不能保存voice ID复用**。这是API设计限制，不是bug
11. **✅ 已解决：Cron任务可用voiceclone**：通过创建Hermes TTS插件`mimo-clone`（`~/.hermes/plugins/tts/mimo-clone/`），将voiceclone封装为TTS Provider，内置`text_to_speech`工具可直接使用克隆声音。config.yaml配置`provider: mimo-clone`即可。Cron任务（早报等）自动使用克隆声音，无需Python脚本
12. **Token Plan端点可用于TTS**：`XIAOMI_API_KEY`（Token Plan格式，`tp-coz...`）可以用于TTS克隆调用，端点为`https://token-plan-cn.xiaomimimo.com/v1`。不需要单独的MIMO_API_KEY
13. **mimo-clone插件配置**：config.yaml中添加`mimo-clone`配置段，指定`voice_sample`（参考音频路径）和`model`（mimo-v2.5-tts-voiceclone），然后设置`tts.provider: mimo-clone`
14. **插件加载验证**：Gateway重启后必须检查日志确认插件加载成功：`hermes logs 2>/dev/null | grep "registered TTS provider"`，应看到`Plugin 'mimo-clone' registered TTS provider: mimo-clone`。如果看不到此日志，说明插件未被发现（检查plugins.enabled列表）或is_available()返回False（检查API Key读取）
15. **⚠️ 插件必须显式启用（2026-06-25 验证）**：用户安装的插件（`~/.hermes/plugins/`）必须在`config.yaml`的`plugins.enabled`列表中添加`tts/mimo-clone`，否则插件不会被加载，TTS会fallback到默认的Edge/小米预置音色（茉莉）。

**启用命令：**
```bash
hermes plugins enable tts/mimo-clone
```

**症状：** config.yaml中写了`tts.provider: mimo-clone`，但生成的音频仍是Edge TTS的茉莉音色。检查tts_registry会发现`get_provider("mimo-clone")`返回None。

**诊断链路：**
```
text_to_speech("你好")
  → _get_provider() → "mimo-clone"  ✅ 配置正确
  → _dispatch_to_plugin_provider()
    → tts_registry.get_provider("mimo-clone") → None  ❌ 插件未注册
    → 回退到 DEFAULT_PROVIDER = "edge"
    → Edge TTS zh-CN-XiaoxiaoNeural 茉莉音色
```

**修复后验证：**
```bash
hermes plugins enable tts/mimo-clone
hermes gateway restart
# 检查插件注册
hermes logs 2>/dev/null | grep "registered TTS provider"
# 应看到: Plugin 'mimo-clone' registered TTS provider: mimo-clone
```
16. **参考音频路径管理**：参考音频应放在不会被清理的目录（如`/Users/libing/Desktop/中岛美雪语音克隆/`），生成的语音输出到定期清理的子目录（如`定期清除/`）

## 验证步骤

1. 测试预置音色：使用`mimo-v2.5-tts`模型
2. 测试语音克隆：使用短文本测试参考音频
3. 检查生成的WAV文件大小和时长

## MiMo生态系统

详见 `references/mimo-skills-ecosystem.md`，包含：
- MiMo-Skills安装位置和功能（唱歌/方言/导演模式/音色设计/音色克隆）
- MiMo-Code（AI代码助手）和MiMo-V2-Flash（旗舰推理模型）信息
- API端点对比（Token Plan vs MiMo开放平台）
- 调用示例

## 已集成的自定义克隆脚本

### 中岛美雪声音克隆（MiMo-Skills集成版）

**位置**：`~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/scripts/nakajima_clone.py`
**参考音频**：`/Users/libing/Desktop/中岛美雪语音克隆/nakajima_miyuki.wav`（保留目录，不清理）
**生成语音输出**：`/Users/libing/Desktop/中岛美雪语音克隆/定期清除/`（定期清理）

**使用方法**：
```bash
# 设置API Key
export XIAOMI_API_KEY=$(grep "^XIAOMI_API_KEY=" ~/.hermes/.env | cut -d= -f2- | tr -d "'\"")

# 运行克隆
python3 ~/.hermes/skills/mimo-skills/skills/mimo-v2-5-tts/scripts/nakajima_clone.py \
  "要说的文本" \
  ~/Desktop/中岛美雪语音克隆/定期清除/output.wav \
  "风格指令（可选）"
```

**创建自定义克隆脚本的模式**：
1. 在保留目录（如`/Users/libing/Desktop/中岛美雪语音克隆/`）存放参考音频
2. 在 `scripts/` 创建专用脚本，使用 `XIAOMI_API_KEY` + Token Plan端点
3. 脚本自动查找参考音频
4. 生成的语音输出到定期清理的子目录

## API文档参考

- 官方文档：https://platform.xiaomimimo.com/docs/zh-CN/usage-guide/speech-synthesis-v2.5
- 模型下线公告：https://platform.xiaomimimo.com/docs/updates/deprecate
