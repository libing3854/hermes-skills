# 参考音频收集工作流

## 资源搜索策略

### 搜索关键词组合
```
[名人名] インタビュー 音声
[名人名] interview audio
[名人名] 访谈 说话
[名人名] ラジオ インタビュー
[名人名] 纯享版  (Bilibili音乐)
[名人名] 现场 live (Bilibili音乐)
```

## 下载方法

### Bilibili下载（最常用）
```bash
# 必须带 --ignore-config（旧config可能有不兼容选项）
# 必须带 --cookies-from-browser chrome（否则HTTP 412）
yt-dlp --ignore-config -x --audio-format wav --audio-quality 0 \
  -o "output.%(ext)s" --cookies-from-browser chrome "URL"

# 多P视频指定分P
yt-dlp --ignore-config -x --audio-format wav -o "output.%(ext)s" \
  --cookies-from-browser chrome "https://www.bilibili.com/video/BVxxx?p=21"

# 仅下载第一个（避免下载整个播放列表）
yt-dlp --ignore-config --playlist-items 1 -x --audio-format wav \
  --cookies-from-browser chrome "URL"
```

**⚠️ yt-dlp配置陷阱**：`~/.config/yt-dlp/config`可能包含旧选项（如`--js-runtimes node`），导致`no such option`报错。始终加`--ignore-config`绕过。

**⚠️ Bilibili播放列表**：多P视频不加`--playlist-items`会下载全部分P，文件名冲突时后面的会覆盖前面的。明确指定p=N或用`--playlist-items 1`。

### YouTube下载
```bash
yt-dlp -x --audio-format wav -o "output.%(ext)s" "URL"
```

## 音频截取

### 标准流程
```bash
# 1. 截取指定时间段（16kHz/16bit/mono，语音克隆标准格式）
ffmpeg -i input.wav -ss 00:01:30 -to 00:02:00 -ar 16000 -ac 1 output.wav

# 2. 截取前N秒（用于配置文件中的DataURL参考音频）
ffmpeg -y -i input.wav -t 10 -ar 16000 -ac 1 output_short.wav

# 3. 检查音频信息
ffprobe -v error -show_entries format=duration,bit_rate output.wav
```

### 多版本截取（语音克隆切片策略）
为每首歌从不同位置切3-5段30秒切片，逐个测试：
```bash
# 跳过前奏（通常30-60秒），避开副歌拖长音部分
ffmpeg -i song.wav -ss 01:00 -to 01:30 -ar 16000 -ac 1 slice_1.wav
ffmpeg -i song.wav -ss 02:30 -to 03:00 -ar 16000 -ac 1 slice_2.wav
ffmpeg -i song.wav -ss 04:00 -to 04:30 -ar 16000 -ac 1 slice_3.wav
```

**⚠️ 切片位置影响克隆质量**：
- 前奏/间奏：可能有乐器残留，不适合
- 副歌长音：会导致克隆语音拖沓拉长
- 主歌中段（跳过前30秒）：通常最合适
- 每首歌多切几段，用户会指定"用哪个"，未选用的归档到`unused/`

## 人声分离

从歌曲中提取纯人声用于克隆。详见[vocal-separation.md](vocal-separation.md)。

```bash
# 安装
pip3 install demucs soundfile

# 分离（两轨：人声 + 伴奏）
demucs --two-stems=vocals -o . --mp3 song.wav

# 输出：htdemucs/<歌名>/vocals.mp3
```

**⚠️ 必须装soundfile**：否则torchaudio报backend错误。用`--mp3`比wav更稳定。

## 质量检查

### 检查清单
- [ ] 人声清晰，无背景音乐
- [ ] 无明显噪音或杂音
- [ ] 时长15-60秒（克隆参考音频10秒也够用）
- [ ] 说话/唱歌内容连贯
- [ ] 音量适中

## 工作目录结构

```
~/Desktop/[名人名]语音克隆/
├── 原始音频/
│   ├── 歌曲1.wav
│   └── 歌曲2.wav
├── 人声/
│   ├── 歌曲1_vocals.mp3
│   └── 歌曲2_vocals.mp3
├── 切片/
│   ├── slice_1.wav (01:00-01:30)
│   ├── slice_2.wav (02:30-03:00)
│   └── slice_3.wav (04:00-04:30)
└── 生成结果/
    ├── normal.wav
    ├── shenqing.wav
    └── aishang.wav
```
