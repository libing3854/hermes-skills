# 自动修复-审核循环脚本模板

## 跟踪文件模板（放在工作目录下）

```json
{
  "round": 1,
  "max_rounds": 3,
  "issue_history": {},
  "write_task": "t_xxx",
  "current_fix_task": null,
  "current_review_task": null,
  "phase": "write",
  "status": "running"
}
```

## 字段说明

| 字段 | 值 | 说明 |
|------|-----|------|
| round | 1-3 | 当前轮次（修复轮次，写作不算） |
| max_rounds | 3 | 最大轮次（超过后问用户） |
| issue_history | {} | 问题→连续未解决轮次计数 |
| write_task | t_xxx | 初始写作任务ID（仅第一批使用） |
| current_fix_task | t_xxx | 当前修复任务ID |
| current_review_task | t_xxx | 当前审核任务ID |
| phase | write/review/fix | 当前阶段：write=等写作完成，review=等审核，fix=等修复 |
| status | running/stuck/all_passed/xxx_failed | 循环状态 |

## 质量检查阈值（可按项目调整）

```python
# 字数
HANZI_MIN = 4500
HANZI_MAX = 6000

# 禁用词（必须为0）
BANNED_WORDS = ['深吸一口气', '仿佛', '不由得']

# 高频词（每章≤N次）
HIGH_FREQ_LIMITS = {
    '某种': 3,
    '一种': 3,
    '微微': 3,
    '如同': 3,
}

# 断路器：同一问题连续N轮未解决
CIRCUIT_BREAKER = 3
```

## Cron Job 配置

```python
cronjob(
    action='create',
    name='修复审核循环监控',
    script='fix_review_loop.py',  # 文件名，不含路径
    no_agent=True,                 # 纯脚本，不消耗LLM
    schedule='every 5m',
    deliver='local'                # 不推送，避免刷屏
)
```

## 任务创建要点

### 修复任务（assignee: shanli）
```
hermes kanban create "修复-X章-R{round}" \
  --assignee shanli \
  --workspace "dir:/path/to/chapters" \
  --body "$(cat body.txt)"
```

### 审核任务（assignee: lili）
```
hermes kanban create "审核-X章-R{round}" \
  --assignee lili \
  --body "$(cat body.txt)"
```

### 订阅通知（每个新任务都必须）
```python
def subscribe_task(task_id):
    run(f"""sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs 
        (task_id, platform, chat_id, thread_id, user_id, notifier_profile, created_at, last_event_id) 
        VALUES ('{task_id}', 'qqbot', '54D8D2AB6A48EE35127DD0F86081146A', '', 'binge', 'default', 
        strftime('%s','now'), (SELECT COALESCE(MAX(id),0) FROM task_events));" """)
    run(f'hermes kanban dispatch --max 1 2>/dev/null')
```

## 批次间脚本复用（快速派发下一批）

当用户说"继续下一批"或"直接下一批"时，不需要重新写脚本，复制+sed修改即可：

```bash
# 1. 复制基础脚本
cp ~/.hermes/scripts/fix_review_loop.py ~/.hermes/scripts/fix_review_loop_batchN.py

# 2. sed修改跟踪文件路径和章节范围
sed -i '' 's/\.fix_review_loop\.json/.fix_review_loop_batchN.json/' ~/.hermes/scripts/fix_review_loop_batchN.py
sed -i '' 's/305, 312/321, 328/' ~/.hermes/scripts/fix_review_loop_batchN.py
sed -i '' 's/第一批/第N批/g' ~/.hermes/scripts/fix_review_loop_batchN.py
sed -i '' 's/305-312章/321-328章/g' ~/.hermes/scripts/fix_review_loop_batchN.py

# 3. 创建新的跟踪文件
cat > /path/to/workdir/.fix_review_loop_batchN.json << 'EOF'
{"round":1,"max_rounds":3,"issue_history":{},"current_fix_task":null,"current_review_task":null,"phase":"write","status":"running","write_task":"t_xxx","batch":"321-328"}
EOF

# 4. 创建cron
cronjob(action='create', script='fix_review_loop_batchN.py', no_agent=True, schedule='every 5m', deliver='local')
```

**⚠️ 验证sed修改结果：**
```bash
grep -n "fix_review_loop\|check_chapters" ~/.hermes/scripts/fix_review_loop_batchN.py | head -5
# 确认跟踪文件路径和章节范围已更新
```

## 循环结束后标准清理

当循环状态变为 `all_passed` 或 `stuck` 后，必须执行：

```bash
# 1. 停掉cron job（避免空转）
cronjob(action='remove', job_id='xxx')

# 2. 归档已完成的看板任务
DONE_IDS=$(hermes kanban list 2>/dev/null | grep "✓" | awk '{print $2}')
for id in $DONE_IDS; do hermes kanban archive "$id" 2>/dev/null; done

# 3. 报告最终结果给用户
```

**不清理的后果：** cron job每5分钟空跑一次，浪费资源；看板积累大量done任务影响视觉。

## 注意事项

1. 脚本输出非空即推送，`[SILENT]` 表示无事发生
2. 修复任务用 `--workspace dir:` 确保文件持久化
3. 审核任务不需要 workspace（审核报告写到固定报告目录）
4. 跟踪文件路径硬编码在脚本中，不同项目需修改
5. 断路器触发后 cron job 应手动暂停，避免重复触发
6. 每个新批次的脚本必须验证sed修改结果（grep确认路径和范围）
7. **Gemini provider注意：** task body过长会导致空响应，修复任务body控制在200字以内
8. **Provider切换：** LongCat额度耗尽时，修复任务可改用 `--assignee shanliG`（Gemini），审核任务仍用 `--assignee lili`（DeepSeek）

## 阶段流转逻辑

```
write → 完成 → 创建审核任务 → review
review → 完成 → 检查质量 → 全部达标？→ all_passed
                      ↓ 有问题
                 记录问题历史 → 创建修复任务 → fix
fix → 完成 → 检查质量 → 全部达标？→ all_passed
                  ↓ 有问题
             创建审核任务 → review（round++）
```

**关键：每个阶段完成后必须：**
1. 更新 `phase` 字段
2. 更新对应的任务ID字段
3. 调用 `subscribe_task` 订阅新任务通知
4. 调用 `hermes kanban dispatch --max 1` 派发新任务
