# TTS/Voice Cron Job Diagnostic Checklist

> 场景：用户报告"带语音的定时任务没有执行"
> 创建时间：2026-05-28
> 最后更新：2026-06-10（新增 media_delivery_allow_dirs 诊断步骤）

## 诊断四步法

### Step 1: 哪些 cron job 带语音？

```bash
hermes cron list  # 列出所有 cron job
```

检查每个 job 的 `skills` 字段 — 包含 `daily-morning-report` 等含 TTS 流程技能的才可能有语音。
注意区分：
- `no_agent=true` 的任务 → **无法使用 `text_to_speech`**（TTS 是 LLM 工具）
- 有 skills 但技能本身不含 TTS 步骤的 → 纯文本任务

### Step 2: 音频文件是否生成？

```bash
ls -lt ~/voice-memos/ | head -20
```

按任务名过滤：
```bash
ls -lt ~/voice-memos/ | grep -E "早报|morning|finance|weekly" | sort -k6,7
```

关键判断：
- ✅ 有今天的 .mp3/.ogg → **TTS 生成正常**
- ❌ 没有今天的文件 → TTS 生成失败或被跳过
- ⚠️ 有文件但日期不对 → 可能是缓存/旧文件

### Step 3: Cron session 日志

通过 session_search 查找最近一次执行记录：
```
session_search(query="早报 TTS 语音", session_id="cron_xxx_yyy", sort="newest")
```

在 assistant 消息中找 `text_to_speech` 工具调用：
- 有调用 → TTS 执行了，检查返回结果
- 没有调用 → agent 可能跳过了 TTS 步骤（常见原因：超时、token 耗尽、技能未加载）
- 调用报错 → 查看错误信息

### Step 4: 生成 ≠ 交付！

音频文件生成了不代表用户收到了。检查：
- `deliver` 配置是否正确（如 `telegram:xxx,qqbot`）
- `last_delivery_error` 是否为 null
- 目标平台是否支持音频附件（Telegram ✅，QQ 视情况）
- `MEDIA:` 标签是否正确嵌入最终输出

## 常见问题速查

| 症状 | 原因 | 修复 |
|------|------|------|
| 音频文件没有生成 | no_agent=true，无 LLM 调 TTS | 改为 agent 模式，或脚本内嵌 edge-tts |
| 音频文件生成了但没收到 | deliver 配置或 MEDIA 标签问题 | 检查 deliver target 和输出格式 |
| TTS 调用报错 | TTS provider 不可用 | 检查 ~/.hermes/config.yaml TTS 配置 |
| 之前有语音现在没有 | 技能版本更新后 TTS 步骤被移除 | 对比技能版本，确认 TTS 步骤仍在 |
| skills 为空 | cron job 未加载技能 | 更新 cron job 确保 skills 非空 |
| 音频生成了但没发出去，MEDIA 标签正确 | `media_delivery_allow_dirs` 为空 | 添加语音目录到允许列表并重启 Gateway（见下方） |

### media_delivery_allow_dirs 配置陷阱（2026-06-10）

**症状**：音频文件正常生成，`MEDIA:` 标签正确输出，但 Telegram/QQ 收不到语音。

**根因**：`~/.hermes/config.yaml` 中 `gateway.media_delivery_allow_dirs` 默认为 `[]`（空数组），Gateway 拒绝发送任何目录下的媒体文件。

**诊断**：
```bash
grep media_delivery_allow_dirs ~/.hermes/config.yaml
# 如果显示 media_delivery_allow_dirs: [] → 这就是问题
```

**修复**：
```bash
hermes config set gateway.media_delivery_allow_dirs '["/Users/libing/voice-memos"]'
hermes gateway restart
```

**注意**：这是 Gateway 级别的安全限制，与技能配置、cron 配置、MEDIA 标签格式均无关。

## 健康喝水提醒的语音说明

健康喝水提醒（`health-daily-drink-water`）当前是 `no_agent=true` 纯脚本模式，**不包含 TTS**。
历史上的语音文件（如 `health_drink_20260525_1541.mp3`）是之前 agent 模式或手动触发时生成的。
如需恢复语音提醒，需要将任务改为 agent 模式并添加 TTS 步骤。
