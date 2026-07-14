# 并行对照实验模式（2026-06-26 验证）

## 场景
让多个agent做同样的修改任务，对比修改质量。

## Workspace隔离（关键）

**问题：** 多个任务共用同一个workspace目录，后执行的agent会读到先执行的agent的修改结果。

**解决方案：** 为每个agent创建独立的文件副本目录：

```bash
mkdir -p _对照实验/agentA _对照实验/agentB _对照实验/agentC
cp 原始目录/第*.md _对照实验/agentA/
cp 原始目录/第*.md _对照实验/agentB/
cp 原始目录/第*.md _对照实验/agentC/

hermes kanban create "实验A" --assignee agentA --workspace "dir:$(pwd)/_对照实验/agentA"
hermes kanban create "实验B" --assignee agentB --workspace "dir:$(pwd)/_对照实验/agentB"
hermes kanban create "实验C" --assignee agentC --workspace "dir:$(pwd)/_对照实验/agentC"
```

## kanban profiles必须包含所有assignee

**问题：** `hermes kanban dispatch` 只认默认config中 `kanban.profiles` 列表里的profile。

**症状：** 任务创建成功但 Spawned=0，卡在 ready 状态。

**修复：** 在默认config.yaml中添加所有需要的kanban profiles：
```yaml
kanban:
  profiles: '["lili", "shanli", "nvlinshi", "shanli-agnes20flash"]'
```

## 验证脚本

```bash
for AGENT in agentA agentB agentC; do
  echo "--- $AGENT ---"
  cd _对照实验/$AGENT/
  # 检查各项修改指标
  grep -c "应被替换的词" 目标文件.md
done
```
