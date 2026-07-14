# 人声分离参考

## demucs 安装与使用

### 安装
```bash
pip3 install demucs soundfile
```
`soundfile`是必须的，否则torchaudio报backend错误。

### 基本用法
```bash
# 两轨分离（人声 + 伴奏）
demucs --two-stems=vocals -o . --mp3 input.wav

# 输出目录：htdemucs/<歌名>/
#   vocals.mp3    ← 人声
#   no_vocals.mp3 ← 伴奏
```

### 已知问题
1. **torchaudio backend错误**：`pip3 install soundfile`解决
2. **wav保存失败**：用`--mp3`输出更稳定
3. **默认模型变更**：htdemucs是默认模型，有时比旧模型差，可用`-n mdx_extra_q`回退

### 后处理
分离后的mp3可直接用于语音克隆参考音频。如需wav：
```bash
ffmpeg -y -i vocals.mp3 -ar 16000 -ac 1 output.wav
```

## 在线工具（备用）
- vocalremover.org - 被Cloudflare拦截，自动化浏览器无法通过
- lalal.ai - 付费，质量更高
- 如需使用在线工具，让用户在本地浏览器手动操作
