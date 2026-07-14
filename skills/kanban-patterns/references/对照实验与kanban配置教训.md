# 对照实验与Kanban配置教训（2026-06-26）

## 对照实验Workspace隔离

**问题**：多个agent修改同一个目录的文件会互相踩踏。

**解决方案**：为每个agent创建独立副本目录：
```bash
mkdir -p _对照实验/shanli _对照实验/nvlinshi _对照实验/agnes
cp 原目录/第*.md _对照实验/shanli/
cp 原目录/第*.md _对照实验/nvlinshi/
cp 原目录/第*.md _对照实验/agnes/
# 然后分别指定 --workspace "dir:/path/_对照实验/shanli"
```

## kanban profiles必须包含所有worker profile

**问题**：默认config的kanban profiles只包含`["lili", "shanli"]`，导致nvlinshi和shanli-agnes20flash的任务无法dispatch（Spawned: 0）。

**修复**：在默认config.yaml中添加所有worker profile：
```bash
sed -i '' 's/profiles: '\''\["lili", "shanli"\]'\''/profiles: '\''\["lili", "shanli", "nvlinshi", "shanli-agnes20flash"]'\''/' ~/.hermes/config.yaml
```

## nvlinshi kanban协议问题

**现象**：nvlinshi无论使用Qwen3.5 122B还是DeepSeek V4 Flash (NVIDIA)，执行完任务后不调用kanban_complete/kanban_block，导致protocol_violation。文件修改可能已完成但kanban任务标记为失败。

**处理方式**：
1. 手动检查文件是否已修改（grep验证）
2. 如果文件已修改，手动 `hermes kanban complete <task_id> --summary "..."`
3. 如果文件未修改，需要换其他agent重做

## 修改任务Agent选择优先级

| Agent | 修改完成率 | kanban协议 | 推荐度 |
|-------|-----------|-----------|--------|
| shanli-agnes20flash | 5/5 | ✅ 正常 | ⭐⭐⭐ 首选 |
| shanli | 4/5 | ✅ 正常 | ⭐⭐ 次选 |
| nvlinshi | 1/5 | ❌ protocol_violation | ⚠️ 不推荐 |

**对照实验任务**：角色名统一+世界观红线+别字修复（8处修改）
- agnes：5/5全部通过
- shanli：4/5（修了名字但漏了西区）
- nvlinshi：1/5（只修了处罝，其余崩溃3次未修改）
