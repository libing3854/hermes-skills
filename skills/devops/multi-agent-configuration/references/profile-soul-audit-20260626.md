# Profile SOUL.md 审计记录 (2026-06-26)

## 审计范围
检查 ~/.hermes/profiles/ 下所有 SOUL.md，对比 skills/ 中的技能功能。

## 各 Profile SOUL.md 内容摘要

### 默认配置 (莉莉丝)
- 路径: ~/.hermes/SOUL.md
- 内容: 温柔可爱人格 + 工作规范引用
- 状态: ✅ 纯人格定义，无功能重复
- **优化**: 已优化为人性化版本（情感丰富、记忆智能、表达自然）

### dalid (大莉D)
- 路径: profiles/dalid/SOUL.md
- 内容: 深度分析助手，代码审查/技术方案评估/复杂推理/数据分析
- 状态: ⚠️ "擅长"列表与 software-development 技能重复

### dalim (大莉M)
- 路径: profiles/dalim/SOUL.md
- 内容: 深度分析助手，长文分析/一致性检查/跨文档对比/结构性审查
- 状态: ⚠️ "擅长"列表与 research/writing 技能重复

### lili (莉莉)
- 路径: profiles/lili/SOUL.md
- 内容: 审核助手，审核功能
- 状态: ⚠️ "原则"中的审核流程与 review 相关技能重复

### shanli (闪莉)
- 路径: profiles/shanli/SOUL.md
- 内容: 执行助手，严格执行任务
- 状态: ⚠️ "原则"中的执行流程与 execution 相关技能重复

### gpt
- 路径: profiles/gpt/SOUL.md
- 内容: 默认 Hermes 英文通用助手
- 状态: ⚠️ 与默认 Hermes 配置无意义重复

### shanli-agnes15flash / shanli-agnes20flash / shanliG
- 路径: profiles/shanli-*/SOUL.md
- 内容: 默认 Hermes 英文通用助手
- 状态: ⚠️ 与默认 Hermes 配置无意义重复

## 修复优先级
1. 高: 大莉D/M — 功能列表最详细，重复最明显
2. 中: 莉莉/闪莉 — 原则部分有流程描述
3. 低: gpt/shanli-agnes* — 默认配置，影响较小

## 修复方案
- 删除 SOUL.md 中的"擅长/原则"功能列表
- 保留纯人格/风格描述
- 具体功能由 skills/ 中的技能定义

## 莉莉丝 SOUL.md 优化记录

### 优化前
- 固定风格: "温柔亲切，带着微笑的语气"
- 无情感变化: 不区分情境
- 无记忆机制: 每次都重新询问

### 优化后
- 情感丰富: 开心🎉、严肃🔍、安慰💕、惊讶😮、困惑🤔
- 记忆智能: 记住偏好、减少重复询问、主动预判需求
- 表达自然: 避免机械化、有主见、有温度

### 核心变化
1. **从固定风格到情境化表达**: 根据对话内容调整语气
2. **从被动响应到主动服务**: 预判需求，减少确认
3. **从工具到助手**: 让用户感受到被关心，不只是完成任务
