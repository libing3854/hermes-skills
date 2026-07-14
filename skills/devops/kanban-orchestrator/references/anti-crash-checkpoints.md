# Anti-Crash Checkpoint Strategy for Kanban Tasks

> When a kanban task involves multi-step research or content generation, splitting "read" and "write" into separate tasks causes the write task to fail — it cannot access the read task's output. Instead, use a single task with checkpoint saves.

## The Read+Write Pitfall

**Problem:** Splitting research into "Task A: read and create index" + "Task B: read index and write summary" seems logical, but kanban tasks are independent — Task B's worker cannot reliably access Task A's output files.

**User correction (2026-05-28):** "就是说现在读和写是分开的导致写的任务没有读取所以写不出来对吧" — The read and write tasks are separate, so the write task has nothing to read.

**Root cause:** Kanban tasks run in isolated contexts. Even if files exist on disk, the worker may not know to look for them, or may start before the parent task's files are written.

**Fix:** Combine read+write into a single task with checkpoint saves at each stage.

## Checkpoint Save Pattern

For any kanban task with 3+ stages of work:

```
Stage 1: Read/index → Save checkpoint file
Stage 2: Research/generate → Save checkpoint file  
Stage 3: Final output → Save final file
```

### Task Body Template

```markdown
## 防崩溃规则
1. **每完成一个阶段必须写入文件**，不要等最后一起写
2. **每个文件写入后验证**：用 `ls -la` 确认文件存在且大小合理（≥500字节）
3. **如果某个阶段失败**：跳过继续下一阶段，已完成的文件不会丢失
4. **搜索失败处理**：如果某个关键词搜不到，记录"需进一步研究"，继续下一个
5. **超时处理**：每个阶段控制在指定时间内，超时就保存当前进度进入下一阶段
```

### Checkpoint File Naming

```
output_dir/
├── 00-索引摘要.md          # Stage 1 checkpoint
├── 01-主题A.md             # Stage 2 checkpoint
├── 02-主题B.md             # Stage 2 checkpoint
├── ...
└── 99-总索引.md            # Final output
```

Use numbered prefixes (01-, 02-, etc.) for ordering. Use `99-` for final aggregation files.

## Dependency Between Tasks

When Task B genuinely depends on Task A's output:

1. **Preferred:** Combine into one task with checkpoints
2. **If must split:** Use `parents=[task_A_id]` in `kanban_create` so Task B only starts after Task A completes
3. **Never:** Create both as independent ready tasks and hope Task B finds Task A's files

## Verification After Each Checkpoint

```bash
# Verify file exists and has content
ls -lh "/path/to/output/01-topic.md"
wc -l "/path/to/output/01-topic.md"
```

Minimum threshold: each checkpoint file should be ≥500 bytes (at least one paragraph of substantive content).
