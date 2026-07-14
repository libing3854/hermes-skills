# references/delegate-task-workarounds.md

> 记录 delegate_task 调用中的已知问题和 workaround
> 更新：2026-05-27

## 问题：deepseek-v4-pro 模型名报 Unsupported model

**现象**：delegate_task 中使用 `{"model": "deepseek-v4-pro", "provider": "deepseek"}` 报 400 错误。

**根因链条（2026-05-27 完整复盘）：**

1. **浅层原因**：delegation config 的 base_url/key_env 指向错误的目标
   - 第一次修复：把 base_url 指向 ChatAnywhere → 还是报错
   - 第二次修复：改回 DeepSeek 官方 API → 但缺失 `providers:` 注册

2. **深层根因**：`deepseek` 只在 `model:` 段有定义，不在 `providers:` 下注册
   ```yaml
   # config.yaml 中的问题结构
   model:                          # 主模型配置
     provider: deepseek            # 只在主模型路由时生效
     base_url: https://api.deepseek.com
   providers:
     longcat: ...                  # ✅ 有
     omlx: ...                     # ✅ 有
     deepseek: ???                 # ❌ 没有！delegate_task 找不到它
   ```
   - 当主模型是 `deepseek-v4-flash` 时：Hermes 复用主模型的 provider 配置，能读到 base_url 和 key，delegate_task 正常工作
   - 当主模型是 `LongCat` 时：delegate_task 去 `providers:` 找 deepseek → 找不到 → 报 Unsupported model

3. **最终修复**（2026-05-27）：
   ```yaml
   providers:
     deepseek:
       name: DeepSeek
       base_url: https://api.deepseek.com
       key_env: DEEPSEEK_API_KEY
       api_mode: chat_completions
       default_model: deepseek-v4-flash
   ```
   在 `providers:` 下添加 deepseek 条目，明确指定 `key_env` 从 `.env` 读取。

## 已知局限（即使修复后）

**`deepseek-v4-pro` 的 delegate_task 在 LongCat 主模型下仍然可能失败。** 经测试：
- ✅ `curl` 直接调用 DeepSeek 官方 API → 模型存在且正常返回
- ✅ 主模型为 `deepseek-v4-flash` 时 → delegate_task 正常
- ❌ 主模型为 `LongCat` 时 → delegate_task 仍然报 Unsupported model
- ❌ 原因不明，可能涉及 Hermes 的模型名解析/缓存机制

**workaround（两种方案）：**

**方案 A（推荐）：delegate_dalim() 切换模型（2026-06-05 实战验证有效）**
```python
delegate_dalim()  # 切换到大莉M（mimo-v2.5-pro）
delegate_task(tasks=[{
    "goal": "深度审核...",
    "context": "...",
    "toolsets": ["terminal", "file"]
}])
delegate_restore()  # 恢复默认模型
```
- 优点：不需要冰哥手动切主模型，流程更流畅
- delegate_dalim() 会切换当前会话模型到 mimo-v2.5-pro，delegate_task 使用切换后的模型
- 已在第三卷第八批（114-120章）审核中验证有效

**方案 B（备选）：让冰哥切主模型到 deepseek**
- 需要调大莉时，让冰哥先切到 deepseek-v4-flash 主模型
- 或者直接让基座模型自己完成（大莉不可用时的手册策略）

## 冰哥偏好

- 审核大纲/重任务 → 优先派大莉（deepseek-v4-pro）
- 不要在 delegate_task 上反复重试浪费时间（连续2次失败就切换方案）
- 切换方案：先试 delegate_dalim()，失败则让冰哥切主模型到 deepseek，或由基座直接完成并标注"未经交叉审核"

## 验证命令

```bash
# 检查 DeepSeek 官方 API 支持的模型
source ~/.hermes/.env 2>/dev/null
curl -s "https://api.deepseek.com/models" \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY"
# → 应返回 deepseek-v4-flash 和 deepseek-v4-pro

# 检查 config.yaml 中 deepseek 是否在 providers: 下注册
grep -A 5 "^  deepseek:" ~/.hermes/config.yaml
# → 应显示 name/base_url/key_env 等字段
```

## 详细章级大纲创建流程（2026-05 实践）

当需要为整卷写详细章级大纲时：

1. **创建大纲文件**：`大纲_第X卷_详细章级大纲.md`
   - 每章包含：核心事件、情绪目标、章首/章尾钩子、伏笔（标明回收章节）、字数目标（5000-6000字）、角色变化
   - 卷首包含：卷级主题、情绪弧线、核心设定回顾、团队/城市状态

2. **创建追踪文件**（同时创建）：
   - `追踪_第X卷_伏笔.md`：所有伏笔的状态表（活跃/已回收/跨卷）
   - `追踪_第X卷_角色状态.md`：每个角色的最新状态快照 + 关键变化记录
   - `追踪_第X卷_时间线.md`：详细到相对日期的事件时序

3. **审核流程**：
   - 详见 `references/outline-quality-review.md`
   - 优先派大莉审核（注意主模型必须是 deepseek，否则 delegate_task 不可用）
   - 按 P0→P1→P2→P3 修复
   - 二次审核后定稿
