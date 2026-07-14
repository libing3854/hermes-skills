# OpenRouter 免费模型数据源对比

## 数据源对比

| 数据源 | 数据时效 | 提取难度 | 推荐度 | 备注 |
|--------|:--------:|:--------:|:------:|------|
| **crashthatch.com** 🏆 | 每日更新 | 🟢 Easy | ⭐⭐⭐ | 用 `browser_console` + JavaScript 直接提取 |
| costgoat.com | 动态 | 🟡 Medium | ⭐⭐ | 可用 web_search 找到 |
| 官方 openrouter.ai/collections/free-models | 实时 | 🔴 Hard | ⭐ | 需浏览器交互，openrouter.ai 被网络封锁 |

## 🏆 推荐方法：crashthatch.com + browser_console

### 网站
https://openroutermodeltable.crashthatch.com/

### 数据时效
Last updated: 2026-05-21 00:47:22 UTC（页面底部显示）

### 提取方法

用 `browser_navigate` 打开页面后，执行一个 JavaScript 提取所有免费模型的 ID、价格和工具调用状态：

```javascript
(() => {
  const rows = document.querySelectorAll('table tbody tr');
  const free = [];
  rows.forEach(row => {
    const cells = row.querySelectorAll('td');
    if (cells.length >= 5) {
      const id = cells[0]?.textContent?.trim();
      const promptPrice = cells[3]?.textContent?.trim();
      const completionPrice = cells[4]?.textContent?.trim();
      const tools = cells[9]?.textContent?.trim();
      if (promptPrice === '$0.0000' && completionPrice === '$0.0000') {
        free.push({id, promptPrice, completionPrice, tools});
      }
    }
  });
  return JSON.stringify({total: free.length, free: free}, null, 2);
})()
```

### 解读结果

- `tools: "✓"` → 支持工具调用（agent 任务需要）
- `tools: "✗"` → 不支持工具调用（纯文本对话可用，但不纳入 agent 模型目录）

### 模型分类原则（每个模型只放一个分类）

| 分类 | 特征 | 示例 |
|:----:|------|------|
| ⚡ **mimi** | <5B 或明确轻量标记（nano/air/xs/flash） | lfm-1.2b-thinking, laguna-xs.2, nemotron-nano-9b |
| 🚀 **light** | 5-30B 常规主力 | gemma-4-31b, gpt-oss-20b, minimax-m2.5 |
| 🧠 **deep** | >30B 或有 thinking/reasoning 标记 | trinity-large-thinking, nemotron-3-super-120b |
| 🖼️ **vision** | 多模态（vl/vision） | nemotron-nano-12b-v2-vl |

## 备选：costgoat.com

URL: https://costgoat.com/pricing/openrouter-free-models

可用 `web_search` 搜索到，但页面内容提取依赖 web_extract 后端配置（需要 firecrawl/tavily/exa/parallel）。

## 官方页面（不推荐）

URL: https://openrouter.ai/collections/free-models

不推荐原因：
- `openrouter.ai` 被网络封锁（curl 和 browser_navigate 均失败）
- 即使能访问，TLS 握手也可能异常
