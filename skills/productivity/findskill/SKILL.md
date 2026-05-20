---
name: findskill
description: "灵匠（hermes-skill-creator）的前置数据供应技能。被子代理调用，搜索本地已安装、Skills Hub、Skills.sh、GitHub 四个来源的技能信息，返回结构化 JSON 数据供灵匠的判断复用或新建流程。不安装任何技能，仅提供数据。又名「寻技」。"
version: 0.2.0
author: Lily (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [skills, search, data-provider, productivity]
    related_skills: [hermes-skill-creator]
---

# findskill（寻技）

**灵匠（hermes-skill-creator）的前置数据供应技能。**

寻技不直接面向用户。它被灵匠的 Step 0 通过 `delegate_task` 以子代理方式调用（⚡ **莉闪** 级别，常规搜索任务），搜索四个来源的技能信息，返回结构化数据供灵匠判断是**复用**还是**新建**。

不安装任何技能，不执行任何命令，仅提供搜索和评估数据，确保代码安全。

---

## 核心定位

```
灵匠 Step 0 → delegate_task(子代理+寻技)
                   ↓
            寻技搜索四源
              ├── 本地
              ├── Skills Hub
              ├── Skills.sh
              └── GitHub
                   ↓
            返回结构化 JSON
                   ↓
            灵匠判断：复用 or 新建
```

---

## When to Use

本技能**不由用户触发**。由灵匠（hermes-skill-creator）的 Step 0 在执行 `delegate_task` 时加载并使用。

---

## 子代理调用规范

### 调用方式

由灵匠 Step 0 通过 `delegate_task` 启动子代理：

```javascript
delegate_task({
  goal: "使用寻技（findskill）技能搜索技能数据。\n\n1. 加载寻技：skill_view(name='findskill')\n2. 按照寻技的工作流执行搜索\n3. 返回结构化 JSON 数据（不是显示文本）",
  context: "关键词：<从用户需求提取的关键词>\n\n按照寻技的搜索流程执行，返回 JSON。",
  toolsets: ['web', 'terminal', 'file']
})
```

### 子代理执行流程

子代理加载本技能后，按以下步骤执行：

#### 步骤 1: 提取搜索关键词

从 `context` 中的关键词出发，提取 2-3 组变体关键词。例如：

```
原始关键词: pdf extraction
变体: pdf, document extraction, OCR
```

#### 步骤 2: 四源并行搜索

使用 `web_search` 和 `terminal` 工具并行搜索：

| 来源 | 搜索命令 | 预期数据 |
|------|----------|----------|
| 🔍 **本地** | `skills_list()` → 匹配 name/description | 已安装技能的名称、分类、描述 |
| 🌐 **Skills Hub** | `web_search site:github.com hermes skill <关键词>` | Hub 上的社区和官方技能 |
| 🌐 **Skills.sh** | `web_search site:skills.sh <关键词>` | 评分、安装量、更新时间 |
| 🐙 **GitHub** | `web_search <关键词> site:github.com SKILL.md` | 未收录的社区技能 |

#### 步骤 3: 安全评估（5 维度）

对每个找到的技能，执行安全评估：

| 维度 | 评估标准 | 输出值 |
|------|----------|--------|
| 来源可信度 | 官方仓库 / trusted 标记 / 社区 / 个人 | `"official"` / `"trusted"` / `"community"` / `"personal"` |
| 代码安全 | 是否有 shell 注入、数据外泄风险 | `"safe"` / `"review_needed"` / `"unsafe"` |
| 依赖风险 | 是否需要外部 API / npx / 专有工具 | `"none"` / `"npx"` / `"api_key"` / `"proprietary"` |
| 维护状态 | 最近更新、star 数 | `"active"` / `"stable"` / `"inactive"` |
| 生态兼容 | 是否可在 Hermes Agent 中直接使用 | `"native"` / `"adaptable"` / `"incompatible"` |

#### 步骤 4: 返回结构化 JSON

搜索完成后，返回以下格式的 JSON 数据（不是显示文本，是纯数据）：

```json
{
  "query": {
    "original": "pdf extraction",
    "variants": ["pdf", "document extraction", "ocr"]
  },
  "results": [
    {
      "name": "pdf-extractor",
      "version": "v2.1",
      "description": "PDF text extraction, table recognition, OCR",
      "sources": {
        "skills_hub": {"found": true, "trust": "official", "identifier": "anthropics/skills/pdf-extractor"},
        "skills_sh": {"found": true, "trust": "official", "rating": 4, "installs": 2800},
        "github": {"found": true, "url": "https://github.com/anthropics/skills/tree/main/skills/pdf-extractor"}
      },
      "safety": {
        "source_trust": "official",
        "code_safety": "safe",
        "dependency_risk": "none",
        "maintenance": "active",
        "hermes_compatible": "native",
        "verdict": "safe_to_use"
      },
      "installed": false,
      "category": "productivity"
    },
    {
      "name": "pdf-to-markdown",
      "version": "v0.8",
      "description": "PDF to Markdown conversion, batch support",
      "sources": {
        "skills_sh": {"found": true, "trust": "community", "rating": 2},
        "github": {"found": true, "url": "https://github.com/user/pdf-to-markdown"}
      },
      "safety": {
        "source_trust": "community",
        "code_safety": "safe",
        "dependency_risk": "npx",
        "maintenance": "stable",
        "hermes_compatible": "adaptable",
        "verdict": "review_needed"
      },
      "installed": false,
      "category": "utility"
    }
  ],
  "summary": {
    "total_found": 3,
    "safe_to_use": 1,
    "review_needed": 1,
    "unsafe": 0,
    "already_installed": 0,
    "recommendation": {
      "best_match": "pdf-extractor",
      "reason": "官方来源、多源一致、无外部依赖、活跃维护"
    }
  }
}
```

#### 步骤 5: 结论

返回 JSON 后，追加一句结论供灵匠使用：

```text
搜索完成。安全可用的技能 X 个，需审查的 Y 个。推荐使用 <name>。
```

---

## 数据格式规范

### 安全评估字段说明

| 字段 | 可能值 | 含义 |
|------|--------|------|
| `safety.verdict` | `"safe_to_use"` | 5 维度全部通过，可直接复用 |
| | `"review_needed"` | 1-2 项有问题，需人工审查 |
| | `"unsafe"` | 3+ 项有问题，禁止复用 |
| `safety.source_trust` | `"official"` | 官方仓库或 trusted 来源 |
| | `"trusted"` | 社区但带 trusted 标记 |
| | `"community"` | 社区贡献，未考证 |
| | `"personal"` | 个人仓库，需警惕 |
| `safety.hermes_compatible` | `"native"` | 已有技能，HERMES 原生可用 |
| | `"adaptable"` | 来自其他平台，需适配 |
| | `"incompatible"` | 依赖专有工具，无法使用 |

### verdict 的分级决策规则

| Verdict | 处理方式 |
|---------|----------|
| `safe_to_use` | 灵匠直接进入复用流程的 R2 |
| `review_needed` | 灵匠走安全审查+适配，向冰哥报告 |
| `unsafe` | 灵匠直接拒绝，回到 Step 1 新建 |

---

## 安全红线

1. **绝不安**装任何技能 — 寻技只搜索和评估数据
2. **绝不执**行外部命令 — 仅使用 `web_search` 和 `skills_list()` 做只读操作
3. **绝不写**入用户系统 — 不创建文件、不修改配置
4. **数据透明** — 每个技能的 verdict 必须附带具体评估理由
5. **宁缺毋滥** — 不确定安全时一律标 `review_needed`，不放低标准

---

## 与灵匠的分工

| 职责 | 寻技 | 灵匠 |
|------|------|------|
| 搜索技能 | ✅ 四源搜索 | ❌ |
| 数据评估 | ✅ 安全 5 维度评估 + JSON 结构化 | ❌ |
| 安装/适配 | ❌ | ✅ 复用流程 / 新建流程 |
| 安全审查执行 | ❌ 仅提供数据 | ✅ 基于寻技数据做决策 |
| 向冰哥报告 | ❌ | ✅ 格式化的复用建议 |
| 代码适配 | ❌ | ✅ 工具映射 + 双子审查 |

---

## 常见陷阱

1. **Skills.sh 是 JS 渲染的 SPA** — `web_search site:skills.sh <关键词>` 不一定能获取到有效结果，因为 skills.sh 是 Next.js 应用，页面内容通过 JavaScript 动态渲染。`curl` 获取的是 HTML 框架而非数据。替代方案：通过 Skills Hub（`hermes skills search`）或 GitHub 搜索来补充。

2. **GitHub API 未认证时有限流** — 未提供 GitHub Token 时，API 搜索限制为 10 次/分钟，代码搜索需要认证。大规模搜索时注意避免触发限流。

3. **同一个技能不同来源信息可能不一致** — Skills Hub、Skills.sh、GitHub 对同一技能的评分、版本、描述可能不同。以可信度最高的来源为准，可信度相同时以 Skills.sh（通常更新更及时）为准。

4. **中文关键词搜索效果不如英文** — 大多数技能的 name 和 description 是英文。中文关键词搜索可能返回较少结果。建议同时尝试英文同义词。

5. **JSON 输出必须有 recommendation 字段** — 灵匠的决策逻辑依赖 `summary.recommendation`。缺少该字段会导致灵匠不知道推荐哪个技能。确保每个搜索结果都包含 recommendation。

---

## 更新日志

- **v0.2.0** — 重构为灵匠数据供应技能。去掉用户交互和安装相关内容，改为子代理调用的结构化 JSON 输出，加入安全 5 维度评估和数据格式规范。添加 dual-skill-collaboration 参考文档。
- **v0.1.0** — 初始版本，多源智能搜索工具
