---
name: health-daily-drink-water
category: productivity
version: 5.7
description: 健康每日提醒：每20分钟提醒冰哥喝水+久坐缓解+用眼保护。纯Python脚本版，零token消耗。
---

# 健康每日-喝水 (Health Daily - Drink Water)

> **2026-05-25 更新：冰哥的 cron 已迁移为纯脚本模式（no_agent=true）**
>
> cron 当前使用 `~/.hermes/scripts/health_daily.py`（纯 Python 脚本，无 LLM 调用），
> 每 20 分钟通过 stdout 投递到 QQ Bot。脚本做时间计算、农历转换、动作轮换，零 token 消耗。
> oMLX 的 Huihui-Qwen3.5-4B 仅有 32K 上下文不够装技能文档，LM Studio 的 8B 又太慢（405s/次），
> 最终用纯脚本方案解决。
>
> 本技能文档保留以备 agent 模式参考。

## 🏗 架构（v6.1 — 纯脚本）

本技能已从 LLM Agent（500+行SKILL.md + delegate_task）重构为 **纯 Python 脚本 + no_agent cron**：

```
cron (*/20 9-19, no_agent=true, deliver=qqbot)
  └─ scripts/health_daily.py  ← stdout = 投递消息
```

- **零 token 消耗**：脚本运行约 0.3s，无 LLM API 调用
- **零上下文问题**：无 prompt 长度限制
- **零调度开销**：no_agent=true，cron 直接跑脚本

## ⚙️ 配置

```bash
cronjob action=update job_id=$JOB_ID \
  schedule="*/20 9-19 * * *" \
  script=health_daily.py \
  no_agent=true \
  deliver=qqbot
```

脚本路径：`~/.hermes/scripts/health_daily.py`
投递渠道：qqbot（stdout 即消息）

## 📝 能力范围

- 时间计算（公历+农历+时钟，依赖 `zhdate` 库，无则用简版农历）
- 久坐动作轮换（17个，按时间槽 `slot % 17`）
- 用眼提醒轮换（14个，按时间槽 `slot % 14`）
- 新闻时间判断（11:00/19:00 输出新闻占位符）

**不支持/未实现**（纯脚本限制）：
- ❌ 实时新闻抓取（需 LLM agent 的 web_search 工具）
- ❌ session_search 去重（需 Hermes API）
- ❌ TTS 音频生成
- ❌ 新闻领域轮换

## 🐛 已知问题

### 模型上下文超限（旧版 agent 模式）
在 agent 模式下（v5.x 及之前），oMLX 原生模型 Huihui-Qwen3.5-4B 仅有 32K 上下文窗口（`max_context_window=32768`），但 skill 文档+prompt 合计约 35K tokens，导致 `HTTP 400: Prompt too long`。

**修复**（如果切回 agent 模式）：
1. 修改 `~/.omlx/settings.json` → `sampling.max_context_window: 43008`（42K）
2. 重启 oMLX 服务
3. 或改用 `deepseek-v4-flash`（128K 上下文）

### 调度器卡死
当某轮 cron 失败后，调度器可能停止调度后续轮次：
- `next_run_at` 未推进，连续数小时无执行
- **修复**：重启 gateway（`launchctl stop ai.hermes.gateway && launchctl start ai.hermes.gateway`）

## 📂 文件

- `scripts/health_daily.py` — 主执行脚本
- `references/legacy-agent-mode.md` — 旧版 agent 模式的完整文档（含 session_search 去重、新闻轮换、FTS5 偏差等历史内容）
