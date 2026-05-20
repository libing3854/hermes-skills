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
分析用户的 GitHub Starred 项目，归类总结技术偏好关键词。

### 第二步：采集 Trending 项目
访问 GitHub Trending 页面（https://github.com/trending），提取当天热门项目列表。

### 第三步：匹配筛选
根据技术偏好关键词对 Trending 项目进行匹配筛选，选出最相关的前 N 个。

### 第四步：生成推荐报告
整理匹配到的项目，包含项目名称、描述、匹配原因。

## 参考文件

- `references/workflow.md` — 详细的工作流步骤说明

## 版本历史

- v1.0.0 — 初始版本：GitHub 收藏分析 + Trending 推荐
