# Kanban Task Monitoring Frequency

## User-Defined Standard (2026-06-08)

When monitoring kanban task progress for the user, use these intervals:

| Task Type | Check Interval | Examples |
|-----------|---------------|----------|
| Simple (single chapter edit, quick fix) | 1-5 min | Typo fixes, one-line changes |
| Medium (3-5 chapter writing) | 5-15 min | Standard batch writing |
| Complex (7-8 chapter writing) | 15-30 min | Large batch, multi-dimension edits |
| Review tasks (莉莉 audit) | 5-10 min | Quality review passes |

## Implementation

Use background process with `notify_on_complete=true` for long-running tasks:

```bash
# For complex tasks (15-30 min checks)
terminal(background=true, notify_on_complete=true, command="while true; do
  status=$(hermes kanban show <task_id> 2>&1 | grep 'status:' | awk '{print \$2}')
  if [ \"\$status\" = \"done\" ] || [ \"\$status\" = \"blocked\" ]; then
    echo \"Task complete: \$status\"
    hermes kanban show <task_id> 2>&1 | grep -E 'completed:|Latest summary' | head -5
    break
  fi
  sleep 900  # 15 minutes for complex tasks
done")
```

## Progress Reporting

When checking task status, report partial progress — don't wait for all tasks:
- "5/8 chapters done, 3 still running"
- "Writing complete, review started"
- "2/3 modification tasks done"

After all tasks complete, immediately proceed to next workflow step (e.g., trigger review) unless the user has asked to be consulted first.
