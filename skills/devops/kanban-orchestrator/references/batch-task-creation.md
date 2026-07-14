# Batch Kanban Task Creation Patterns

## The Problem
Creating 10+ kanban tasks individually is tedious. Python subprocess wrappers fail due to shell escaping issues with multi-line bodies.

## The Solution: Direct Shell Commands

```bash
# ✅ Works reliably
hermes kanban create "Task Title" \
  --assignee default \
  --max-runtime 2h \
  --body "Multi-line body content here"
```

## Batch Creation Script Pattern

```bash
#!/bin/bash
# Create tasks from a list

create_task() {
    local title="$1"
    local body="$2"
    local parent="$3"
    
    if [ -n "$parent" ]; then
        hermes kanban create "$title" --assignee default --max-runtime 2h --parent "$parent" --body "$body"
    else
        hermes kanban create "$title" --assignee default --max-runtime 2h --body "$body"
    fi
}

# Usage
create_task "Research: Topic A" "Task details..."
create_task "Research: Topic B" "Task details..." "parent_task_id"
```

## Extraction Pattern (from plan file)

```bash
# Extract task titles from a markdown plan
grep "^#### 卡片 T" plan.md | while read line; do
    id=$(echo "$line" | sed 's/#### 卡片 \(T[0-9]*\) — .*/\1/')
    title=$(echo "$line" | sed 's/#### 卡片 T[0-9]* — //')
    echo "$id | $title"
done
```

## Performance Notes
- Each task creation: ~2-5 seconds
- 40 tasks: ~2-3 minutes total
- Tasks auto-start if dispatcher is running (ready → running immediately)

## Common Pitfalls
1. **subprocess.run with input= fails** — shell escaping issues with multi-line bodies
2. **--body-file flag doesn't exist** — must use `--body "$BODY"` with shell variable
3. **Special characters in titles** — quote titles properly, avoid backticks
4. **Dependency chains** — create parent tasks FIRST, then children with `--parent`
