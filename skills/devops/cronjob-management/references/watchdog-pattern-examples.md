# Watchdog 模式实例

## 看板任务完成提醒（kanban_done_notifier.py）

完整工作实例，部署于 2026-06-12。每 15 分钟检查看板任务状态变化，有新完成任务时推送通知。

### 脚本

```python
#!/usr/bin/env python3
"""
看板任务完成提醒器
定期检查 kanban 任务状态，当任务变为 done 时输出通知。
配合 hermes cron (no_agent=True) 使用：有输出就推送，无输出就静默。
"""
import json, os, subprocess, sys, time
from datetime import datetime

STATE_FILE = os.path.expanduser("~/.hermes/data/kanban_done_state.json")

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_tasks():
    try:
        result = subprocess.run(
            ["hermes", "kanban", "list", "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return None

def main():
    tasks = get_tasks()
    if tasks is None:
        return  # 命令失败，静默退出

    current = {}
    for t in tasks:
        current[t["id"]] = t["status"]

    prev = load_state()

    newly_done = []
    for tid, status in current.items():
        if status == "done" and prev.get(tid) != "done":
            task_info = next((t for t in tasks if t["id"] == tid), None)
            if task_info:
                newly_done.append(task_info)

    save_state(current)  # 无论有无变化都保存

    if not newly_done:
        return  # 静默退出

    lines = [f"✅ 看板任务完成提醒 — {len(newly_done)} 个任务刚刚完成：", ""]
    for t in newly_done:
        title = t.get("title", "无标题")
        assignee = t.get("assignee", "未分配")
        task_id = t.get("id", "?")
        completed_at = t.get("completed_at")
        if completed_at:
            ts = datetime.fromtimestamp(completed_at).strftime("%Y-%m-%d %H:%M")
        else:
            ts = "刚刚"
        lines.append(f"  📌 [{task_id}] {title}")
        lines.append(f"     负责人: {assignee} | 完成时间: {ts}")
        lines.append("")

    print("\n".join(lines))

if __name__ == "__main__":
    main()
```

### 部署步骤

```bash
# 1. 写脚本
# 文件保存到 ~/.hermes/scripts/kanban_done_notifier.py

# 2. 手动运行初始化状态文件（输出会很大，但只需要执行一次）
python3 ~/.hermes/scripts/kanban_done_notifier.py

# 3. 验证状态文件已创建
python3 -c "import json; d=json.load(open('$HOME/.hermes/data/kanban_done_state.json')); print(f'总任务: {len(d)}')"

# 4. 再次运行验证静默（无输出 = 正常）
python3 ~/.hermes/scripts/kanban_done_notifier.py && echo "EXIT: $?"

# 5. 创建 cron job
cronjob(action='create',
    name='看板任务完成提醒',
    schedule='*/15 * * * *',
    no_agent=True,
    script='kanban_done_notifier.py',
    deliver='origin',
    repeat=0)

# 6. 如果 repeat 不是 forever，修正
cronjob(action='update', job_id='xxx', repeat=0)
```

### hermes kanban notify-subscribe（替代方案）

hermes 内置的按任务订阅通知，适合特定任务追踪：

```bash
hermes kanban notify-subscribe <task_id> \
  --platform telegram \
  --chat-id 611807381
```

限制：需要指定 platform + chat-id，不能自动监控所有任务状态变化。
