# 子代理渲染HTML看板的坑与解决方案

## 背景

在本会话中尝试用 delegate_task 子代理生成/修改大型 HTML 看板文件（180KB+），多次超时失败。

## 问题

| 尝试 | 结果 | 原因 |
|------|------|------|
| delegate_task 完整生成200KB+ HTML | 超时（600s） | 数据量太大（44标地×双K线≈200KB），子代理处理不完 |
| delegate_task 设计师修改样式 | 超时（600s） | 读完整文件（180KB）+ 重写，超过超时限制 |
| delegate_task 设计师仅改CSS | ❌ 同样超时 | 虽然任务简单，但文件太大传输就花了很久 |

## 解决方案

1. **不要用子代理处理大型 HTML 文件** — 超过 50KB 的文件直接在当前会话中 patch
2. **patch 优先于 regenerate** — 用 `patch` 工具只修改特定 CSS/JS 行，不重写整个文件
3. **Python 生成 HTML 最可靠** — 数据在 Python 端处理好，HTML 模板用 f-string 生成，不用子代理碰数据
4. **如果要改样式 → 直接 patch CSS** — 找到对应的 CSS 选择器，用 `patch(new_string, old_string)` 替换
5. **如果要改 JS → 单行 patch** — 不要替换大段代码，找到具体行精确匹配

## 推荐工作流

```bash
# 1. Python 生成 → 一次性输出完整 HTML
python3 gen_finance_board.py

# 2. 调试/修改 → 在当前会话中直接 patch 生成的 HTML
patch(
  path="...html",
  old_string=".cd { padding: 10px; }",
  new_string=".cd { padding: 24px 20px; }"
)

# 3. 大规模重构 → 改 Python 生成脚本后重新生成
# 不要在子代理中操作 200KB 文件
```
