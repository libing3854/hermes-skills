# 自动化写作流水线 - 状态文件模板

## 用途
CronJob 每次启动是全新 session，无法记忆上次状态。此文件作为持久化状态存储，让 CronJob 知道当前执行到哪一批、什么阶段。

## 文件路径
`{项目目录}/追踪/自动化状态.md`

## 模板

```yaml
# 第X卷写作自动化状态

## 当前状态
- **阶段：** writing          # idle | writing | waiting_review | reviewing | passed | failed | revision | done
- **批次号：** 1
- **章节范围：** 067-071
- **写作任务ID：** t_xxx
- **审核任务ID：** null
- **重试次数：** 0
- **上次操作时间：** 2026-05-31T15:00:00

## 状态机说明
- idle: 空闲，等待启动
- writing: 闪莉写作中
- waiting_review: 写作完成，等待创建审核任务
- reviewing: 大莉M审核中
- passed: 审核通过，准备创建下一批
- failed: 审核不通过，需要修改
- revision: 修改中
- done: 全部章节完成

## 历史记录
- [2026-05-31 15:00] 批次1 开始写作 (t_xxx)
```

## CronJob 读写逻辑

### 读取
```
读取 追踪/自动化状态.md → 获取当前 phase 和 batch_num
```

### 写入（按阶段）
1. **writing → waiting_review**: 写作任务 done 时更新
2. **waiting_review → reviewing**: 创建审核任务时更新
3. **reviewing → passed**: 审核通过时更新
4. **reviewing → failed**: 审核不通过时更新
5. **failed → revision**: 创建修改任务时更新
6. **revision → waiting_review**: 修改完成时更新
7. **passed → writing**: 创建下一批任务时更新（batch_num+1, chapter_range+5）
8. **任意 → done**: 所有章节完成时更新

## 批次上下文自动计算

CronJob 需要自动计算每批的读取范围：
```
当前批次 N，写作范围第 X-X+4 章
读取范围：第 X-30 到第 X-1 章（共30章）
```

示例：
- 批次1: 写067-071, 读037-066
- 批次2: 写072-076, 读042-071
- 批次3: 写077-081, 读047-076

## 审核循环上限
- 最大重试次数：3
- 超过3次：暂停自动化，通知冰哥介入
