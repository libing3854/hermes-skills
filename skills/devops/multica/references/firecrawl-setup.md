# Firecrawl 安装和配置

## 概述
Firecrawl ⭐ 139K — 大规模网络搜索、抓取和交互API。AI Agent获取网络数据的首选工具。

## 安装
```bash
pip3 install firecrawl-py
```

## API Key
1. 注册：https://firecrawl.dev
2. 获取API Key（格式：`fc-`开头36字符）
3. 写入Hermes环境：
```bash
# 注意：v0.17.0的redact_secrets会拦截fc-前缀key
# 需先临时关闭：hermes config set security.redact_secrets false
echo "FIRECRAWL_API_KEY=*** >> ~/.hermes/.env
# 恢复：hermes config set security.redact_secrets true
```

## 使用示例
```python
from firecrawl import FirecrawlApp
app = FirecrawlApp(api_key="fc-...")

# 抓取网页
result = app.scrape_url("https://example.com", formats=['markdown'])
md = result.markdown  # Markdown内容

# 搜索
results = app.search("AI agent 2026", source="web")
```

## 自托管（需要Docker）
```bash
git clone https://github.com/firecrawl/firecrawl
cd firecrawl
docker compose up -d
```

## 我们的替代方案
- Hermes内置：`web_extract` (markdown提取)、`web_search` (搜索)
- Firecrawl优势：大规模批量抓取、JS渲染、结构化提取、代理轮换
- 适用场景：需要批量抓取>10个页面，或需要JS渲染的动态页面
