# 闪莉 (shanli) Profile — 历史经验教训

从 2026-05-24 至 2026-05-28 的 30+ 个历史会话中提取。

## 已修复的问题

| # | 问题 | 根因 | 解决方案 | 日期 |
|:-:|:-----|:-----|:---------|:-----|
| 1 | 401 认证失败 | profile .env 用 `***` 占位符 | LongCat api_key 硬编码到 config.yaml | 05-26 |
| 2 | 模型解析到错误 provider | profile 无 config.yaml → 解析到 custom/openrouter 空模型 | 创建完整 config.yaml（含所有 provider） | 05-26 |
| 3 | 金融看板 cron 路径错误 | `expanduser("~")` 在 cron 环境解析到 profile home | 所有脚本用绝对路径 | 05-27 |
| 4 | vision 路由失败 (400) | vision provider=auto → deepseek 不支持多模态 | 显式设置 `auxiliary.vision.provider: longcat` | 05-28 |
| 5 | 看板规范不起效 | 文件内容与 model_selector plugin 功能重复 | 删除文件，model_selector 全权负责 | 05-26 |
| 6 | model_selector 签名 bug | dispatch 传参方式与 handler 签名不匹配 | 加 `**kwargs` 和 `*args` 吸收多余参数 | 05-27 |

## 已知限制（非 bug）

| # | 问题 | 说明 | workaround |
|:-:|:-----|:-----|:-----------|
| 7 | delegate_task model 参数无效 | Hermes 上游从未实现 model 参数（5 层静默丢弃） | delegate-duo 插件切换 delegation |
| 8 | profile gateway 掉线 | active_profile 切换导致非活跃 profile 的 gateway 停掉 | `hermes gateway start --profile shanli` |

## 配置陷阱

| # | 陷阱 | 症状 | 预防 |
|:-:|:-----|:-----|:-----|
| 9 | failure_limit=2 太低 | 免费模型池连续 2 次失败 → 任务被 blocked | 提升到 5 |
| 10 | 长篇任务单 worker 超限 | 55-65 章写作任务，慢模型 ~16 t/s 无法在 2h 内完成 → 96 次协议违规崩溃 | 分批创建，每批 5-10 章 |

## 诊断速查

```
# 看板 worker 崩溃诊断
hermes kanban log <task_id> | tail -30

# 常见日志模式对应修复：
# "HTTP 401" → api_key 过期/***占位符 → 更新 config.yaml 中的 api_key
# "HTTP 400 No models provided" → profile 无 config.yaml → 创建 config.yaml
# "protocol violation" (60s 退出) → 任务太大或 auth 错误 → 先看 log，不要直接加 runtime
# "Provider: custom  Model: LongCat-2.0-Preview" → profile 无 config.yaml → 同上
# "Provider: openrouter  Model: (empty)" → profile 无 config.yaml → 同上

# gateway 状态
hermes profile list                      # 看 gateway 是否 running
hermes kanban assignees                  # 看 assignee 是否可 spawn
grep "active_profile" ~/.hermes/.env     # 当前活跃 profile
```
