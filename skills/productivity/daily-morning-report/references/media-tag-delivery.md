# MEDIA: 标签音频交付机制

> 发现时间：2026-05-28
> 最后更新：2026-06-10（新增 media_delivery_allow_dirs 陷阱）
> 场景：cron 任务生成了音频文件但 Telegram/QQ 未收到语音

## 问题

技能 v3.5 的"输出红线"禁止输出任何音频路径行（包括 `MEDIA:` 标签），但 Hermes Gateway 需要 agent 在输出中写 `MEDIA:/path/to/file` 才能拦截并发送音频附件。

**结果：** 音频文件正常生成（~/voice-memos/morning_report_20260528_0800.mp3, 1.2MB），但从未发送到 Telegram。

## 修复（v3.5 → v3.6）

在技能的 **6 处** 同步更新规则：

| # | 位置 | 修改 |
|---|------|------|
| 1 | 输出红线 | 禁止→**强制要求** `MEDIA:` 标签 |
| 2 | 输出模板末尾 | 新增 `MEDIA:~/voice-memos/morning_report_YYYYMMDD_HHMM.mp3` |
| 3 | 音频规范 | "不包含路径"→"必须附加 MEDIA:" |
| 4 | Cron 任务模式 | 补充 MEDIA: 说明 |
| 5 | 交付渠道差异 | QQ 描述改为"Gateway 统一处理" |
| 6 | 自检清单 | 新增 MEDIA: 检查项 |

## 关键教训

**模板必须与规则一致。** 仅更新规则文字而不动模板，agent 照模板输出时仍然会漏掉。模板是 agent 的直接参照，改规则必须同步改模板。

## MEDIA: 标签工作原理

```
Agent 输出文本 + MEDIA:/path/to/audio.mp3
        ↓
Gateway 拦截 MEDIA: 标签
        ↓
Telegram → 作为语音消息附件发送
QQ → 作为音频附件发送
CLI 终端 → 原样显示文本（MEDIA: 不被拦截）
```

## ⚠️ media_delivery_allow_dirs 配置陷阱（2026-06-10）

**问题**：音频文件生成了、`MEDIA:` 标签也正确输出了，但 Gateway 仍然不发送音频。

**根因**：`~/.hermes/config.yaml` 中 `gateway.media_delivery_allow_dirs` 默认为空数组 `[]`，Gateway 不允许发送任何目录下的媒体文件。

**修复**：
```bash
hermes config set gateway.media_delivery_allow_dirs '["/Users/libing/voice-memos"]'
hermes gateway restart  # 必须重启才生效
```

**验证**：
```bash
grep "media_delivery_allow_dirs" ~/.hermes/config.yaml
# 应显示: media_delivery_allow_dirs: '["/Users/libing/voice-memos"]'
```

**注意**：这是 Gateway 级别的安全限制，与技能或 cron 任务配置无关。即使 `MEDIA:` 标签正确，如果目录不在允许列表中，音频也不会发送。

## 调试流程

当用户报告"语音没收到"时：

1. **查 cron job** — `cronjob(action='list')` 确认任务存在且 last_status
2. **查音频文件** — `ls -lt ~/voice-memos/` 确认文件是否生成
3. **查 session 日志** — `session_search(query="TTS text_to_speech")` 确认 TTS 调用是否成功
4. **查技能规则** — 检查技能的输出模板末尾是否有 `MEDIA:` 行
5. **查 deliver 配置** — 确认 cron job 的 deliver 目标正确
6. **查 media_delivery_allow_dirs** — `grep media_delivery_allow_dirs ~/.hermes/config.yaml` 确认语音目录在允许列表中，若为空需添加并重启 Gateway
