---
name: hermes-skill-creator
description: "创建新技能、修改和优化现有技能、评估技能性能的完整工作流。当用户想创建技能、优化已有技能、运行评估测试、或对技能进行对比分析时使用。又名「灵匠」。"
version: 0.12.0
author: Lily (adapted from anthropics/skills/skill-creator)
license: MIT
metadata:
  hermes:
    tags: [skills, authoring, eval, testing, productivity]
    related_skills: [hermes-agent-skill-authoring, daily-morning-report, video-summary, findskill]
    source:
      name: skill-creator
      repo: https://github.com/anthropics/skills
      path: skills/skill-creator/SKILL.md
      commit: b0cbd3df1533
      commit_date: "2026-03-06"
      file_hash: dcd4803e61e913e6fc27294184cd3a71f09f5e924ff20c8a9a20173e7b3c2bcf
      adapted_by: Lily (Hermes Agent)
      adapted_at: "2026-05-13"
---

# Hermes Skill Creator（灵匠）

一个专为 **Hermes Agent** 适配的技能创建与迭代优化工作流，中文名「灵匠」—— 以灵动匠心雕琢技能。

本技能改编自 Anthropic 官方 `skill-creator`（[anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)），将原本为 Claude Code 设计的流程映射到 Hermes Agent 的 tool-based 环境中。

---

## 核心工作流概览

```
┌─────────────────────────────────────────────────┐
│ 0. delegate_task 调用「寻技」搜索          │
│    - delegate_task → 子代理加载寻技               │
│    - 寻技自动搜索四源（本地/Hub/Skills.sh/GitHub）    │
├──────────────┬──────────────────────────────────┤
│ safe_to_use  │ review_needed                     │
│ 快捷复用     │ 完整复用                          │
│ 直接装       │ 安全审查+适配+报告                │
├──────────────┼──────────────────────────────────┤
│              │ 1. 捕捉意图 (Capture Intent)         │
│              │    - 从对话中提取用户需求             │
│              ├─────────────────────────────────────┤
│              │ 2. 访谈与研究 (Interview & Research)  │
│              │    - 深入理解格式/边界/依赖            │
│              ├─────────────────────────────────────┤
│              │ 3. 撰写 SKILL.md (Write SKILL.md)    │
│              │    - 编写前端 YAML + Markdown 正文   │
│              ├─────────────────────────────────────┤
│              │ 4. 创建评估用例 (Create Evals)         │
│              │    - 编写 evals.json 测试用例          │
│              ├─────────────────────────────────────┤
│              │ 5. 运行测试 → 评分 → 聚合 → 审查     │
│              │    delegate_task + grader + benchmark │
│              ├─────────────────────────────────────┤
│              │ ↻ 迭代优化 (Iterate)                  │
│              │    根据反馈改进 → 重新测试 → 重复      │
└──────────────┴──────────────────────────────────┘
```

---

## When to Use

| 场景 | 说明 |
|------|------|
| 🆕 **创建新技能** | 用户想要创建一个全新的技能来捕获某个工作流 |
| 🔧 **优化现有技能** | 已有技能，但想改进它的行为或性能 |
| ♻️ **复用现有技能** | 在 Hub 或本地找到功能相近的技能，进行安全审查后适配复用 |
| 🧪 **运行评估** | 想测试一个技能在多个场景下的表现 |
| 📊 **对比分析** | 想对比带技能和不带技能的输出差异 |
| 🎯 **优化描述** | 调整技能的 description 以提高触发准确率 |
| 📦 **打包分发** | 将技能目录打包为可分享的格式 |

---

## Hermes Agent 工具对照表

这是本技能适配的核心——将 Claude Code 的 CLI 操作映射到 Hermes Agent 的 tool-based API：

| 操作 | 原始 skill-creator（Claude Code） | Hermes Agent 适配版 |
|------|------|------|
| 创建技能文件 | 写文件到 `skills/<name>/SKILL.md` | `skill_manage(action='create', name='xxx', content='...')` |
| 编辑技能 | 直接编辑 SKILL.md | `patch(path=..., old_string=..., new_string=...)` |
| 读取技能 | `cat /path/to/skill/SKILL.md` | `skill_view(name='xxx')` |
| 列出技能 | `ls skills/` | `skills_list()` |
| 运行测试 | `claude -p "prompt"` | `delegate_task(tasks=[{goal: "prompt", toolsets: ['terminal', 'file']}])` |
| 子代理并行 | Claude Code 原生 | `delegate_task(tasks=[...])` 自动并行 |
| 文件读取 | `cat / read` | `read_file(path)` |
| 文件搜索 | `grep / find` | `search_files(pattern, path)` |
| 文件写入 | `write` | `write_file(path, content)` |
| Python 脚本 | `python script.py` | `terminal(command="python script.py")` |
| 技能目录路径 | `~/.claude/commands/` | `~/.hermes/skills/<category>/<name>/` |
| 基准测试 | `claude -p` 不同参数 | `delegate_task` + `aggregate_benchmark.py` |

---

## Creating a Skill

### Step 0: 调用「寻技」搜索数据（Search via findskill）

接到创建新技能的需求后，**不要直接开始写**。先通过 `delegate_task` 启动子代理（⚡ **莉闪** 级别，日常搜索任务）加载寻技（findskill）来搜索数据。寻技会返回结构化的 JSON 评估数据，供后续判断。

#### 操作方式

```javascript
// ⚡ 莉闪 — 搜索任务是常规信息搜集，用闪速模型即可
delegate_task({
  model: {model: "deepseek-v4-flash"},
  goal: "使用寻技（findskill）技能搜索技能数据。\n\n1. 加载寻技：skill_view(name='findskill')\n2. 按照寻技的工作流执行四源搜索\n3. 返回结构化 JSON 数据（不是显示文本）",
  context: "关键词：<从用户需求提取的关键词>\n\n安全第一！仅搜索和评估，不安装任何技能。",
  toolsets: ['web', 'terminal', 'file']
})
```

#### 寻技返回的数据格式

寻技返回的 JSON 中包含 `summary.recommendation` 字段，直接指示最佳选择：

```json
{
  "results": [...],
  "summary": {
    "total_found": 3,
    "safe_to_use": 1,
    "review_needed": 1,
    "unsafe": 0,
    "recommendation": {
      "best_match": "pdf-extractor",
      "reason": "官方来源、多源一致、无外部依赖、活跃维护"
    }
  }
}
```

每个结果中的 `safety.verdict` 决定了后续路径：

| Verdict | 含义 | 后续操作 |
|---------|------|----------|
| `safe_to_use` | 安全可用 | **直接复制使用**（跳过安全审查和适配） |
| `review_needed` | 需审查 | 进入完整复用流程（安全审查 + 适配） |
| `unsafe` | 不安全 | **跳过该技能**，继续看下一个 |

#### 搜索结果判断

```text
寻技搜索返回 JSON
        ↓
提取 summary.recommendation 和 results
        ↓
遍历 results：
  unsafe → 跳过
  review_needed → 标记审查
  safe_to_use → 候选
        ↓
有 safe_to_use 的匹配？ ──是──→ 「快速复用」：直接安装使用
        ↓ 否
有 review_needed 的匹配？ ──是──→ 「完整复用流程」：安全审查 + 适配 + 报告
        ↓ 否
进入 Step 1: 创建新技能
```

**"功能相近"的标准：** 该技能的核心能力能覆盖用户需求的 60% 以上，或者稍加修改即可覆盖。

#### 🚨 关键检查：用户偏好（User Preference Check）

**在进入「创建新技能」流程前，必须先问一个问题：**

> "找到了 <最近匹配技能名>（来源：<Hub/GitHub>，安装量：<N>），你是想直接装这个现成的，还是让我自己写一个？"

**为什么必须问：**
- 冰哥的明确偏好：**优先装现成的，不信任我们自己写的原创内容**（尤其是代码/HTML相关技能）
- 冰哥的原话："我需要的是复制网上的技能（介于昨天html代码修复问题我们能力是值得怀疑的）"
- 信任信号：网上已有技能经过大量用户验证（如obra/superpowers = 92.9K⭐，166K安装量），比自己写的更可靠

**决策树：**
```text
寻技搜索返回结果
  ↓
有功能相近的（覆盖60%+需求）？
  ├── 是 → 询问冰哥：「直接装这个现成的还是自己写？」
  │     ├── 冰哥说「直接装」 → 走复用流程
  │     └── 冰哥说「自己写」 → 走Step 1
  └── 否 → 仍然先问冰哥是否想找替代品
        ├── 是 → 再搜，搜不到就装最近似的
        └── 否 → 走Step 1
```

**区分「灵感来源记录」与「直接复用」：**
| 用户选择 | 后续操作 | SKILL.md metadata |
|:---------|:---------|:------------------|
| 直接安装现成技能 | 安装后不改内容 | 正常安装，无特殊标注 |
| 受启发后自己写 | 全新创作，记录灵感来源 | `metadata.source.inspired_by` |
| 适配后使用 | 修改后再安装 | `metadata.source.adapted_from` |

**新增 Pitfall #20：** 不要假设用户想要原创内容。即使寻技没找到100%匹配，也要先问「要不要装最近似的现成技能」再决定是否新建。冰哥明确表达过不信任莉莉丝的原创代码质量（尤其中文名+HTML+技能内容），直接装Hub上的比自己写更安全。

### Step 1: Capture Intent（仅在确定需要新建时执行）

从对话中提取用户意图。从已有对话历史中找答案：

1. **这个技能应该做什么？**
2. **什么情况下应该触发？**（用户说什么话/做什么事时触发）
3. **输出格式是什么？**
4. **是否设置测试用例？**
   - 客观可验证的输出（文件转换、数据提取、代码生成、固定工作流）→ 适合测试
   - 主观输出（写作风格、设计）→ 通常不需要测试

### Step 2: Interview and Research

主动询问边界情况、输入/输出格式、示例文件、成功标准和依赖。

---

### 复用现有技能（Reuse Flow）

当 **Step 0** 通过寻技搜索到功能相近的现有技能时，根据寻技返回的 `safety.verdict` 走不同路径：

| Verdict | 路径 | 说明 |
|---------|------|------|
| `safe_to_use` | **快捷复用**（下方） | 寻技已做完全安全审查，直接装 |
| `review_needed` | **完整复用**（下方） | 寻技标记了风险，需人工审查+适配 |
| `unsafe` | **跳过** | 寻技判定不安全，放弃此技能 |

---

#### 快捷复用（safe_to_use 路径）—— 直接使用

寻技已通过安全 5 维度审查给出 `safe_to_use` 结论，**无需再次审查和适配**。

```text
安全评估：src_trust=official ✓ | code=safe ✓ | dep=none ✓ | mnt=active ✓ | compat=native ✓
判定：safe_to_use — 直接复制使用
```

**操作步骤：**

```bash
# 从 Hub 安装（最快）
hermes skills install <identifier>

# 或手动复制目录
cp -r ~/.hermes/skills/<source>/<name>/ ~/.hermes/skills/<category>/<name>/
```

向冰哥告知技能已就绪：

```text
找到候选技能：<name>
来源：<多源>
安全审查：✅ 通过（寻技自动审查，verdict=safe_to_use）
操作：已安装
```

---

#### 完整复用（review_needed 路径）—— 审查 + 适配

寻技标记了 `review_needed`，需要人工介入走完整流程。

#### 流程概览

```
找到候选技能 → 安全审查 → 确认可复用 → 代码适配 → 交付
```

#### Step R1: 安全审查（Security Review）

对候选技能执行通用的【安全检查】中定义的 5 个审查维度。具体标准见上方「安全检查」一节。

#### Step R2: 确认可复用（Confirm Reusability）

向冰哥报告搜索结果和安全审查结论，格式如下：

```
找到候选技能：<name>（<来源>）
描述：<description>
安全审查：✅ 通过 / ❌ 不通过
复用建议：
  - 可直接安装使用
  - 需适配后使用（说明需要改什么）
  - 不推荐（说明原因）
```

等待冰哥确认后再进行下一步。

#### Step R3: 代码适配（Code Adaptation）

如果技能来自其他平台（Claude Code、Cursor 等）或版本不同，需要适配到 Hermes Agent：

**工具映射规则（同本技能的 Hermes Agent 工具对照表）：**

| 原平台 | Hermes Agent |
|--------|-------------|
| `claude -p "..."` | `delegate_task({goal: "..."})` |
| 直接编辑文件 | `write_file` / `patch` / `read_file` |
| shell 命令 | `terminal(command="...")` |
| 依赖于 `.claude/commands/` | 改为 `~/.hermes/skills/<category>/<name>/` |

**适配完成后建议用双子代理并行审查**，参见「双视角并行代码审查」一节。

#### Step R4: 安装与交付

```bash
# 如果来自 Hub
hermes skills install <identifier>

# 如果手动适配
# 直接使用 skill_manage 或 write_file 创建目录
```

告知冰哥技能已就绪。如果经过了适配，说明改动范围。

---

### 安全检查（Security Check）—— 写之前必做

无论新建、复用还是修改，**在开始写 SKILL.md 之前**，必须对技能内容做一轮安全审查。这是硬性要求，不可跳过。

审查以下 5 个维度：

| 审查项 | 检查内容 | 通过标准 |
|--------|----------|----------|
| 🔐 **来源可信度** | 发布者/仓库是否可信（官方、trusted 标记、知名作者） | 避免来路不明的技能 |
| 🔍 **代码审查** | SKILL.md 中是否有恶意指令、后门、数据外泄风险 | 无 shell 注入、无敏感数据发送 |
| 🛡️ **原则无意外** | 技能描述与实际行为是否一致 | 不存在"隐藏行为" |
| 📋 **依赖检查** | 技能是否依赖外部服务、API Key、专有工具 | 依赖需在 Hermes Agent 可用范围内 |
| 🪪 **许可检查** | 技能的 license 是否允许修改和再分发 | MIT / Apache-2.0 优先 |

**不通过的后果：**

| 情况 | 处理方式 |
|------|----------|
| 新建技能 → 检查不通过 | 修复问题后才能继续写 |
| 复用技能 → 检查不通过 | **拒绝复用**，回到 Step 1 从零创建 |
| 修改技能 → 发现原有问题 | 标记已知风险，向冰哥报告后再决定 |

**每次修改后重新检查：** 对 SKILL.md 做任何修改（patch / edit / rewrite）后，重新快速审查一遍修改部分，确保没有引入新的安全风险。

---

### Step 3: Write the SKILL.md

#### 技能目录结构

```
~/.hermes/skills/<category>/<name>/
├── SKILL.md              # 必需 - 主技能文件（YAML前端 + Markdown正文）
├── references/           # 可选 - 参考文档（按需加载到上下文）
│   ├── schemas.md
│   ├── workflow-comparison.md
│   └── dual-skill-collaboration.md  # 双技能协作模式（子代理数据供应架构）
├── scripts/              # 可选 - Python 脚本（确定性/重复性任务）
│   ├── aggregate_benchmark.py
│   └── quick_validate.py
├── agents/               # 可选 - 子代理指令
│   ├── grader.md
│   └── analyzer.md
└── assets/               # 可选 - 模板/图标/字体
```

#### YAML 前端格式

```yaml
---
name: skill-name               # 小写+连字符，≤64字符
description: "Use when ..."    # 触发条件 + 行为描述，≤1024字符
version: 1.0.0                 # 版本号
author: Hermes Agent           # 作者
license: MIT                   # 许可
metadata:
  hermes:
    tags: [tag1, tag2]          # 分类标签
    related_skills: [other]     # 相关技能
---
```

#### 灵感来源记录（Inspiration Source Documentation）

当技能的设计灵感来自外部项目（同名启发、功能参考、概念迁移），新增 `metadata.source.inspired_by` 字段记录参考来源：

```yaml
metadata:
  hermes:
    source:
      inspired_by:
        - name: "obra/superpowers"
          url: "https://github.com/obra/superpowers"
          relation: "name_inspiration"      # name_inspiration / concept_reference / partial_adaption
        - name: "garrytan/gstack"
          url: "https://github.com/garrytan/gstack"
          relation: "name_inspiration"
```

**与 adapted_from 的区别：**
| 字段 | 适用场景 |
|:----|:---------|
| `adapted_from` | 代码/内容直接来自上游仓库，做了本地适配 |
| `inspired_by` | 仅名字/概念受到启发，内容为全新原创 |

**这样做的好处：**
- **可追溯** — 后续审查时知道设计背景和灵感来源
- **避名权** — 明确标注灵感来源，避免被误认为抄袭
- **助审查** — 当让 🚀 大莉等子代理做技能审核时，灵感来源信息帮助审查者理解设计决策上下文

---

#### 渐进式披露（Progressive Disclosure）

Hermes Agent 的三级加载系统：
1. **元数据**（name + description）→ 始终在上下文中（~100 词）
2. **SKILL.md 正文** → 技能被触发时加载（建议 <500 行）
3. **references/ 等资源** → 按需加载（无限制）

**关键模式：**
- SKILL.md 保持在 500 行以下；接近时增加层级 + 清晰指引
- 从 SKILL.md 中明确引用 reference 文件及其使用时机
- 大型 reference 文件（>300 行）应包含目录

#### 原则：无意外（Principle of Lack of Surprise）

技能必须不包含恶意代码、漏洞利用代码或任何可能损害系统安全的内容。技能的内容不应在描述其意图时让用户感到意外。不要配合创建误导性技能或旨在促进未授权访问、数据泄露或其他恶意活动的技能。类似"扮演 XYZ"这样的角色扮演技能是可以的。

#### 编写风格

- 使用命令式语气（"执行"、"检查"、"确保"）
- 解释为什么重要，而不仅仅说必须要做
- 保持通用，不局限于具体示例
- 使用示例模式展示输入/输出：

```markdown
**示例 1：**
输入：用户说"把这个 CSV 转成表格"
输出：调用脚本 parse_csv.py → 生成 HTML table
```

### Step 4: Create Test Cases

技能草稿完成后，编写 2-3 个真实的测试 Prompt。

保存测试用例到 `evals/evals.json`：

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "name": "basic-csv-to-table",
      "prompt": "用户的实际任务描述",
      "expected_output": "期望结果的描述",
      "files": [],
      "expectations": [
        "输出包含表格标题行",
        "输出来自脚    本 parse_csv.py"
      ]
    }
  ]
}
```

查看 `references/schemas.md` 了解完整的 JSON schema。

---

## Running and Evaluating Test Cases

这是核心迭代循环——以下步骤必须按顺序连续执行，不要中途停下。

### 工作区目录结构

```
<skill-name>-workspace/
├── iteration-1/
│   ├── eval-<name>/
│   │   ├── eval_metadata.json
│   │   ├── with_skill/
│   │   │   ├── run-1/
│   │   │   │   ├── outputs/      # 输出文件
│   │   │   │   ├── timing.json
│   │   │   │   └── grading.json  # 评分结果
│   │   │   └── run-2/
│   │   └── without_skill/
│   │       └── run-1/
│   └── benchmark.json
│   └── benchmark.md
├── iteration-2/
└── ...
```

### Step 1: 并行启动所有测试运行

对于每个测试用例，**在同一轮**中启动两个子代理——一个带技能，一个不带（作为 baseline）。

**使用 `delegate_task(tasks=[...])` 并行启动：**

```javascript
delegate_task({
  tasks: [
    // 带技能的测试
    {
      goal: "执行这个任务，使用指定的技能文件。\n- 技能路径：<path-to-skill>\n- 任务：<eval prompt>\n- 输出保存到：<workspace>/iteration-N/eval-<name>/with_skill/run-1/outputs/\n- 最终输出：<期望的输出文件>",
      toolsets: ['terminal', 'file', 'web']
    },
    // baseline 测试（不带技能）
    {
      goal: "执行这个任务（不带任何技能辅助）。\n- 任务：<eval prompt>\n- 输出保存到：<workspace>/iteration-N/eval-<name>/without_skill/run-1/outputs/",
      toolsets: ['terminal', 'file', 'web']
    }
  ]
})
```

**不同的 baseline 场景：**
- **创建新技能**：baseline = 不带任何技能
- **改进已有技能**：先快照原技能（`read_file` 或 `skill_view`），baseline 指向快照版

同时为每个 eval 目录写入 `eval_metadata.json`：

```json
{
  "eval_id": 1,
  "eval_name": "basic-csv-to-table",
  "prompt": "用户的原始 prompt",
  "assertions": []
}
```

### Step 2: 在测试运行期间编写断言

不要干等运行结束——利用这段时间为每个测试用例编写定量断言。

**好的断言：** 客观可验证、有描述性名称、一眼就能看出检查什么
**不适合断言的情况：** 写作风格、设计质量等主观判断

更新 `eval_metadata.json` 中的断言字段：

```json
{
  "eval_id": 1,
  "eval_name": "basic-csv-to-table",
  "prompt": "用户的原始 prompt",
  "assertions": [
    {
      "text": "输出文件是一个 HTML 文件",
      "description": "验证输出格式是否为 HTML"
    },
    {
      "text": "表格包含 CSV 中的所有数据列",
      "description": "验证数据完整性"
    }
  ]
}
```

### Step 3: 捕获耗时和 Token 数据

子代理任务完成后，立即保存 `timing.json`（`delegate_task` 返回的结果中包含 `total_tokens` 和 `duration_ms`，需立即保存）：

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: 评分、聚合与审查

#### 4a: 评分每个运行

对每个运行的输出，用子代理去做评分——子代理读取 `agents/grader.md` 中的指令来评估每条断言：

```javascript
delegate_task({
  goal: "作为评分代理（Grader），评估以下断言。\n\n断言列表：<assertions>\n输出目录：<workspace>/iteration-N/eval-<name>/with_skill/run-1/outputs/\n\n按照 grader.md 的流程评分，输出 grading.json 到 <output_dir>/grading.json\n\ngrader.md 内容：\n<读取 agents/grader.md 的内容传入>",
  toolsets: ['terminal', 'file']
})
```

**grading.json 的 expectations 数组必须使用字段：`text`、`passed`、`evidence`（不要用 `name`/`met`/`details`）。**

#### 4b: 聚合为 benchmark

运行聚合脚本生成统计分析：

```bash
cd ~/.hermes/skills/productivity/hermes-skill-creator
python scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name "<name>"
```

这会生成 `benchmark.json` 和 `benchmark.md`，包含 pass_rate、time、tokens 的均值 ± 标准差和 delta。

#### 4c: 分析师视角

阅读 benchmark 数据，发现聚合统计可能隐藏的模式：

- **始终通过的断言**（两种情况都通过）→ 不能区分技能价值
- **高方差的评估** → 可能不稳定
- **时间/token 权衡** → 技能增加了多少开销？

#### 4d: 生成审查报告

`scripts/generate_report.py` 可以从 benchmark 结果生成静态 HTML 报告供用户查看：

```bash
cd <skill-creator-path>/scripts
python generate_report.py <workspace>/iteration-N --static <output_path>/review.html --skill-name "<skill-name>"
```

- `--static <path>` 指定静态 HTML 输出路径（不必启动 HTTP server）
- `--benchmark <path>` 可选，指定 benchmark.json 路径
- 报告包含性能汇总表、每个 eval 的详细结果、断言逐条检查和备注

生成后告诉用户报告路径，让用户打开查看并给出反馈。如果用户不能打开 HTML，也可以直接向他们展示关键数据：通过率、耗时对比、主要改进点。

### Option B：双视角并行代码审查（Dual-Subagent Code Review）

当工作涉及**从其他平台适配代码到 Hermes Agent**（如技能迁移、脚本适配），建议在初次完成后使用**两个子代理并行审查**，分别关注不同维度：

```javascript
delegate_task({
  model: {model: "deepseek-v4-pro"},  // 高阶模型加速审查
  tasks: [
    {
      // 子代理 1：功能一致性审查
      goal: "审查适配版代码的功能一致性。需要阅读并对比原版和适配版的所有文件，逐一评估...",
      toolsets: ['web', 'terminal', 'file']
    },
    {
      // 子代理 2：差异修改合理性审查
      goal: "审查适配版对原版做的修改是否合理。分析每个差异、移除项、新增项...",
      toolsets: ['web', 'terminal', 'file']
    }
  ]
})
```

**分工原则：**
- **子代理 1（功能一致性）**：对比原版和适配版的代码逻辑、输出格式、接口——确保功能不退化
- **子代理 2（修改合理性）**：检查工具映射是否正确、移除的功能是否合理、是否有断裂引用——确保改动有意义

**适合的场景：**
- 从 Claude Code 迁移技能到 Hermes Agent
- 适配第三方脚本（Python、Bash）到 Hermes 环境
- 大型代码重用/跨平台移植工作

### Step 5: 读取反馈并迭代

### 如何改进技能（Improving the Skill）

改进是迭代循环的核心。运行测试、用户审查结果后，需要基于反馈改进技能。

#### 1. 从反馈中泛化（Generalize from Feedback）

技能将被反复使用很多次。当前在少量示例上迭代是为了快速推进，但如果技能只适用于这些示例，那就没有价值。与其过度拟合（overfit）或加入过于严格的 MUST，不如尝试不同的思路或模式。

#### 2. 保持精简（Keep it Lean）

删除不必要的内容。阅读 transcript（而不仅仅是最终输出）——如果技能让模型浪费大量时间做无产出的事情，尝试删除导致这种行为的部分。

#### 3. 解释原因（Explain the Why）

努力解释每件事的"为什么"。当前的 LLM 很智能，它们有良好的理论心智（theory of mind），在好的框架下可以超越死板的指令真正创造价值。如果发现自己在用 ALWAYS 或 NEVER 全大写，或在用极其僵化的结构——这是黄旗信号。重构并解释推理过程，让模型理解为什么你要求的事情很重要。

#### 4. 寻找跨测试用例的重复工作（Look for Repeated Work）

阅读测试运行的 transcript，注意子代理是否都独立编写了类似的辅助脚本或采取了相同的多步骤方法。如果所有测试用例都导致子代理写了 `create_docx.py` 或 `build_chart.py`，这是强烈的信号——技能应该打包这个脚本。写一次，放到 `scripts/` 中，告诉技能使用它。这样每次调用都不必重新发明轮子。

### 终止条件

当以下任一条件满足时停止迭代：
- 用户说满意了
- 反馈全部为空（用户查看了所有输出，没有提意见）
- 连续两轮没有有意义的改进

---

### Step 6: 交付前准备（Pre-delivery）

技能迭代完成后，在交付前完成以下收尾工作：

#### 6a: 起中文名

冰哥的习惯是所有技能都要有一个中文名。在 SKILL.md 的标题和 description 中加入中文名：

```markdown
# skill-name（中文名）

多源智能技能搜索工具。又名「中文名」。
```

中文名风格参考：简洁、有涵义、两个字的优先（灵匠、寻技等）

#### 6b: 来源追溯 + 更新检查脚本

如果技能是从上游仓库适配而来（如 anthropics/skills、GitHub 社区仓库），在 `metadata.source` 中记录追踪信息，并创建 `scripts/check_upstream_updates.py`：

```yaml
source:
  name: original-skill-name
  repo: https://github.com/author/repo
  path: path/to/SKILL.md
  commit: abcdef123456
  commit_date: "2026-05-14"
  file_hash: abc123...
  adapted_by: Lily (Hermes Agent)
  adapted_at: "2026-05-14"
```

更新检查脚本只需读取 source 元数据、联网比对 GitHub API 的 commit 和文件哈希、输出差异。

#### 6c: 版本号 + git 初始化（按来源类型决定）

Git 不是所有技能都要建的。冰哥的规则：

| 技能来源 | Git？ | 原因 |
|---------|:-----:|------|
| 🌐 **网上来的**（anthropic/skills、obra/superpowers、GitHub 社区等） | ✅ **必须 Git** | 日后联网更新出问题可以回滚 |
| 🏠 **自己写的（日常维护）** | ❌ 不用 | 自己维护，无外部同步风险 |
| 🏠 **自己写的（大功能改动前）** | ✅ **建议 Git** | 冰哥实测：改动大功能（如接入新 provider、重构核心逻辑）时没有 git 会很被动。改动前 git init + commit 快照，改完打标签，方便回滚 |
| 🔗 **配套技能**（如 A 的更新需要 B 也改） | ✅ **都要 Git** | 即使是自己写的，也要防版本冲突 |

```bash
# 网上来的技能 — 建 Git + 打标签
cd ~/.hermes/skills/<category>/<name>/
git init && git add -A && git commit -m "init: xxx v<version> — <来源>"
git tag -a "v<version>" -m "xxx v<version> — <说明>"

# 自己写的技能 — 不用建
# 直接在 SKILL.md 里更新 version 字段即可
```

> 💡 **来源判断**：SKILL.md 的 `author` 和 `metadata.source` 字段会写明来源。`adapted from obra/superpowers` = 网上来的。只有 author 没写来源的才是自己写的。

#### 6d: 额外检查

在通用 Checklist 基础上额外检查：
- [ ] 中文名已在 title 和 description 中体现
- [ ] 如果是适配技能，source 元数据完整（commit + file_hash）
- [ ] check_upstream_updates.py 已创建且可运行
- [ ] .gitignore 已配置，排除了不需要追踪的文件
- [ ] SKILL.md version 字段与 git tag 一致

---

## Description Optimization（可选）

技能创建完成后，可以优化 description 字段，提高触发精准度。

### Step 1: 生成触发评估查询

创建 20 个评估查询——混合应该触发和不应该触发的场景：

```json
[
  {"query": "用户的实际 Prompt", "should_trigger": true},
  {"query": "另一个 Prompt", "should_trigger": false}
]
```

- **应该触发（8-10 个）**：覆盖不同措辞、正式/非正式风格、包含不直接命名技能但明显需要它的场景
- **不应该触发（8-10 个）**：最有价值的是"擦边球"——共享关键词但实际需要不同的场景

### Step 2: 与用户审查

将评估集展示给用户审查和调整。

### Step 3: 手动优化描述

根据评估集，手动调整 SKILL.md 中的 description 字段：

- 加入用户实际使用的关键词和短语
- 使 description "推一把"（slightly pushy），对抗模型倾向于不触发技能的趋势
- 包含具体的使用场景说明

### Step 4: 展示前后对比

向用户展示优化前后的 description diff，确认修改。

---

## Common Pitfalls

1. **不要用 `skill_manage(action='create')` 创建脚本目录的结构** — 对于需要 scripts/ 或 references/ 的技能，用 `write_file` 逐个创建文件和目录层级

2. **delegate_task 结果不包含完整的运行详细信息** — 子代理的返回是其自主报告的摘要，不是可验证的事实。对于文件创建等操作，需要自己 verify 文件是否确实创建成功

3. **delegate_task 的 timeout 限制** — 默认父代理等待子代理的超时是 600 秒。复杂任务的 baseline 和 with-skill 运行都要在时间内完成

4. **不要在 SKILL.md 中放入 Claude Code 特有的命令** — 全部替换为 Hermes Agent 的工具调用（`skill_manage`、`delegate_task`、`write_file`、`patch`、`read_file` 等）

5. **description 不要过于狭窄** — 描述应该覆盖触发场景的类别，而不是单个任务。如 "Use when converting data formats..." 而不是 "Use to convert CSV to HTML"

6. **确保 YAML 前端正确** — 前端必须以 `---` 开头（第 0 字节），以 `\n---\n` 闭合。不能有前导空白

7. **技能生效需要新会话** — 当前会话的技能缓存已固定。新建会话后 `skills_list`/`skill_view` 才能看到新技能

8. **多语言内容** — 如果用户使用中文，确保描述和 SKILL.md 正文使用中文编写，否则触发模型可能不会识别

9. **LLM 对断言评估的一致性** — 使用 LLM 子代理做评分时，同一断言在不同运行中可能得到不同结果。设置多个运行（run-1, run-2, run-3）来平滑方差

10. **不要并行启动过多子代理** — `delegate_task` 的最多并行数是 3（可配）。超出上限的任务会排队

11. **delegate_task 在大任务上可能超时，要有回退计划** — 默认超时 600 秒（10 分钟）。对于需要大量文件创建、多 URL 抓取或多个步骤循环的大型适配任务，子代理可能超时。**不要连续重试**同一个超时的大任务，改为手动分步骤执行：先获取参考数据，再逐一创建文件，最后验证。

12. **代码审查发现的问题要及时修复** — 双子代理审查报告中的每个 ❌ 问题都是优先修复项。先修高风险（YAML 解析器、断裂引用），再修中低风险（字段缺失、步骤不完整）。修复后重新验证。

13. **子代理适配大技能易超时，不要重试** — 当子代理处理大型技能（SKILL.md 44KB+、多个脚本+MB级CSV知识库）时，delegate_task 默认 600s 超时可能不够。**不要原地重试**——重试只会再等 600s。改为手动分步：先审查源码，然后逐一 write_file 创建文件，最后验证。

14. **版本号规则必须先问冰哥确认，不要擅自假设** — 冰哥有自己的一套版本规则：初始 v0.1.0，新增功能 +0.1，内部修改 +0.0.1。次版本满 10 自然进位（0.9.0 → 0.10.0）。大版本更新必须先问冰哥，如果他说不生则继续累加次版本号（0.10.0 → 0.11.0 → ...），而不是跳到 1.0.0。

15. **Step 0 通过 delegate_task 调用寻技，不直接 skill_view** — 寻技现在是一个子代理技能，通过 `delegate_task(toolsets=['web', 'terminal', 'file'])` 调用，而不是直接 `skill_view()`。子代理自行加载寻技，搜索完成后返回 JSON 数据。

16. **写之前不做安全检查就是挖坑** — 安全检查是硬性门槛，无论新建、复用还是修改都必须执行。跳过这一步可能在后续迭代中才发现安全问题（如外部依赖、API Key 泄露），返工成本更高。

17. **技能间数据供应关系：数据提供技能应被子代理调用** — 如果一个技能是另一个技能的数据提供者（如「寻技」为「灵匠」提供搜索数据），它应该：
    - 被子代理通过 `delegate_task` 调用，而不是由用户直接触发
    - 返回结构化 JSON 数据（不是显示文本），供主技能的程序化决策
    - 不含任何安装/执行/写入操作（只读）
    - 在 description 中注明自己的定位（"XX 的前置数据供应技能"），避免被错误触发

18. **当技能名与国际知名项目重名时，必须改名并注明灵感来源** — 如 Superpowers（与 obra/superpowers 重名）→ 神通，GStack（与 garrytan/gstack 重名）→ 通才。寻技搜索不仅要查本地/Hub/GitHub 是否有同名技能，还要查是否有知名外部项目同名。发现重名后：① 向冰哥报告冲突情况并提供改名选项 ② 在 SKILL.md 的 `metadata.source.inspired_by` 中记录灵感来源 ③ 不要使用可能引发混淆的名称

19. **新技能记得起中文名** — 冰哥的习惯是所有技能都要有中文名。在 title 和 description 中加入「又名」。风格参考：灵匠、寻技、美学工匠、设计百宝箱。如果 SKILL.md 正文中标题是英文，中文名写在括号里：`# skill-name（中文名）`。

20. **安全扫描可能产生误报（false positive）**

21. **rf-string / f-string 中嵌入 JS 代码的花括号转义** — 当技能使用 `rf'''...'''` 模板嵌入 JavaScript 时，所有 JS 的 `{` `}` 必须写为 `{{` `}}`。忘记转义会导致 Python 编译错误（`f-string: invalid syntax`）。常见错误模式：
    - `function(x) { return x.c; }` → 必须写 `function(x) {{ return x.c; }}`
    - `try { ... } catch(e) { ... }` → 必须写 `try {{ ... }} catch(e) {{ ... }}`
    - `if(cond) { ... }` → 必须写 `if(cond) {{ ... }}`
    - `{ upColor: '#22c55e' }` → 必须写 `{{ upColor: '#22c55e' }}`
    - **排查方法**：修改后运行 `py_compile.compile(file, doraise=True)` 验证 Python 语法。如果报 `f-string: invalid syntax`，说明有不匹配的花括号。
    - **最佳实践**：不要在 rf 模板中直接嵌入复杂 JS 逻辑。将新代码先写在单独的 .py 文件中调试，确认花括号正确后再迁移到模板中。或者改用 Python 字符串拼接/`.replace()` 来注入代码段，避免 rf 模板转义问题。

22. **模板脚本中重复声明变量导致整个 `<script>` 块静默失效** — 当在 rf 模板中新增 JS 变量声明时，检查该变量是否已在模板的其他位置声明过。`const`/`let` 不允许重复声明，重复声明会导致 **整个脚本块静默中止**（浏览器控制台无错误详情）。症状：`typeof D === "undefined"`、`typeof MARKETS === "undefined"` 但 HTML 结构正常。排查方法：
    - 浏览器控制台检查 `typeof D` 是否为 `"undefined"`
    - 搜索脚本中是否有重复的 `const VARNAME=` 或 `var VARNAME=`
    - 在生成 HTML 中 `grep "const VARNAME="` 确认只出现一次
    - 常见场景：重构面板生成代码时，模板顶部已有 `const MARKETS=...`，新代码中又写了 `var MARKETS=...`

23. **`execute_code` 中的复杂文件修改绕过 patch 工具的转义限制** — 当 `patch` 工具因 `Escape-drift detected` 错误失败时（常见于 JavaScript 代码中含 `\"` 转义符），改用 `execute_code` 中直接的文件字符串操作：

    ```python
    with open('target.py') as f:
        content = f.read()
    # 直接用 Python 字符串操作替换
    content = content.replace(old_string, new_string)
    with open('target.py', 'w') as f:
        f.write(content)
    ```

    这样绕过 patch 工具的自动转义检测，对 JS 代码中大量含引号的内容最可靠。 — `hermes skills install` 的自动安全扫描基于静态规则，对知名项目（如 obra/superpowers, 92.9K⭐, 166K 安装量）也可能误报 `CRITICAL exfiltration`。遇到 `BLOCKED` 时：
    - 先 inspect 触发告警的具体内容和位置（`hermes skills inspect <identifier>`）
    - 如果是知名项目且风险像是误报（如 echo 错误信息被当成数据外泄），向冰哥汇报后可用 `--force` 安装
    - 不要自动 `--force`，必须让冰哥决策
    - 常见误报模式：`echo "{\\\"error\\\": ...}"` 被误判为数据外泄、`.git/hooks/*.sample` 被误判为安全风险

24. **复杂多文件改动：写需求文档让 🚀 大莉执行** — 当面对跨多个文件、逻辑复杂的改动（如接入新 API provider、重构核心脚本），**不要自己直接动手改**。冰哥的偏好是：

    ```
    我（莉莉丝）→ 写详细的需求文档（/tmp/xxx_requirement.md）
                ↓
        让 🚀 大莉 加载技能后执行
                ↓
        大莉超时/只做了一部分？
                ↓
        我接手收尾 + git commit
    ```

    **操作步骤：**
    1. 先理清所有需要改动的文件和具体改动点
    2. 写一份完整的 `/tmp/xxx_requirement.md`（包含背景、每项改动的详细说明、注意事项）
    3. 用 `delegate_task(toolsets=['terminal','file','skills'])` 让大莉执行
    4. 大莉超时或被中断后，检查 `git status` 看完成了多少
    5. 接手收尾未完成的部分
    6. `git add + commit + tag` 打版本

    **为什么这样更好：**
    - 大莉（deepseek-v4-pro）编码能力比莉莉丝（deepseek-v4-flash）更强
    - 需求文档让大莉有清晰的执行路线图，减少试错
    - 冰哥明确说过：「你写需求让大莉来」
    - 大莉超时后莉莉丝接手收尾，形成「规划→执行→收尾」的流水线


---

## Verification Checklist

- [ ] Step 0 已执行：通过 `delegate_task` 调用寻技搜索过现有技能，返回了 JSON 数据
- [ ] 如搜索到相近技能，已走安全审查流程并得到冰哥确认
- [ ] 写之前已执行安全检查（5 维度：来源/代码/依赖/许可/原则无意外）
- [ ] 修改后已重新快速审查修改部分
- [ ] SKILL.md 以 `---` 开头（字节 0）
- [ ] YAML 前端包含 `name`、`description`、`version`、`author`、`license`、`metadata.hermes.{tags, related_skills}`
- [ ] name 小写+连音符、≤64 字符
- [ ] description ≤1024 字符
- [ ] SKILL.md 总长 ≤100,000 字符（目标 8k-15k）
- [ ] 没有残留的 Claude Code 专有命令（`claude -p`、`.claude/commands/` 等）
- [ ] 所有工具引用使用了 Hermes Agent 的 API（`skill_manage`、`delegate_task`、`write_file`、`patch`、`read_file`、`search_files`、`skills_list`、`skill_view`）
- [ ] evals/evals.json 格式正确
- [ ] 脚本文件（scripts/）可以直接运行（`python script.py ...`）
- [ ] agents/ 目录中的子代理指令是自包含的
- [ ] 新技能在新会话中可被 `skill_view(name='<skill-name>')` 读取
- [ ] 工作流包含提示使用 `delegate_task` 并行的说明
- [ ] 包含对 baseline 对比（with/without skill）的支持
- [ ] 包含迭代循环的终止条件说明

---

## 版本管理（Git）

本技能使用 Git 进行版本管理。仓库位于技能目录内：

```bash
cd ~/.hermes/skills/productivity/hermes-skill-creator

# 查看版本历史
git log --oneline --decorate

# 查看当前版本标签
git tag -l

# 创建一个新版本（同时更新 SKILL.md 中的 version 字段）
git add -A
git commit -m "feat: 灵匠 vX.Y.Z — 更新说明"
git tag -a vX.Y.Z -m "灵匠 vX.Y.Z — 更新说明"
```

### 版本号规范（冰哥规则）

| 操作 | 版本变化 | 示例 |
|------|---------|------|
| 初始 | `0.1.0` | — |
| 新增功能 | 次版本 +0.1 | `0.1.0` → `0.2.0` |
| 内部修改 / Bug 修复 | 修订号 +0.0.1 | `0.3.0` → `0.3.1` |
| 次版本满 10 | 自然进位，不走大版本 | `0.9.0` → `0.10.0` → `0.11.0` |
| 大版本更新 | **必须先问冰哥** | 他说"不生"就继续走 `0.11.0` → `0.12.0` |

**当前版本历史：**
| 版本 | 说明 |
|------|------|
| v0.1.0 | 初始版本 |
| v0.2.0 | 新增 Step 0 + 复用流程 |
| v0.3.0 | 扩大搜索范围到 GitHub 等多平台 |
| v0.3.1 | Step 0 改为调用寻技（内部重构） |
| v0.4.0 | 新增通用安全检查节 |
| v0.5.0 | Step 0 改为 delegate_task 调用寻技子代理 |
| v0.12.0 | 2026-05-20 | 🚀 新增 pitfall #24（复杂多文件改动：写需求让大莉执行）。📝 iMessage 技能新增 +86 中国号码故障排查指南。 |
| v0.10.0 | 2026-05-19 | 新增「灵感来源记录」规范（inspired_by vs adapted_from 区分）；新增名称冲突 pitfall #18（重名国际项目处理流程）；强化 Step 0 用户偏好检查环节。 |
| v0.8.0 | 2026-05-19 | 新增灵感来源记录（inspired_by）字段规范；修复重复 pitfall 编号；新增名称冲突 pitfall #18（当技能名与国际知名项目重名时的处理流程） |

### 更新上游后提交

```bash
cd ~/.hermes/skills/productivity/hermes-skill-creator
python scripts/check_upstream_updates.py --update  # 更新 metadata
git add SKILL.md
git commit -m "sync: 同步上游更新至 commit <sha>"
git tag -a v0.3.1 -m "灵匠 v0.3.1 — 同步上游更新"

注：上游同步属于内部修改，修订号 +0.0.1。如果同时也改了功能，则算新增功能 +0.1。
```

---

## 上游更新检查（Upstream Updates）

本技能适配自 [`anthropics/skills/skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator)。上游仓库可能会持续更新，你可以通过以下方式来同步更新：

### 手动检查

```bash
cd ~/.hermes/skills/productivity/hermes-skill-creator
python scripts/check_upstream_updates.py
```

脚本会：
1. 从 GitHub API 获取上游最新 commit
2. 对比记录的 commit SHA 和文件哈希
3. 输出差异摘要（新增/修改/删除的节）
4. 返回更新建议

### 何时检查

- 定期维护时（建议每月一次）
- 发现 Claude Code 版 `skill-creator` 有大版本更新时
- 手动触发：`python scripts/check_upstream_updates.py --diff`（输出详细差异）

### 如何同步

1. 运行检查脚本了解差异范围
2. 阅读上游更新的 commit message 和 diff
3. 判断哪些改动可以/应该移植到 Hermes 适配版
4. 手动移植相关改动（注意：Claude Code 专有的 CLI 调用需要映射为 Hermes Agent 工具调用）
5. 更新 `metadata.source.commit` 和 `metadata.source.file_hash`

---

## 与原始 skill-creator 的差异

详见 `references/workflow-comparison.md`。

关键差异：
- **Claude Code CLI → Hermes Agent Tools**：所有 `claude -p` 变为 `delegate_task`
- **Claude 技能发现 → skill_manage API**：不再依赖 `.claude/commands/`
- **浏览器 viewer → 静态 HTML**：无头环境使用 `--static` 生成文件
- **`run_loop.py` 自动优化 → 人工+LLM 迭代**：由于没有 `claude -p` 子进程，描述优化改为人工引导
- **`.skill` 打包 → 目录结构**：Hermes Agent 技能是目录结构，不需要 zip 打包
