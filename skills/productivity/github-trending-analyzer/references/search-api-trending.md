# GitHub Search API 模拟 Trending 方案

GitHub Trending 页面已客户端渲染，curl 无法获取数据。用 Search API 替代。

## 双查询策略

同时发起两个查询，合并去重，模拟 Trending 效果：

### 查询 1：最近创建增长最快
```
created:<YYYY-MM-DD>..<YYYY-MM-DD> sort:stars
```
捕获最近一周新创建且 star 增长最快的仓库。

### 查询 2：近期活跃高 star
```
stars:>1000 pushed:><YYYY-MM-DD> sort:stars
```
捕获已有高 star 且近期仍在活跃更新的仓库。

## Python 参考实现

```python
#!/usr/bin/env python3
"""Fetch GitHub trending-like data using search API."""
import urllib.request
import urllib.parse
import json
import os
import sys
from datetime import datetime, timedelta

token = os.environ.get('GITHUB_TOKEN', '')
today = datetime.utcnow()
week_ago = today - timedelta(days=7)
week_ago_str = week_ago.strftime('%Y-%m-%d')
today_str = today.strftime('%Y-%m-%d')

queries = [
    f"created:{week_ago_str}..{today_str} sort:stars",
    f"stars:>1000 pushed:>{week_ago_str} sort:stars",
]

all_repos = []
seen = set()

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/vnd.github.v3+json',
}
if token:
    headers['Authorization'] = f'token {token}'

for q in queries:
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q)}&per_page=30"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    for r in data.get('items', []):
        if r['full_name'] not in seen:
            seen.add(r['full_name'])
            all_repos.append({
                'full_name': r['full_name'],
                'description': r.get('description', '') or '',
                'language': r.get('language', '') or '',
                'stars': r.get('stargazers_count', 0),
                'forks': r.get('forks_count', 0),
                'updated_at': r.get('updated_at', ''),
                'created_at': r.get('created_at', ''),
                'topics': r.get('topics', []),
                'html_url': r.get('html_url', ''),
                'owner': r.get('owner', {}).get('login', ''),
            })

print(json.dumps(all_repos, ensure_ascii=False))
```

## 按领域分类关键词

对 Search API 返回的结果按关键词分类：

| 分类 | 关键词（名称/描述/主题/lang 匹配） |
|------|------|
| 🤖 AI / ML | ai, llm, gpt, agent, deep-learning, machine-learning, neural, transformer, nlp, pytorch, tensorflow, ollama, langchain, openai, claude, anthropic, generative-ai |
| 💻 开发工具 | cli, developer-tools, docker, kubernetes, automation, workflow, ide, editor, sandbox, terminal, shell, zsh, git |
| 🌐 前端 / Web | react, vue, nextjs, frontend, web, css, javascript, typescript, html, ui, tailwind, bootstrap, svelte |
| 📱 移动端 | ios, android, flutter, mobile, react-native, swift, dart |
| ⚡ 系统 / CLI | linux, kernel, rust, go, c++, system, operating-system, security, network, database, server, self-hosted, embedded, firmware, ssh |
| 🎮 其他 | 不属于以上分类的项目 |

分类逻辑：将项目的 name + description + topics + lang 合并转为小写集合，与各分类关键词集合做交集匹配。

## 注意事项

- Search API 未认证限流：每小时 30 次
- 合并两个查询最多获取 60 个不重复项目
- `urllib.parse.quote` 需要对查询字符串做 URL 编码
- 不要用 `curl | python3` 管道方式（安全策略拦截），先写脚本到文件再执行
