# Research Index → Kanban Allocation Workflow

> For large-scale research projects (10+ topics), create a structured index first, then allocate as kanban tasks. This ensures coverage, avoids duplication, and enables parallel execution.

## Workflow Steps

### Step 1: Create Research Index Framework

Before creating any kanban tasks, generate a comprehensive index of all topics to research.

**Index structure:**
```
# Research Index Framework

## Per-topic entry:
### Module X.Y — Topic Name
- **Priority:** 核心/重要/补充
- **Estimated time:** X-Y hours
- **Research content:**
  - Sub-topic 1
  - Sub-topic 2
- **Search keywords:**
  - 中: [Chinese keywords]
  - EN: [English keywords]
- **Output file:**详解/XX-YY-topic.md
```

**Tips:**
- Use a delegator (大莉M/D) to generate the index — they can hold the full 100+ module structure in context
- Include priority levels and time estimates for each module
- Mark dependencies between modules
- Generate a summary statistics table at the end

### Step 2: Review and Fix Index

Have a second delegator (大莉D) review the index for:
- Missing topics
- Priority inconsistencies (module priority vs. roadmap placement)
- File naming conflicts
- Search keyword quality

Fix all issues before proceeding to allocation.

### Step 3: Allocate to Kanban Tasks

Group modules into kanban tasks based on:
1. **Time constraint:** Each task ≤ 2 hours (prevent token exhaustion)
2. **Dependency:** Tasks with dependencies use `parents=[...]`
3. **Parallelism:** Independent modules can run in parallel tracks

**Allocation template:**
```
Task T0101: Research Module 1.1 + 1.2 (2h)
  ├── Read: existing index files
  ├── Search: web_search with provided keywords
  ├── Write: 详解/01-01-topic.md (checkpoint)
  └── Dependencies: none

Task T0102: Research Module 1.3 (2h)  
  ├── Read: T0101 output
  ├── Search: web_search with provided keywords
  ├── Write: 详解/01-02-topic.md (checkpoint)
  └── Dependencies: T0101
```

### Step 4: Review Allocation

Have a second delegator review the allocation for:
- Task size (each ≤ 2h)
- Dependency completeness (no missing parents)
- Parallel track feasibility
- Module coverage (no modules left out)

## Anti-Crash Body Template for Research Tasks

Each kanban task body should include:

```markdown
# Research: [Topic]

## 输出目录
`/path/to/output/`
先创建目录：`mkdir -p "/path/to/output/"`

## 阶段1：读取前置资料（X分钟）
读取以下文件：[list files]
**完成后保存**：写入 `output/checkpoint-01.md`

## 阶段2：深度研究（Y分钟）
搜索关键词：[list keywords with web_search]
**完成后立即保存**：写入 `output/checkpoint-02.md`

## 阶段3：整理定稿（Z分钟）
**完成后立即保存**：写入 `output/final.md`

## ⚠️ 防崩溃规则
1. 每完成一个阶段必须写入文件
2. 每个文件写入后验证：ls -la 确认文件存在且≥500字节
3. 某阶段失败→跳过继续下一阶段
4. 超时→保存当前进度进入下一阶段
```

## Example: Large-Scale Research Project

**Project:** Warhammer × Daoism worldbuilding research (103 modules)

1. **Index generation:** 1974-line framework with 103 modules, 9 sections
2. **Priority classification:** 31 core / 38 important / 25 supplementary / 9 bonus
3. **Allocation:** ~180 kanban tasks across 6 phases, 4 parallel tracks
4. **Review:** Dual-review (大莉M deep + 大莉D final) caught 22 priority conflicts + 3 file naming conflicts
5. **Execution:** Phase 0-2 (~30 tasks) designed with full body prompts; Phase 3-6 pending body generation
