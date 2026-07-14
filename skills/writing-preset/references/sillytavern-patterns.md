# SillyTavern 提示词系统借鉴点

来源：easychen/intro-to-silly-tavern-prompts (GitHub) + SillyTavern 官方文档

## 核心机制

SillyTavern 的提示词系统由4部分组成：角色卡 + 世界信息 + 系统设置 + 对话历史。

### 可借鉴的模式

| 模式 | SillyTavern 实现 | 我们的实现 |
|------|-----------------|-----------|
| 角色卡 | 示范对话段落（至少3段） | character-dialogue-template |
| 创作者笔记 | 每N条消息自动插入指导语 | writing-guardrails（手动检查清单） |
| 动态世界信息 | 关键词触发自动加载 | context-trigger（细纲标注） |
| 预设模板 | 上下文模板+指令模板+采样器 | writing-preset（看板任务body模板） |

### 不能直接复制的机制

1. **自动注入/触发** — Hermes skill系统不支持链式调用或自动触发，必须手动嵌入
2. **采样器参数** — temperature/creativity等模型参数无法通过skill控制
3. **JSON配置文件** — 无法被执行，改为Markdown模板

### 设计原则

从 SillyTavern 借鉴时，必须将"自动化幻想"落地为"检查清单+模板"形态：
- ❌ "自动注入" → ✅ "嵌入任务body作为检查项"
- ❌ "连锁调用" → ✅ "手动依次加载"
- ❌ "自动触发" → ✅ "细纲中标注"

## 详细文档

- 提示词系统分析：https://github.com/easychen/intro-to-silly-tavern-prompts
- 官方文档：https://docs.sillytavern.app/usage/prompts/
- Sphiratrioth预设：https://huggingface.co/sphiratrioth666/SillyTavern-Presets-Sphiratrioth
