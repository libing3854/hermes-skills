# Kanban-Cron 任务追踪约定

## 用途

用 Hermes Kanban 追踪定时 Cron 任务的执行状态，提供统一的「任务看板」视角。

## 已追踪的任务

| Kanban 任务 | Cron Job ID | 时间 | 渠道 |
|:------------|:------------|:----:|:----:|
| 📰 生成AI周报 | `7b87806cd77e` | 每周日 20:00 | Discord |
| 💹 金融看板 | `0938e881e6aa` + `ed1a1d1add18` | 每天 10:00/20:00 | Discord |
| 🏁 闪莉Ping监控 | `649c712a8c22` | 每30分钟 | 本地 |
| 📖 番茄小说扫榜与推荐 | `t_368686e9`（kanban） | — | 本地 |

## 任务命名规范

```
{Emoji} {任务名称}
```

用 Emoji 快速区分任务类型：
- 📰 AI 内容生成
- 💹 金融/数据
- 🏁 系统监控/Ping
- 📖 写作/扫榜

## 看板状态流转

```
triage → todo → ready → running → done
                    ↓
                blocked
```

## 执行者规则

**所有看板任务默认走闪莉**，不需要指定 `--assignee`。闪莉由 Ping 系统从 mimi/light/deep/vision 分类中选最快的模型执行。

特殊任务才指定：
- 纯本地操作 → `--assignee xiaoli`（小莉）
- 详细规则见 `~/.hermes/看板调度规范.md`

## 常用命令

```bash
# 查看所有任务
hermes kanban list

# 查看统计
hermes kanban stats

# 查看任务详情
hermes kanban show t_<id>

# 完成任务（cron跑完后标记）
hermes kanban complete t_<id>

# 添加追踪评论
hermes kanban comment t_<id> --body "2026-05-23 20:00 执行成功 ✅"

# 创建新的追踪任务（不用加 --assignee，默认走闪莉）
hermes kanban create "📰 任务名" --body "说明\\n\\n关联Cron: <job_id>"
```

## 初始化看板

```bash
hermes kanban init
# 看到输出：Kanban DB initialized at ~/.hermes/kanban.db
# 然后可创建任务
```

注意：Kanban 和 Cron 是**两个独立系统**。Cron 自动按时跑，Kanban 记录和追踪。两者通过任务标题中的 Cron Job ID 关联。

## 调度规范

详细的调度规则见 **`~/.hermes/看板调度规范.md`**，已上传至 GitHub `hermes-skills/docs/看板调度规范.md`。

核心原则：
- **默认** → ⚡ 闪莉（Ping 分类选最快的模型，通过 `--skill` 路由）
- 纯本地 → 🏠 小莉（gemma-4-e4b，`--assignee xiaoli`）
