# 看板任务监控协议

> 实战来源：2026-06-09 写作批次监控

## 监控间隔

| 闪莉模型 | 建议间隔 | 原因 |
|---------|---------|------|
| LongCat（性能弱） | 5分钟 | 写5章约需10-15分钟 |
| 闪莉mimi（轻量） | 3分钟 | 写5章约需5-8分钟 |
| 大莉（深度模型） | 2分钟 | 响应较慢 |

## 监控命令

```bash
# 检查任务状态
hermes kanban show <task_id> 2>&1 | grep -E "status|completed|summary|Runs|running|timed_out" | tail -10

# 检查产出文件
ls -la /path/to/正文/第2XX章*.md 2>/dev/null

# 检查字数
for f in /path/to/正文/第2XX章*.md; do echo "$(basename $f): $(wc -m < "$f") 字符"; done
```

## 状态解读

| 状态 | 含义 | 下一步 |
|------|------|--------|
| running | 正在执行 | 等待，5分钟后再检查 |
| done | 已完成 | 读取summary，验证产出 |
| timed_out | 超时 | 检查日志，决定是否重试 |
| crashed | 崩溃 | 检查日志，修复后重试 |
| blocked | 已阻止 | 检查原因，unblock或创建新任务 |

## 超时处理

当任务timed_out时：

```bash
# 检查超时原因
hermes kanban show <task_id> 2>&1 | grep -E "timed_out|Iteration|error" | tail -5

# 检查产出（可能部分完成）
ls -la /path/to/正文/第2XX章*.md 2>/dev/null | wc -l

# 如果有部分产出，检查是否可用
for f in /path/to/正文/第2XX章*.md; do
  chars=$(wc -m < "$f")
  if [ $chars -ge 4500 ]; then
    echo "$(basename $f): $chars ✅ 可用"
  else
    echo "$(basename $f): $chars ❌ 需补充"
  fi
done
```

## LongCat特定问题

### RPM限速
```
HTTP 429: 服务端模型:LongCat-2.0-Preview 总RPM超过限制
```
**处理**：等待1-2分钟后重试，或切换到其他Provider

### Iteration budget exhausted
```
Iteration budget exhausted (90/90)
```
**处理**：
1. 检查已完成的产出（可能部分章节已写完）
2. 如果有部分产出，创建新任务补充剩余章节
3. 如果无产出，精简任务body后重试

## 批次间衔接

每批完成后，立即安排莉莉审核，不要直接写下一批：

```
闪莉完成 → 检查产出 → 安排莉莉审核 → 等审核结果 → 根据结果决定下一步
```

**冰哥铁律**：先审核通过再继续下一批。
