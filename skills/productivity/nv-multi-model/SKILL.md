---
name: nv-multi-model
description: NVIDIA NIM + OpenRouter 双 Provider 多模型竞速 Ping 系统 —— 通过并发竞速+波峰波谷感知实现低延迟模型路由
version: 1.5.0
author: Lily
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [nvidia, multi-model, routing, latency, ping, racing]
    related_skills: [us-stock-daily-report, hermes-agent, financial-dashboard]
---

# NVIDIA + OpenRouter 双 Provider 多模型竞速 Ping 系统

## 概述

利用 NVIDIA build.nvidia.com 免费 API（20个可用模型）+ OpenRouter 免费模型（26个可用），通过**分组并发竞速**机制实现低延迟模型路由。核心思想：不选模型，全并发，谁快用谁。

## 架构

```
莉莉丝接任务 → 判断任务类型 → 读 ranking.json（最新延迟数据）
                              ↓
                     选候选池最低延迟的3个并发
                              ↓
                     🏁 谁先回来用谁，其余丢弃
                              ↓
                     全失败？ → deepseek-v4-flash 兜底
```

## 目录结构

```
~/.hermes/data/NVping/
├── tmp/              # 实时数据（每半小时更新）
│   ├── ping_A.json   # A组最新结果
│   ├── ping_B.json   # B组最新结果
│   ├── ranking.json  # 竞速排名（闪莉读取）
│   ├── groups.json   # 分组配置（每天动态调整）
│   ├── state.txt     # 下一轮组别（A/B交替）
│   └── health.json   # 健康检查
├── day/              # 日档案（保留90天）
├── week/             # 周总结（保留52周）
└── month/            # 月档案（保留24个月）
```

## Ping 机制

### 时间轴
```
00:00 ── Group A（~23个模型，含 NV + OpenRouter）
00:30 ── Group B（~23个模型，含 NV + OpenRouter）
01:00 ── Group A
...每半小时交替，每模型每小时ping一次
```

### 并发控制
```python
# NVIDIA: asyncio.Semaphore(10) 控制并发
# OpenRouter: asyncio.Semaphore(5) 控制并发（免费模型限速更严格）
# 约 46 个模型分两组，每组 2-3 秒完成
```

### API Key 有效期与存储
- **NVIDIA Key**: 到期日 2027-05-17，存储于 macOS Keychain 服务名 `nvidia_api_key`
- **OpenRouter Key**: 存储于 macOS Keychain 服务名 `openrouter_api_key`
- **读取 NVIDIA**: `security find-generic-password -w -s "nvidia_api_key"`
- **读取 OpenRouter**: `security find-generic-password -w -s "openrouter_api_key"`
- **更新**: `security add-generic-password -a "nvidia_nim" -s "服务名" -w "新key"`

### 并发限制实测
- NVIDIA: 15/30/50 并发测试结论保持不变
- OpenRouter 免费模型: **Semaphore(5)**，实测 10+ 并发触发 429 限速
- 安全并发数：NV ≤10，OpenRouter ≤5

### 数据文件权限
```bash
chmod 700 ~/.hermes/data/NVping/
chmod 600 ~/.hermes/data/NVping/tmp/*
```
```bash
# 写入 macOS Keychain
security add-generic-password -a "nvidia_nim" -s "nvidia_api_key" -w "nvapi-..."
# 读取
security find-generic-password -w -s "nvidia_api_key"
```

## 完整兜底链

```
⚡ 闪莉竞速（3模型并发） → 全失败 → deepseek-v4-flash 兜底
                ↓ 仍失败
         🚀 大莉（核弹模型）最终兜底

🐣 闪莉mimi竞速（3模型并发） → 全失败 → 🏠 小莉 本地处理
```

**大莉定位**：核弹模型（Pro），最贵但最强。仅当闪莉多组全失败时出动，日常不用。

## 排名依据

**费用 + 能力**综合排序，不是只看速度：
🏠小莉(免费) → 🐣闪莉mimi(免费) → ⚡闪莉(免费) → 🚀大莉(付费Pro, 核弹兜底)

## 模型分类（46个可用，含双Provider）

完整分类清单见 `references/model-classification.md`。

当前 Ping 系统覆盖 **25 个可用 NVIDIA NIM 模型**（2026-06-26 实测，53个候选中25个返回200）+ OpenRouter 免费模型。每日蛇形分组后去重，实际每轮 Ping 约 **25 个独特模型**。

**⚠️ 模型生命周期**：NVIDIA 会不定期下线旧模型ID（2026-06-12 大规模下线导致14天数据断档）。groups.json 的 `updated_at` 字段记录最后更新时间。模型列表过期时运行 `scripts/nv_model_test.py` 重新扫描可用模型。

### 🐣 闪莉mimi（小莉替补）- 15个
< 4B 或 <10B+响应<5s。小莉忙时顶替，高峰期首选。
兜底：→ 🏠 小莉（本地）

### 🚀 轻量模型（闪莉日常主力）- 20个
> 4B 且响应<5s。日常对话、搜索、看图。
兜底：→ deepseek-v4-flash

### 🧠 强模型（深度任务）- 4个
含于轻量中，nemotron-3-super-120b, llama-4-maverick, qwen3-next, dracarys-70b

## 竞速分组

| 组 | 候选池 | 并发 | 场景 |
|:--:|--------|:----:|------|
| ⚡ 闪电组 | 5个mimi最快的 | 3 | 简单任务/高峰期 |
| 🚀 标准组 | 6个轻量最快的 | 3 | 日常任务 |
| 🖼️ 视觉组 | 3个视觉模型 | 3 | 图片理解 |
| 🧠 深度组 | 3个强模型 | 3 | 深度推理 |

## 波峰波谷感知

```python
load_level = calc_load_level(avg_ms, baseline_ms)
# low(<0.8) → 低谷期，大模型放心用
# normal(<1.2) → 正常
# high(<2.0) → 高峰期，只用mimi
# spike(>=2.0) → 放弃NVIDIA，切小莉
```

## 动态分组（每天评估后执行）

蛇形算法：排名1→A, 2→B, 3→B, 4→A, 5→A, 6→B... 保证两组延迟均衡。
不稳定模型降级到 C 组（每4小时 ping 一次），恢复后重新加入。

## 数据流

### 每30分钟（Ping脚本：nv_ping.py）
1. 读 state.txt 确定组
2. 读 groups.json 获取该组模型列表
3. 从 macOS Keychain 读取 API Key（不硬编码）
4. 用 asyncio.Semaphore(10) 并发 ping 组内所有模型
5. 写入 ping_X.json（原始结果）
6. 更新 ranking.json（含按分类排序的 top_by_category + 健康状态）
7. 更新 health.json（最后成功时间、成功率、连续失败次数）
8. 翻转 state（A→B, B→A）
9. 检查 API Key 过期天数

### 每天00:00 → Telegram 日报（评估脚本：nv_daily_eval.py）

评估脚本完成后自动输出人类可读的摘要，通过 cronjob 的 `deliver: telegram:611807381` 配置投送到 Telegram。

**Cron 任务配置：**

```yaml
闪莉Ping每半小时:
  schedule: "0,30 * * * *"
  script: nv_ping.py
  no_agent: true
  deliver: local

闪莉每日归档评估:
  schedule: "0 0 * * *"
  script: nv_daily_eval.py
  no_agent: true
  deliver: telegram:611807381  # 投送到 Telegram
```

**SSL 证书验证（安全注意）：** 不要禁用验证。`ctx.check_hostname = False` 和 `ctx.verify_mode = ssl.CERT_NONE` 已修复为 `ssl.create_default_context()`。

**trend 计算常见错误：** `ms_arr[:4]` 是最早4条（older），`ms_arr[-4:]` 是最新4条（recent），切勿颠倒。
1. 合并当天48条记录 → day/YYYY-MM-DD.json
2. 计算每个模型：avg_ms / std_ms / min_ms / max_ms / success_rate / trend
3. 趋势判断逻辑：
   - improving: 最近4次比前4次快 >10%
   - degrading: 最近4次比前4次慢 >20%
   - unstable: success_rate < 80%
   - 其余为 stable
4. 蛇形重新分组 → 更新 groups.json（加 effective_from 时间戳防cron冲突）
5. 记录当天波峰波谷时段（peak_hours/off_peak_hours）
6. 检查 API Key 过期（30天/7天/1天触发告警）
7. 清理 >90 天的 day/ 文件

### 每周日 → week/ 总结
聚合7天日文档，生成周级别波峰波谷规律（工作日 vs 周末）。

### 每月1日 → month/ 归档
聚合当月周文档，清理 >52周 的 week/ 和 >24月 的 month/。

## 冷启动策略

- **前7天**：用全局平均延迟代替"同时段基线"
- **新模型前48小时**：标记 `baseline_collecting`，不参与竞速排名
- **7天后**：自动切换到正常基线模式

## 健康检查与告警

### health.json
```json
{
  "last_success": "2026-05-17 10:00",
  "last_failure": null,
  "success_rate_24h": 0.97,
  "consecutive_failures": 0,
  "current_status": "healthy"
}
```

### 触发条件
- last_success > 1小时 → 数据过期警告
- 连续6次 success_rate < 50% → 通知冰哥
- API Key < 30天 → 通知冰哥
- API Key < 7天 → 每天通知
- API Key 过期当天 → 紧急通知

## 脚本位置

```bash
~/.hermes/data/NVping/nv_ping.py           # Ping脚本
~/.hermes/data/NVping/nv_daily_eval.py     # 日评估脚本
~/.hermes/data/NVping/task_tracker.py      # 任务耗时追踪 + 模型切换建议
~/.hermes/scripts/nv_ping.py               # cron软链
~/.hermes/scripts/nv_daily_eval.py         # cron软链
~/.hermes/scripts/task_tracker.py          # cron软链
```

### 辅助工具
- `scripts/nv_model_test.py` — 批量测试当前可用的NVIDIA NIM模型（逐模型ping，输出可用清单）
- `references/current-model-inventory-20260626.md` — 当前可用模型清单（25个，含分类和延迟排名）

## 任务执行时间追踪系统（task_tracker.py）

**定位**：记录每次cron任务的执行耗时，根据历史数据+实时负载给出模型组切换建议（mimi/light/小莉）。

### 数据流

```
莉莉丝每次执行任务 → log_task(任务名, 模型组, 耗时ms)
                          ↓
              task_log.jsonl（累加追加，保留7天窗口）
                          ↓
        get_recommendation() → 读最近7天日志 + 当前ping负载
                          ↓
              task_recommend.json（cron任务读取使用）
                          ↓
              cron任务读 recommendations[任务名] 选模型组
```

### 输出格式（task_recommend.json）

```json
{
  "updated_at": "2026-05-17 22:27:43",
  "load_level": "high",
  "recommendations": {
    "每日早报": "mimi",
    "喝水提醒(新闻)": "mimi",
    "喝水提醒(普通)": "light"
  },
  "rationale": {
    "每日早报": "高负载 (high) → mimi 省时间",
    "喝水提醒(普通)": "短任务豁免 (<1.5s)"
  },
  "by_group_stats": {
    "每日早报": {"light": 2850}
  },
  "sample_counts": {},
  "config": {}
}
```

### v1.1 改进要点（2026-05-17）

| 改进 | 说明 | 参数 |
|------|------|------|
| 🔄 迟滞缓冲区 | 中位值(2500-3500ms)保持当前建议不变，避免震荡 | LIGHT_TO_MIMI=3500, MIMI_TO_LIGHT=2500 |
| 🌱 冷启动默认值 | 无历史数据的任务用 `DEFAULT_RECOMMENDATIONS` 兜底 | 默认 light |
| ⏰ 时间窗口过滤 | 只读最近7天的日志，旧数据不稀释新趋势 | LOG_WINDOW_DAYS=7 |
| 🏃 短任务豁免 | <1.5s的任务跳过切换逻辑，保持light | SHORT_TASK_THRESHOLD_MS=1500 |
| 🚨 Spike修正 | spike负载切"小莉"本地而非mimi（对齐规范） | — |
| 📊 决策追溯 | rationale字段记录每个建议的决策依据 | — |
| ⚙️ 自文档 | config输出当前所有阈值参数 + valid_groups | — |

### 决策优先级（get_recommendation → _decide_group）

```
1️⃣ 短任务豁免？(<1.5s)           → light
2️⃣ 无历史数据？                  → 冷启动默认值
3️⃣ 负载 spike？                  → 小莉（本地模型）
4️⃣ 负载 high？                   → mimi
5️⃣ 负载 low？                    → light
6️⃣ 正常负载 + 平均>3500ms？       → mimi
7️⃣ 正常负载 + 平均<2500ms？       → light
8️⃣ 正常负载 + 2500-3500ms(迟滞区) → 保持当前建议
```

### cron任务使用方式

```python
import json, os
rec = json.load(open(os.path.expanduser("~/.hermes/data/NVping/tmp/task_recommend.json")))
my_task = "每日早报"
group = rec["recommendations"].get(my_task, "light")
```

| 版本 | 日期 | 变更 |
|------|------|------|
| **1.5.0** | 2026-05-19 | 🆕 **OpenRouter 双 Provider** — 接入 27 个 OpenRouter 免费模型，nv_ping.py 支持双 base_url + 双 Keychain Key，nv_daily_eval.py 保留 provider 字段。🆕 Git 版本控制 — NVping 目录初始化 git，v1.4.0/v1.5.0 标签可回滚。🐛 **修复** — nv_daily_eval.py stats_list 缺失 provider 导致蛇形分组丢失 OpenRouter 模型。 |
| 1.4.0 | 2026-05-17 | 新增任务耗时追踪系统(task_tracker.py v1.1)、迟滞缓冲/冷启动/短任务豁免/时间窗口/Spike修正/决策追溯 |
| 1.3.1 | 2026-05-17 | 命名更正（莉闪→闪莉）、新增完整兜底链（大莉核弹）、cron去重、Telegram日报更新 |
| 1.0.0 | 2026-05-17 | 初始版本 |

## 运维坑

### NV模型kanban worker不兼容（2026-06-26）
**结论**：大多数NV免费模型在完整kanban worker上下文中无法工作，但Qwen3.5 122B例外。
- 简单对话中能理解 `work kanban task` 格式 ✅
- 但在系统prompt+工具+技能+任务的复杂上下文中迷失 ❌（除了Qwen3.5）
- 仅 **qwen/qwen3.5-122b-a10b** (916ms, 128K) 成功执行kanban ✅
- 手动chat和深度审核可用，不要用于kanban worker自动化
- nvlinshi profile配置要点：SOUL.md用闪莉风格、task_completion_guidance=null、agent配置精简
- 详见 `references/nv-profile-creation-guide.md`

### NV API未测速大模型ID（2026-06-26实测）
当前ping只覆盖25个中小模型。实测可用的大模型：
- ✅ `deepseek-ai/deepseek-v4-flash` 284B MoE 1M上下文 995ms
- ✅ `deepseek-ai/deepseek-v4-pro` 1M上下文 1101ms
- ✅ `qwen/qwen3.5-122b-a10b` 128K 916ms — **唯一kanban兼容**
- ❌ `z-ai/glm-5.1` 太慢(19831ms)
- ❌ `moonshotai/kimi-k2.5` 404
- ❌ `minimaxai/minimax-m2.7` 超时
- ❌ `nvidia/nemotron-3-ultra-550b-a55b` 超时

### SSL 证书验证泄露
**问题**：`ctx.check_hostname = False` + `ctx.verify_mode = ssl.CERT_NONE` 导致 MITM 攻击风险。
**修复**：删除这两行，直接用 `ssl.create_default_context()`。

### trend 计算颠倒
**问题**：`recent = sum(ms_arr[:4])`（取了最早4条）、`older = sum(ms_arr[-4:])`（取了最新4条）—— 完全反了。
**修复**：`older` 取前4条，`recent` 取后4条。

### 子代理 HTML 生成超时
200KB+ 文件通过 delegate_task 修改会超时（600s）。直接在文件上用 `patch` 工具改 CSS/JS 避免超时。

### groups.json 重复条目导致 API 浪费
**问题**：每日蛇形分组如果不去重，groups.json 中同一模型可能出现多次。每半小时 Ping 时会重复调用同一模型，每天浪费近千次 API 调用。

**修复**：在 `nv_ping.py` 的 `main()` 中添加 dedup 防护：
```python
seen = set()
deduped = []
for e in normalized_entries:
    key = (e["id"], e["provider"])
    if key not in seen:
        seen.add(key)
        deduped.append(e)
normalized_entries = deduped
```

### nv_daily_eval.py provider 字段丢失
**问题**：`evaluate_and_regroup()` 中 `stats_list` 构建时缺少 `provider` 字段，导致蛇形分组时 `s.get("provider", "nv")` 取默认值，OpenRouter 模型被错误分配到 NVIDIA 组。

**修复**：stats_list 的 append 中加入 `"provider": s.get("provider", "nv")`，蛇形分组输出改为 `{"id": s["model"], "provider": s.get("provider", "nv")}` 格式。

### groups.json 被清空导致 ping 死循环（2026-06-22，2026-06-26 彻底修复）

**触发链**：NVIDIA 模型下线 → 所有 ping 全部 404 → `nv_daily_eval.py` 每天0点运行 → `evaluate()` 发现所有模型 `ms=None`（无成功记录）→ `if not s["ms"]: continue` 跳过 → `sl` 列表为空 → `stable` 和 `unstable` 都为空 → `new_grouping` = `{"A": [], "B": []}` → 覆盖 groups.json → `nv_ping.py` 看到空分组 → "空组"退出 → 永远没数据 → 恶性循环。

**第一层修复（2026-06-22）**：在 `nv_ping.py` 添加 fallback——当 `groups[group]` 为空时从 `categories` 按 A/B 取模型：
```python
model_entries = groups["groups"].get(group, [])
if not model_entries:
    cats = groups.get("categories", {})
    pool_keys = ["mimi", "light"] if group == "A" else ["deep", "vision"]
    for ck in pool_keys:
        model_entries.extend(cats.get(ck, []))
```

**第二层修复（2026-06-26，根因修复）**：在 `nv_daily_eval.py` 添加空分组保护——`new_grouping` 为空时不覆盖 `groups.json`：
```python
new_a = ev.get("new_grouping", {}).get("A", [])
new_b = ev.get("new_grouping", {}).get("B", [])
if not new_a and not new_b:
    print("  ⚠️ 新分组为空，跳过 groups.json 覆盖")
else:
    cg["groups"] = ev["new_grouping"]
    with open(os.path.join(TMP,"groups.json"),"w") as f: json.dump(cg,f)
```

**教训**：
- 空分组意味着数据不足而非"没有模型"，eval 不能无条件覆盖分组
- `evaluate()` 中的 `if not s["ms"]: continue` 是一柄双刃剑：正常过滤噪声，但全部失败时判所有模型为无数据
- 两层防护互补：ping fallback 让系统在无分组时自愈，eval 保护防止再次清空

### nv_ping.py URL 被拼两次（2026-06-26 修复）
**问题**：`API_URL` 已包含 `/v1/chat/completions`，但 `ping()` 函数中又追加了 `/chat/completions`，导致实际请求 URL 为 `https://integrate.api.nvidia.com/v1/chat/completions/chat/completions`——全部返回 404。
**症状**：所有模型 ping 结果为 HTTP 404，但 curl 直接测试同一模型却返回 200。
**修复**：`nv_ping.py` 第26行 `f"{API_URL}/chat/completions"` 改为 `API_URL`。
**根因**：早期 API_URL 只定义到 `/v1`，后来改为完整路径但 `ping()` 函数未同步更新。
**教训**：修改 API_URL 常量时，必须全局搜索所有引用该变量的代码。

### NIM 端点大面积 404/410（2026-06-22）
**现象**：NVIDIA NIM 上多个模型返回 HTTP 404（不存在）或 410（已下线），包括 deepseek-v3.1-terminus、deepseek-v3.2、kimi-k2-thinking、qwen3-coder-480b 等。Google Gemini 返回 429（限流）。

**处理**：这些是模型生命周期变更，不是代码 bug。需要定期更新 `groups.json` 的 categories 列表，移除已下线模型、添加新上线模型。更新后 groups.json 的 `updated_at` 和 `effective_from` 字段会记录变更时间。

## 参见

- `references/subagent-html-generation-pitfalls.md` — 用子代理操作大型HTML文件的坑与解决方案
- `references/model-list-update-20260622.md` — 2026-06-22 模型列表大更新（移除11个404/410模型，新增9个可用模型）
