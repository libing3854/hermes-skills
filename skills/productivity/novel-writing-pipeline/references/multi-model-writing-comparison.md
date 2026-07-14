# 多模型写作对比实验模式 (2026-07-03)

## 背景

冰哥要求对比不同AI模型的写作质量，选择主写模型。本次实验对比了：
- MiMo v2.5（小米API，mimo-v25 profile）
- 闪莉（LongCat 2.0，shanli profile）
- agnes-2.0-flash（shanli-agnes20flash profile）

## 对比工作流

### 1. 创建独立输出目录
```bash
mkdir -p 08_临时正文/mimo写 08_临时正文/闪莉写 08_临时正文/agnes写
```

### 2. 并行安排kanban任务
每个模型一个独立任务，相同大纲，独立目录：
```bash
hermes kanban create --assignee mimo-v25 --workspace "dir:08_临时正文/mimo写" ...
hermes kanban create --assignee shanli --workspace "dir:08_临时正文/闪莉写" ...
```

### 3. 订阅QQ通知
```bash
sqlite3 ~/.hermes/kanban.db "INSERT OR REPLACE INTO kanban_notify_subs (task_id, platform, chat_id, ...) VALUES ('task_id', 'qqbot', 'chat_id', ...);"
```

### 4. 等待完成 + 手动检查
kanban任务可能不自动完成（protocol violation），需要手动检查文件后complete：
```bash
# 检查文件是否生成
ls 08_临时正文/mimo写/第0*.md | wc -l

# 手动完成
hermes kanban complete <task_id>
```

### 5. 运行质量检查脚本
```bash
python3 09_临时文件/章节质量检查脚本.py
```

### 6. 冰哥人工评估
AI检查脚本只做量化（字数/禁用词/高频词），最终质量判断需要冰哥读内容评估。

## 质量检查脚本要点

```python
# 统计纯汉字数（不含标点/空格/英文）
chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))

# 禁用词检查（0次）
banned = ["仿佛", "深吸一口气", "不由得"]

# 高频词检查
limits = {"像": 10, "如同": 3, "某种": 3, "一种": 3, "微微": 2, "缓缓": 2}
```

## 评估维度（冰哥确认）

| 维度 | 说明 |
|------|------|
| 新版系统流程执行 | 是否吃进了最新大纲的系统设定 |
| 主角活人感 | 社畜资料员底色是否自然 |
| 番茄开篇爽点 | 是否有追读动力 |
| 执行大纲遵守 | 是否偏离大纲 |
| 设定稳定性 | 角色/世界观是否前后一致 |
| 陆青辞角色控制 | 是否有人味，不是说明书 |
| 第一案闭环 | 案件是否收束 |
| 后续可续写性 | 能否在此基础上继续写 |
| 改稿成本 | 修到可用需要多少工作量 |

## 本次实验结论

| 模型 | 综合评分 | 优势 | 劣势 |
|------|---------|------|------|
| MiMo v2.5 | 7.7 | 吃进系统流程好，资料员底色稳 | 文风偏平，动作高潮不够炸 |
| 闪莉 | 4.3 | 悬疑感强，物件感好 | 严重提前揭底，偏离大纲 |
| agnes-2.0-flash | 待评 | 文件修改能力最强 | 字数控制偏弱 |

**结论：** mimo做主写，闪莉借画面和气氛，不当主线继续。

## 注意事项

- 每批不要超过3-5章，10章/批容易iteration budget耗尽
- 新大纲更新后要在任务body中强调人物修改
- Gateway必须运行才能dispatch
- 新profile要加到kanban.profiles配置
