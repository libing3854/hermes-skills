# 双技能协作模式：子代理数据供应架构

## 概述

本模式描述了一个技能（**主技能**）通过 `delegate_task` 启动子代理，子代理加载另一个技能（**数据供应技能**）来获取结构化数据，然后基于数据做出决策的工作流。

## 典型案例：灵匠 + 寻技

```
灵匠（主技能）
  └── Step 0: delegate_task → 子代理
                                 └── skill_view('findskill') 加载寻技
                                 └── 寻技搜索四源（本地/Hub/Skills.sh/GitHub）
                                 └── 返回结构化 JSON
  └── 基于 JSON 的 safety.verdict 决策:
        ├── safe_to_use   → 快捷复用（直接安装）
        ├── review_needed → 完整复用（审查+适配）
        └── unsafe        → 跳过
```

## 适用场景

| 场景 | 说明 |
|------|------|
| **数据提供型** | 一个技能专门负责搜集/评估数据，另一个利用这些数据做决策 |
| **沙箱执行型** | 数据供应技能在子代理隔离环境中执行，不污染主会话 |
| **多源聚合型** | 需要同时搜索多个来源并聚合结果（如寻技的四源搜索） |
| **安全审查型** | 数据供应技能做只读的安全评估，主技能根据评估结果决定是否执行 |

## 架构规则

### 数据供应技能（如寻技）

- **只读**：不安、不执、不写（不安装、不执行危险命令、不写文件）
- **输出 JSON**：返回结构化数据，不是显示文本
- **佐证 clear**：description 中说明自己是"XX 的前置数据供应技能"
- **独立可测试**：可以被子代理直接调用并验证输出

### 主技能（如灵匠）

- **负责任**：基于数据供应技能返回的数据做最终决策
- **兜底**：数据供应技能返回空数据或出错时，有 fallback 路径
- **报告**：将数据供应技能的评估结果以人类可读格式呈现给用户

## 调用模板

```javascript
delegate_task({
  goal: "使用 <数据供应技能名> 技能搜索数据。\n\n" +
        "1. 加载：skill_view(name='<数据供应技能名>')\n" +
        "2. 按照该技能的工作流执行\n" +
        "3. 返回结构化 JSON 数据（不是显示文本）",
  context: "关键词：<提取的关键词>\n\n安全第一！仅搜索和评估，不执行任何操作。",
  toolsets: ['web', 'terminal', 'file']
})
```

## JSON 数据契约

数据供应技能和主技能之间的 JSON 格式是双方的**契约**。变更 JSON 结构必须同步更新双方：

| 字段 | 类型 | 说明 |
|------|------|------|
| `results[].name` | string | 技能名称 |
| `results[].safety.verdict` | `"safe_to_use"` / `"review_needed"` / `"unsafe"` | 安全判定 |
| `summary.total_found` | number | 找到总数 |
| `summary.safe_to_use` | number | 安全可用的数量 |
| `summary.recommendation.best_match` | string | 推荐技能名 |
| `summary.recommendation.reason` | string | 推荐理由 |
