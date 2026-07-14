# TTS 语音集成到定时任务的模式

> 发现时间：2026-05-28
> 场景：给现有定时任务添加 TTS 语音发送功能

## 背景

冰哥要求给所有发送消息的定时任务都加上 TTS 语音版本：
- **每日早报 + 每日喝水** → 完整语音（天气+新闻+物价+黄历+星座+寄语）
- **金融看板、AI周报、GitHub周报** → 摘要/简短版（1500字符）
- **健康每日-喝水、闪莉归档**（no_agent 脚本模式）→ 跳过

## 修改模式

### 1. Agent 模式任务（可调用 text_to_speech）

在技能文件的执行流程末尾添加 TTS 步骤：

```markdown
## TTS 语音摘要（简短版）
在发送文本/HTML之后，调用 `text_to_speech` 生成语音：
- **输入文本**：精简为口语化播报稿（控制在 1500 字符以内）
- **语气**：[匹配任务定位的风格]
- **保存路径**：`~/voice-memos/` 目录下
- **文件命名**：`[prefix]_YYYYMMDD_HHMM.mp3`
```

### 2. No_agent 脚本模式任务（无法调用 text_to_speech）

两种方案：
- **方案A**：改为 agent 模式（消耗 token）
- **方案B**：在 Python 脚本中用 `edge-tts` 库生成音频（不消耗 token）

**决策依据**：高频任务（每20分钟）用方案B，低频任务（每天1次）可用方案A。

### 3. 输出交付（MEDIA: 标签）

**Agent 模式任务：** 在输出文本末尾追加 `MEDIA:~/voice-memos/[filename].mp3`。Gateway 会自动拦截此标签，将音频作为语音消息发送到 Telegram/QQ。

```
[文本内容]

MEDIA:~/voice-memos/morning_report_20260528_0800.mp3
```

**⚠️ 关键：** 输出模板末尾必须包含 `MEDIA:` 行，否则 agent 照模板输出时会漏掉，导致音频生成了但从未发送。详见 `references/media-tag-delivery.md`。

## 字符限制

| 类型 | 限制 | 适用场景 |
|------|------|---------|
| 完整版 | 3000 字符 | 每日早报等需要完整内容的任务 |
| 简短版 | 1500 字符 | 金融看板、周报等需要摘要的任务 |

## 文件命名规范

| 任务 | 命名格式 | 说明 |
|------|---------|------|
| 每日早报 | `morning_report_YYYYMMDD_HHMM.mp3` | 带时戳 |
| 金融看板 | `finance_brief_YYYYMMDD_HHMM.mp3` | 每天两次需时戳 |
| AI周报 | `ai_weekly_brief_YYYYMMDD.mp3` | 周报无需时戳 |
| GitHub周报 | `github_trending_brief_YYYYMMDD.mp3` | 周报无需时戳 |

## 审核要点

添加 TTS 后需检查：
1. TTS 步骤是否编入编号执行流程（不会被跳过）
2. **输出模板末尾是否包含 `MEDIA:~/voice-memos/...mp3` 行**（必须有，否则音频不会发送）
3. 自检清单是否添加 MEDIA: 标签检查项
4. 字符限制、路径、命名规范是否一致
5. 输出红线是否不再禁止 MEDIA: 标签（常见错误：将 MEDIA: 也列入禁止列表）

## 已修改的技能文件

| 技能 | 修改内容 |
|------|---------|
| daily-morning-report | 第九阶段改为完整语音播报 + 音频规范更新 + 自检清单增加3项 |
| financial-dashboard | 完整推送流程增加步骤5 + 语音版提示 |
| ai-weekly-report | 渲染流程增加步骤5 + 语音版提示 |
| github-trending-analyzer | 主工作流增加第五步 + 语音版提示 |
