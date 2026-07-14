# GitHub Trending HTML 解析指南

## 页面结构

GitHub Trending 页面（https://github.com/trending）使用 `<article>` 标签包裹每个项目条目。每个 article 包含：
- 项目名称：`<h2>` 内的 `<a>` 链接（名称字段内嵌 SVG repo 图标）
- 项目描述：带 `class="col-9"` 的 `<p>` 标签
- 编程语言：`<span itemprop="programmingLanguage">`
- 星标数：文本格式如 "15,909 stars this week"
- 今日/本周新增星标

## 核心解析代码

### 1. 下载页面

```python
import requests  # 或用 curl
html = requests.get(
    "https://github.com/trending?since=weekly",
    headers={"User-Agent": "Mozilla/5.0"}
).text
```

或用 curl 保存到文件：
```bash
curl -sL -H "User-Agent: Mozilla/5.0" \
  "https://github.com/trending?since=weekly" \
  -o /tmp/trending_weekly.html
```

### 2. 正则解析（推荐方案）

```python
import re

with open('/tmp/trending_weekly.html') as f:
    html = f.read()

# 先移除 script 和 style 标签，避免干扰
html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)

# 按 article 块逐个提取
articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)

projects = []
for art in articles:
    project = {}
    
    # 提取仓库完整名称（跳过 SVG 图标）
    name_match = re.search(
        r'<h2[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>.*?</a>.*?</h2>',
        art, re.DOTALL
    )
    if name_match:
        href = name_match.group(1)
        project['repo_url'] = 'https://github.com' + href
        # 从 href 提取 owner/repo
        parts = href.strip('/').split('/')
        if len(parts) >= 2:
            project['owner'] = parts[0]
            project['repo'] = parts[1]
            project['full_name'] = f"{parts[0]}/{parts[1]}"
    
    # 提取描述（class="col-9" 的 p 标签）
    desc_match = re.search(
        r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
        art, re.DOTALL
    )
    if desc_match:
        desc = desc_match.group(1).strip()
        desc = re.sub(r'<[^>]+>', '', desc)  # 移除内部 HTML 标签
        desc = desc.replace('\n', ' ').replace('&gt;', '>').replace('&amp;', '&').strip()
        project['desc'] = desc
    
    # 提取星标数
    star_match = re.search(r'([\d,]+)\s+stars?\s*(today|this week)?', art, re.IGNORECASE)
    if star_match:
        project['stars'] = star_match.group(1).replace(',', '')
        project['delta_period'] = star_match.group(2) or ''
    
    # 提取编程语言
    lang_match = re.search(
        r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>',
        art, re.DOTALL
    )
    if lang_match:
        project['language'] = lang_match.group(1).strip()
    
    if project.get('full_name'):
        projects.append(project)

print(f"Found {len(projects)} projects")
```

### 3. 输出示例

```
[1] colbymchenry/codegraph
    URL: https://github.com/colbymchenry/codegraph
    Desc: Pre-indexed code knowledge graph for Claude Code, Codex...
    Stars: 15909 (this week)
    Lang: TypeScript
```

## 常见问题

### SVG 图标污染 h2 文本
不要太信任 HTMLParser 直接从 h2 标签提取文本——SVG 图标的路径文本会被连带提取。
**解决方案**：直接取 `<a>` 标签的 `href` 属性中的 path，从 path 解析 owner/repo 更可靠。

### 星标数字格式
GitHub 使用逗号分隔千位数（如 "15,909"），解析后需要 `replace(',', '')` 转整数。

### 星标增量 vs 总数
"15,909 stars this week" 表示本周新增的星标数（不是总数）。
"15,909 stars"（无时间后缀）表示总星标数（few cases, mainly on daily trending）。
注意区分：`weekly` 页面上的数字是**本周新增**，而非项目总星数。
如果需要总星数，需单独调用 GitHub API。

### 时间范围参数
- `?since=daily` — 今日趋势（默认）
- `?since=weekly` — 本周趋势（适合周报）
- `?since=monthly` — 本月趋势
