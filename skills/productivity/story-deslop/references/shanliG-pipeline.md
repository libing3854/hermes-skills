# shanliG Multi-Stage Refinement Pipeline

> 闪莉原版 → Gemini精修 → Python脚本高频词兜底

## 问题背景

闪莉（mimo-v2.5-pro）写作的章节质量高但有高频词残留（像、一种、微微、缓缓等）。
Gemini 3.5 Flash 精修禁用词效果好，但无法控制"一种"（单章可达15次）。
需要多阶段处理。

## 流程

### Stage 1: Gemini 精修
- 脚本：`/Users/libing/Desktop/临时文件-0001/脑洞文/shanliG_refine.py`
- 模型：gemini-3.5-flash @ localhost:8081
- 提示词核心：禁用词0次 + 高频词上限 + 保留原文剧情
- 温度：0.3（低温度减少随机性）

### Stage 2: Gemini 加强轮（可选）
- 脚本：`/Users/libing/Desktop/临时文件-0001/脑洞文/shanliG_round2.py`
- 将"一种"加入禁用词列表，重跑 Stage 1 失败的章节
- 温度：0.2（更低）

### Stage 3: Python 脚本高频词兜底
- 使用 `delegate_task` 派子agent
- 读取每章上下文，对超出上限的"一种"做语义感知替换
- 替换策略：
  - "一种+独立名词" → 删除"一种"
  - "一种+修饰短语" → 删除"一种"保留修饰
  - 力度场景 → "一股"替代

## 输出目录

精修后文件保存在 `正文_geminified/` 子目录，不直接覆盖原文件。
用户确认后手动复制到 `正文/`。

## Hermes Profile

`~/.hermes/profiles/shanliG/config.yaml`:
```yaml
model:
  provider: gemini-local
  default: gemini-3.5-flash
providers:
  gemini-local:
    name: Gemini Local
    api_key: none
    api_mode: chat_completions
    base_url: http://localhost:8081/v1
    context_length: 1048576
    default_model: gemini-3.5-flash
```

## 实测数据（291-298章，8章）

| 章节 | 闪莉原版 | Gemini第一轮 | Gemini第二轮 | 脚本兜底 |
|------|---------|------------|------------|---------|
| 291  | 一种×5 微微×5 缓缓×6 | 全清 | — | — |
| 292  | 一种×8 微微×4 缓缓×5 | 一种×7 | 一种×7 | →3 ✓ |
| 293  | 像×11 一种×4 | 像×13 一种×6 | 像×11 | →10 ✓ |
| 294  | 如同×4 一种×6 微微×5 | 如同×4 | 如同×4 | →3 ✓ |
| 295  | 如同×4 一种×9 | 仿佛×3(!) 一种×12 | 如同×4 一种×6 | →3 ✓ |
| 296  | 一种×14 | API失败 | 一种×12 | →3 ✓ |
| 297  | 一种×14 | 一种×15 | 一种×6 | →3 ✓ |
| 298  | 深吸×1 不由得×1 一种×17 | 一种×13 | 一种×15 | →3 ✓ |

**关键发现**：
- Gemini 第一轮对禁用词（仿佛/深吸一口气/不由得）清理效果好
- Gemini 第二轮对"一种"有改善但无法清到3次以内
- 第295章 Gemini 翻车：精修后引入3处"仿佛"禁用词
- 第296章 Gemini API 返回错误（模型拒绝处理长文本）
- Python脚本兜底是最终保障
