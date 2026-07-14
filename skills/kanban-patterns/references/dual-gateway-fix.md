# 双Gateway修复流程 (2026-06-15 验证)

## 问题背景
两个LaunchAgent plist同时运行，共享同一个Telegram Bot Token，导致：
- Telegram消息随机分发到两个gateway
- 模型随机切换（mimo-v2.5 vs LongCat）
- Cron jobs在更新中丢失（8→1个）
- Telegram polling conflict每~25秒一次

## 根因
- `ai.hermes.gateway.plist` (default) + `ai.hermes.gateway-shanli.plist` (shanli)
- 两个plist都有 `RunAtLoad: true` + `KeepAlive: true`
- 两个.env文件包含同一个 `TELEGRAM_BOT_TOKEN`

## 修复流程

### Phase 1: 停掉多余gateway（5分钟）

```bash
# Step 1: 备份
cp ~/.hermes/cron/jobs.json ~/.hermes/cron/jobs.json.bak.$(date +%Y%m%d%H%M%S)
cp ~/.hermes/kanban.db ~/.hermes/kanban.db.bak.$(date +%Y%m%d%H%M%S)

# Step 2: bootout shanli gateway（⚠️ 必须先bootout，不能先kill）
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist
sleep 3

# Step 3: 确认进程死亡
ps aux | grep "profile shanli" | grep -v grep
# 应该无输出

# Step 4: 禁用plist（防复活）
mv ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist \
   ~/Library/LaunchAgents/ai.hermes.gateway-shanli.plist.disabled

# Step 5: kickstart default gateway（清理Telegram会话状态）
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway
sleep 15

# Step 6: 重置active_profile
echo "default" > ~/.hermes/active_profile

# Step 7: 验证conflict消失
tail -10 ~/.hermes/logs/gateway.error.log | grep -i "conflict"
# 重启后应该无conflict
```

### Phase 2: 恢复Cron Jobs（10分钟）

```bash
# 1. 检查state snapshot中的jobs
cat ~/.hermes/state-snapshots/<timestamp>/cron/jobs.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    print(f'{j[\"id\"]}: {j[\"name\"]} (script={j.get(\"script\",\"none\")})')
"

# 2. 验证脚本路径存在
for script in nv_ping.py nv_daily_eval.py health_daily.py; do
  test -f ~/.hermes/scripts/$script && echo "✓ $script" || echo "✗ $script MISSING"
done

# 3. 逐个恢复（用cronjob工具）
# Script jobs:
cronjob action=create name="..." script="nv_ping.py" no_agent=true schedule="*/30 * * * *" deliver=local

# Agent jobs:
cronjob action=create name="..." prompt="..." schedule="0 8 * * *" deliver="telegram:611807381" \
  model='{"model":"LongCat-2.0-Preview","provider":"longcat"}' skills='["daily-morning-report"]'
```

## 关键陷阱

### KeepAlive陷阱
两个plist都有 `<key>KeepAlive</key><true/>`。如果先kill进程再disable plist，launchd会**立即自动重启**进程。必须先 `launchctl bootout` 卸载服务，再disable plist。

### Kanban Worker Spawn验证
停掉shanli后，default gateway的 `kanban.profiles: ["lili", "shanli"]` 配置仍然有效。Worker spawn时HERMES_HOME自动设为profile目录（`~/.hermes/profiles/shanli/`），读取该profile的.env和config.yaml。不需要shanli gateway进程。

### Cron Job恢复注意事项
- Cron scheduler不处理profile字段，所有jobs用gateway的HERMES_HOME运行
- 恢复LongCat模型的job时，必须显式指定model/provider字段
- 脚本不存在的job不要恢复（会执行失败）
- Symlink脚本会被cronjob工具拒绝，必须复制实际文件

## 验证清单

```bash
# 1. 只有1个gateway在运行
ps aux | grep "hermes_cli.main" | grep -v grep
# 应该只显示1个进程

# 2. 无Telegram conflict
tail -5 ~/.hermes/logs/gateway.error.log | grep -i "conflict"
# 应该无输出

# 3. active_profile正确
cat ~/.hermes/active_profile
# 应该显示 "default"

# 4. Plist状态
ls ~/Library/LaunchAgents/ai.hermes.gateway*.plist
# 应该只有 ai.hermes.gateway.plist

# 5. Cron jobs数量
hermes cron list 2>/dev/null | grep -c "enabled"
# 应该显示恢复的job数量

# 6. Kanban DB完整
sqlite3 ~/.hermes/kanban.db "PRAGMA integrity_check;"
# 应该显示 "ok"
```
