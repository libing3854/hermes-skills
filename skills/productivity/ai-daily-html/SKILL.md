---
name: ai-daily-html
description: AI 日报 HTML 生成器 — 从 6 个 AI 资讯源采集数据，渲染成赛博朋克复古未来主义风格的 HTML 日报页面
tags: [html, design, ai-news, daily-report, cyberpunk]
---

# 🌟 AI 日报 HTML 生成器

将 AI 日报内容渲染为视觉惊艳的赛博朋克复古未来主义风格 HTML 页面。

## 使用场景

当需要生成一份视觉化 AI 日报时使用。典型的调用链：
1. 从 6 个资讯源采集数据（juya-ai-daily、news.smol.ai、ai.hubtoday.app、Decohack、GitHub Trending、HuggingFace Papers）
2. 整理结构化日报内容
3. 用本技能渲染为 HTML

## 输出路径

生成的 HTML 日报文件默认存放在 **`~/Desktop/ai日报/`** 目录下。

## 模板文件

本技能提供 CSS/HTML 模板，位于 `references/template.html`。

### 设计特征

| 要素 | 内容 |
|------|------|
| 🎨 风格 | 赛博朋克复古未来主义 (Cyberpunk Retro-Futurism) |
| 🌑 主背景 | `#080c12` 深空黑 + 三层径向渐变辉光 |
| 🟠 主色调 | 电光橙 `#ff5722`、电光青 `#00e5ff` |
| 🔤 字体 | Orbitron（标题）+ Space Grotesk（正文）+ Noto Sans SC（中文） |
| ✨ 动效 | 9 区入场动画、卡片悬停发光、扫描线/噪点纹理 |
| 📱 响应式 | 移动端/平板/桌面全适配 |

### 页面结构（9 大板块）

```
┌─ 头部 — 终端徽章 + 标题 + 闪烁光标 ─────────────┐
├─ 🔥 今日头条 — 5 条大事，BREAKING 标签，热度点阵 ─┤
├─ 🧠 AI 模型与平台 — 左右双栏卡片区 ──────────────┤
├─ 🚀 Product Hunt 精选 — 排名表格，前三金银铜 ────┤
├─ 📄 前沿论文 — 5 卡片，大号索引数字水印 ─────────┤
├─ 💻 GitHub Trending — 星标 + 进度条动画 ─────────┤
├─ 📰 行业动态 — 时间线 + 发光节点 ────────────────┤
├─ 📊 今日关键词 — 标签云，featured/hot 分类 ──────┤
└─ 👣 页脚 — 终端风格结束语 ────────────────────────┘
```

## 使用方法

### 方式一：直接使用模板

1. 复制 `references/template.html` 到目标目录
2. 替换模板中的日报数据（标记为 `<!-- DATA -->` 的区域）
3. 更新标题日期
4. 在浏览器中打开

### 方式二：在技能中引用

在 SKILL.md 或其他技能中引用本技能时，加载模板文件并使用其中的设计系统。

## 数据源

| # | 站点 | 类型 |
|:-:|------|------|
| 1 | juya-ai-daily | AI 资讯日报 |
| 2 | news.smol.ai | AI 新闻聚合 |
| 3 | ai.hubtoday.app | AI 资讯平台 |
| 4 | Decohack / Product Hunt | AI 产品发布 |
| 5 | GitHub Trending | AI 开源项目 |
| 6 | HuggingFace Papers | AI 论文 |

## 版本历史

- v1.0.0 — 初始版本：赛博朋克风格 AI 日报 HTML 模板
