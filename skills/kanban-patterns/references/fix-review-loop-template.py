#!/usr/bin/env python3
"""写→审→修循环监控脚本（模板）
使用方法：
1. 复制本文件，修改以下常量：
   - TRACK_FILE: 跟踪文件路径
   - CHAPTER_DIR: 章节目录
   - REPORT_DIR: 报告目录
   - check_chapters()中的章节范围
   - create_review_task()/create_fix_task()中的任务标题和描述
2. 创建对应的 .fix_review_loop.json 跟踪文件
3. 用 cronjob(no_agent=true, schedule="every 5m") 定时运行
"""
import json, subprocess, re, os, glob, sys

# ===== 修改这里 =====
TRACK_FILE = "/path/to/.fix_review_loop.json"
CHAPTER_DIR = "/path/to/chapters/"
REPORT_DIR = "/path/to/reports/"
CHAPTER_START = 305  # 修改为实际章节范围
CHAPTER_END = 312
BATCH_NAME = "305-312"  # 用于任务标题
VOLUME_NAME = "第六卷第一批"  # 用于任务标题
# ===== 修改结束 =====

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    return r.stdout.strip()

def get_task_status(task_id):
    out = run(f'hermes kanban show {task_id} 2>/dev/null | head -5')
    for line in out.split('\n'):
        if 'status:' in line:
            return line.split('status:')[-1].strip()
    return 'unknown'

def count_hanzi(filepath):
    try:
        with open(filepath) as f:
            return len(re.findall(r'[\u4e00-\u9fff]', f.read()))
    except:
        return 0

def count_issues(filepath):
    try:
        with open(filepath) as f:
            content = f.read()
    except:
        return {}
    issues = {}
    for word in ['深吸一口气', '仿佛', '不由得']:
        c = content.count(word)
        if c > 0:
            issues[f'禁用词:{word}'] = c
    for word in ['某种', '一种', '微微', '如同']:
        c = content.count(word)
        if c > 3:
            issues[f'高频词:{word}'] = c
    return issues

def check_chapters(start, end):
    results = {}
    all_issues = {}
    for i in range(start, end + 1):
        files = glob.glob(os.path.join(CHAPTER_DIR, f"第{i}章_*.md"))
        if not files:
            results[i] = {'hanzi': 0, 'issues': {}, 'status': 'missing'}
            continue
        f = files[0]
        hanzi = count_hanzi(f)
        issues = count_issues(f)
        results[i] = {
            'hanzi': hanzi,
            'issues': issues,
            'status': 'ok' if hanzi >= 4500 and len(issues) == 0 else 'fail'
        }
        all_issues.update(issues)
    return results, all_issues

def load_tracking():
    try:
        with open(TRACK_FILE) as f:
            return json.load(f)
    except:
        return {"round": 1, "max_rounds": 3, "issue_history": {}, "phase": "write", "status": "running"}

def save_tracking(data):
    with open(TRACK_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def subscribe_task(task_id):
    run(f"""sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs (task_id, platform, chat_id, thread_id, user_id, notifier_profile, created_at, last_event_id) VALUES ('{task_id}', 'qqbot', '54D8D2AB6A48EE35127DD0F86081146A', '', 'binge', 'default', strftime('%s','now'), (SELECT COALESCE(MAX(id),0) FROM task_events));" """)
    run('hermes kanban dispatch --max 1 2>/dev/null')

def create_review_task(round_num):
    body = f"""## 任务：审核{VOLUME_NAME}（{BATCH_NAME}章）（第{round_num}轮）

### 审核范围
{BATCH_NAME}章，位于：`{CHAPTER_DIR}/`

### 审核维度（8项）
1. 剧情连贯性 2. 对话质量 3. 上下文逻辑
4. AI味检测：禁用词0次，高频词≤3次
5. 字数：每章4500-6000纯汉字
6. 设定一致性 7. 禁止项 8. 章节标题

### 输出
- 报告保存到：{REPORT_DIR}/{VOLUME_NAME}审核R{round_num}.md
- 每章：字数+禁用词+高频词+评分
- 综合评分和结论"""
    out = run(f'''hermes kanban create "莉莉审核{VOLUME_NAME}（{BATCH_NAME}章）R{round_num}" --assignee lili --body "{body}" --json 2>/dev/null''')
    try:
        return json.loads(out).get('id')
    except:
        return None

def create_fix_task(round_num, remaining_issues):
    issue_list = "\n".join([f"- {k}: {v}次" for k, v in remaining_issues.items()])
    body = f"""## 任务：修复{VOLUME_NAME}（{BATCH_NAME}章）残留问题（第{round_num}轮）

### 残留问题
{issue_list}

### 修复要求
1. 字数不足4500字→扩充至4500-5500字
2. 禁用词→全部清零
3. 高频词→每章≤3次
4. ⚠️ 严禁修改剧情走向
5. ⚠️ 严禁两稿拼接

### 输出
- 覆盖原文件
- 修改报告（字数+高频词变化）"""
    out = run(f'''hermes kanban create "修复{VOLUME_NAME}（{BATCH_NAME}章）R{round_num}" --assignee shanli --workspace "dir:{CHAPTER_DIR}" --body "{body}" --json 2>/dev/null''')
    try:
        return json.loads(out).get('id')
    except:
        return None

# ===== 主逻辑 =====
track = load_tracking()
if track['status'] != 'running':
    print(f"[SILENT] Loop status: {track['status']}")
    sys.exit(0)

phase = track['phase']
round_num = track['round']

if phase == 'write':
    write_task = track.get('write_task')
    if not write_task:
        print("[SILENT] No write task"); sys.exit(0)
    status = get_task_status(write_task)
    if status not in ('done', 'blocked', 'crashed', 'gave_up'):
        print(f"[SILENT] Write task {write_task} still {status}"); sys.exit(0)
    if status != 'done':
        track['status'] = f'write_failed_{status}'; save_tracking(track)
        print(f"⚠️ 写作任务异常：{status}"); sys.exit(0)
    review_id = create_review_task(round_num)
    if not review_id:
        track['status'] = 'review_create_failed'; save_tracking(track)
        print("❌ 创建审核任务失败"); sys.exit(0)
    subscribe_task(review_id)
    track['current_review_task'] = review_id
    track['phase'] = 'review'; save_tracking(track)
    print(f"📋 写作完成，已创建审核任务 {review_id}")

elif phase == 'review':
    review_task = track.get('current_review_task')
    if not review_task:
        print("[SILENT] No review task"); sys.exit(0)
    status = get_task_status(review_task)
    if status not in ('done', 'blocked', 'crashed', 'gave_up'):
        print(f"[SILENT] Review task still {status}"); sys.exit(0)
    if status != 'done':
        track['status'] = f'review_failed_{status}'; save_tracking(track)
        print(f"⚠️ 审核任务异常：{status}"); sys.exit(0)
    results, remaining = check_chapters(CHAPTER_START, CHAPTER_END)
    fail_count = sum(1 for r in results.values() if r['status'] == 'fail')
    if fail_count == 0:
        track['status'] = 'all_passed'; save_tracking(track)
        print("✅ 全部达标！"); sys.exit(0)
    for k, v in remaining.items():
        track['issue_history'][k] = track['issue_history'].get(k, 0) + 1
    stuck = {k: v for k, v in track['issue_history'].items() if v >= 3}
    if stuck:
        track['status'] = 'stuck'; save_tracking(track)
        stuck_list = "\n".join([f"  - {k}（连续{v}轮）" for k, v in stuck.items()])
        print(f"🛑 同一问题连续3轮未解决：\n{stuck_list}"); sys.exit(0)
    if round_num >= track['max_rounds']:
        track['status'] = 'max_rounds_reached'; save_tracking(track)
        print(f"🛑 已达最大轮次（{track['max_rounds']}轮）"); sys.exit(0)
    next_round = round_num + 1
    fix_id = create_fix_task(next_round, remaining)
    if not fix_id:
        track['status'] = 'fix_create_failed'; save_tracking(track)
        print("❌ 创建修复任务失败"); sys.exit(0)
    subscribe_task(fix_id)
    track['current_fix_task'] = fix_id; track['current_review_task'] = None
    track['phase'] = 'fix'; track['round'] = next_round; save_tracking(track)
    print(f"🔄 审核发现残留问题，已创建第{next_round}轮修复任务")

elif phase == 'fix':
    fix_task = track.get('current_fix_task')
    if not fix_task:
        print("[SILENT] No fix task"); sys.exit(0)
    status = get_task_status(fix_task)
    if status not in ('done', 'blocked', 'crashed', 'gave_up'):
        print(f"[SILENT] Fix task still {status}"); sys.exit(0)
    if status != 'done':
        track['status'] = f'fix_failed_{status}'; save_tracking(track)
        print(f"⚠️ 修复任务异常：{status}"); sys.exit(0)
    results, remaining = check_chapters(CHAPTER_START, CHAPTER_END)
    fail_count = sum(1 for r in results.values() if r['status'] == 'fail')
    if fail_count == 0:
        track['status'] = 'all_passed'; save_tracking(track)
        print("✅ 修复后全部达标！"); sys.exit(0)
    round_num = track['round']
    review_id = create_review_task(round_num)
    if not review_id:
        track['status'] = 'review_create_failed'; save_tracking(track)
        print("❌ 创建审核任务失败"); sys.exit(0)
    subscribe_task(review_id)
    track['current_review_task'] = review_id
    track['phase'] = 'review'; save_tracking(track)
    print(f"📋 修复完成，已创建审核任务")
