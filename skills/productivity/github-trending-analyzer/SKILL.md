---
name: github-trending-analyzer
description: GitHub 收藏分析 + Trending 推荐 — 分析用户 GitHub stars 总结技术偏好，从 Trending 页面筛选推荐同类型热门项目
tags: [github, trending, stars, recommendation, analysis]
---

# 🌟 GitHub Trending 项目推荐器

分析用户的 GitHub 收藏项目以总结其技术偏好，并根据偏好在 GitHub Trending 页面搜索并筛选指定数量的当天热门同类型项目。

## 使用场景

当需要从 GitHub Trending 中挖掘符合个人技术口味的项目时使用。典型场景：
- 每天刷 Trending 但不想看全部，只想看和自己收藏风格匹配的项目
- 想发现和已收藏项目类似的新热门项目
- 技术选型调研，找同领域热门方案

## 工作流

### 第一步：分析用户偏好
无法访问 GitHub Auth？别慌，两颗Fallback方案：
1. 直接获取用户 Profile 页面的 public starred repos（无需登录即可查看公开收藏数）
2. 根据已可见的 Profile 页面内容来推断用户的技术偏好

**关键教训**：有些用户（特别是 CI 系统/企业用户）可能只收藏了很少甚至 0 个 repos，此时直接基于 Trending 页面共性趋势生成报告即可。不要中断流程。

### 第二步：采集 Trending 项目
**推荐**：直接用浏览器 JS 抓取 Trending 页面，效果最好、最可靠。
```javascript
// 在 browser_console 中执行，一次性提取所有项目
JSON.stringify(Array.from(document.querySelectorAll("article")).map(a => {
  const h2 = a.querySelector("h2 a");
  const desc = a.querySelector("p");
  const lang = a.querySelector('[itemprop="programmingLanguage"]');
  const allLinks = Array.from(a.querySelectorAll("a"));
  const starsLink = allLinks.find(l => l.href && l.href.includes("/stargazers"));
  const allText = a.textContent;
  const weeklyMatch = allText.match(/([\d,]+) stars this week/);
  return {
    name: h2 ? h2.textContent.trim().replace(/\s+/g, "") : "",
    desc: desc ? desc.textContent.trim() : "",
    lang: lang ? lang.textContent.trim() : "",
    stars: starsLink ? starsLink.textContent.trim() : "",
    weeklyStars: weeklyMatch ? weeklyMatch[1] : ""
  };
}), null, 2)
```

**日期范围**：默认 `?since=weekly`（周报），也可用 `?since=daily`（日报）。

### 第三步：匹配筛选
基于 Trending 数据和用户的收藏偏好（或无偏好时的通用热点），选出相关度最高的前 N 个。

**通用偏好关键词映射**（当用户收藏数据不足时使用）：
| 类别 | 权重 | 说明 |
|------|------|------|
| AI / Agent | ⭐⭐⭐⭐⭐ | 年度最大趋势 |
| LLM + RAG | ⭐⭐⭐⭐ | 基础设施层 |
| MCP / Tools | ⭐⭐⭐⭐ | 平台生态 |
| Design / UI | ⭐⭐⭐ | 前端友好 |
| DevOps / Security | ⭐⭐⭐ | 实用工具 |
| Multimedia (Voice/Video/GUI) | ⭐⭐⭐ | 创作民主化 |

### 第四步：生成推荐报告
报告必须包含：
1. **本周Top 3** — 用表格展示前三甲
2. **trending 分类** — 按关键词分组（AI/Agent, Privacy, Tools...）
3. **语言分布统计** — 柱状/列表形式
4. **莉莉丝推荐语** — 2-3 段个性化分析

### 第五步：保存 & 发送
- HTML 保存到桌面（`~/Desktop/github-trending-weekly.html`）
- 发送到 Discord（如已配置）；保存本地即算任务完成

**关键**：即使 Discord 发送失败，本地 HTML 必须是可用交付物。不要因为一步失败就放弃整个任务。

## 工具选择指南

| 场景 | 推荐工具 | 为什么 |
|------|----------|--------|
| 抓取 Trending 列表 | `browser_console` + JS | 干净结构化，无需 HTML 解析 |
| 在 cron 模式下无法用 `execute_code` | 直接调 `browser_console` | execute_code 在 cron 模式被 BLOCKED |
| 用户 Profile 页面需要动态加载 | `browser_navigate` → `browser_console` | 含 JS 的页面无法用 curl |
| 发送 Discord 消息 | `send_message` 工具 / Discord Webhook | 视配置而定 |

## 参考文件

- `references/workflow.md` — 详细的工作流步骤说明
- `references/trending-html-parsing.md` — JS 提取脚本示例（推荐方案）
- `references/search-api-trending.md` — GitHub REST API 备选方案
- `references/cron-mode-lessons.md` — Cron 模式运行教训（execute_code 被阻塞、低收藏用户 fallback、Discord 失败容错）

## 版本历史

- v1.1.0 — 2026-06-28: 大幅更新！添加 cron 模式工具选择指南、低收藏用户 Fallback、JS 提取脚本示例、Discord 发送失败容错、趋势关键词映射表。
