# 智能模型选择器 — model_selector.py

**路径**: `~/.hermes/scripts/model_selector.py`
**创建时间**: 2026-05-26
**来源**: 借鉴 model-router (open-world-project/model-router) 设计思路

## 用途

消费 NV Ping 系统输出的 `ranking.json` 数据，添加智能路由逻辑，输出推荐模型。

## 核心功能

| 功能 | 说明 |
|:----|:------|
| Fast-path 极短 ACK | 检测"好的"、"ok"等短回复 → 走 mimi 最轻量模型，跳过完整判定 |
| 轻量分类指导 | 支持 `--category mimi/light/deep/vision` 手动指定分类 |
| Session 状态管理 | 按 session_id 追踪：当前模型、分类、错误次数、升级等级 |
| Pin/Unpin 固定 | `--pin mimi` 固定 session 到指定分类，`--unpin` 恢复动态 |
| 自动升级 Escalation | 连续 2 次报告失败 → 自动升一级（light→deep） |
| Provider 健康过滤 | 跳过连续失败 >= 3 次的 provider |
| 降级兜底 | 目标分类无可用模型时自动降级到下一个分类，最后兜底 LongCat-2.0-Preview |

## CLI 用法

```bash
# 推荐模型
python3 model_selector.py --task "写一段代码" --session my-session

# 指定分类
python3 model_selector.py --task "分析性能" --category deep --session my-session

# Pin/Unpin
python3 model_selector.py --pin mimi --session my-session
python3 model_selector.py --unpin --session my-session

# 报告失败（触发 escalation）
python3 model_selector.py --report-failure --session my-session

# 查看 session 状态
python3 model_selector.py --status --session my-session
```

## 输出格式

```json
{
  "model": "meta/llama-3.2-1b-instruct",
  "provider": "nv",
  "category": "mimi",
  "reason": "✅ mimi → nv/meta/llama-3.2-1b-instruct",
  "fast_path": true,
  "escalated": false,
  "pinned": false,
  "session_id": "test-session"
}
```

## 数据源

- `~/.hermes/data/NVping/tmp/ranking.json` — Ping 排名数据（categories + health）
- `~/.hermes/data/model_selector_state.json` — Session 状态持久化

## 与闪莉的关系

闪莉的 Kanban 选模逻辑未来可以调用此脚本：
- 获取推荐模型和 provider
- 根据推荐结果设置 delegate_task 的 model 参数
- 通过 `--report-failure` 反馈结果实现自动升降级

## 添加自定义 Provider 到选择器

当新增一个 provider（如 Xiaomi MiMo）时，需要在 `model_selector.py` 中做两处修改：

### 1. 添加 Provider 优先级

在 `get_best_model()` 函数的 `priority` 字典中，按期望的优先级顺序添加：

```python
# 优先级值越小越优先
priority = {"xiaomi": 0, "nv": 1, "longcat": 2, "google": 3, "openrouter": 4}
```

### 2. 添加静态 Fallback 模型池

MiMo 等不在 ranking.json（NV Ping 数据）中的 provider，需要定义静态 fallback 池：

```python
MIMO_FALLBACK_POOL = {
    "mimi":   [{"id": "mimo-v2.5",      "provider": "xiaomi"}],
    "light":  [{"id": "mimo-v2.5",      "provider": "xiaomi"},
               {"id": "mimo-v2-omni",   "provider": "xiaomi"}],
    "deep":   [{"id": "mimo-v2.5-pro",  "provider": "xiaomi"},
               {"id": "mimo-v2.5",      "provider": "xiaomi"}],
    "vision": [{"id": "mimo-v2-omni",   "provider": "xiaomi"},
               {"id": "mimo-v2.5-pro",  "provider": "xiaomi"}],
}
```

### 3. MiMo Fallback 始终前置

修改 `get_best_model()`，将 MiMo fallback 模型始终追加到候选列表最前面：

```python
# 始终将 MiMo fallback 模型加入候选（前置，优先级最高）
mimo_fb = get_mimo_fallback(category)
if mimo_fb:
    available = mimo_fb + available
```

这样 MiMo 会出现在候选列表最前面，按优先级排序后优先被选中（xiaomi=0 最高）。

## 可借鉴的设计（来自 model-router）

1. **轻量分类器**：用便宜的 Flash 模型做 triage，判断任务复杂度
2. **Fast-path 启发式**：正则匹配极短 ACK，不调 classifier
3. **Session 状态字典**：thread-safe 的 session 级状态管理
4. **Mid-loop escalation**：工具调用失败后自动升级 tier
5. **.bak 时间戳备份**：修改文件前创建时间戳备份
