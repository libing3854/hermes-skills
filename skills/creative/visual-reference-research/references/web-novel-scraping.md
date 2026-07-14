# 中文小说网站抓取技术参考

## 已验证的抓取模式（wa01.com / ttkan.co / cn.wa01.com）

### 页面结构
- SSR（服务端渲染），urllib/curl 可直接获取HTML
- 内容在 `<div class="content">` 中
- 每段用 `<p>` 标签包裹
- 广告插入：`<center><div class="mobadsq"></div></center>` — 提取时需跳过
- 章节标题在 `<h1>` 标签中

### URL模式
```
https://www.wa01.com/novel/pagea/{book_slug}_{chapter_num}.html
https://cn.wa01.com/novel/pagea/{book_slug}_{chapter_num}.html  # 简体版
https://www.ttkan.co/novel/pagea/{book_slug}_{chapter_num}.html
```

### 提取代码
```python
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def download_chapter(url):
    req = urllib.request.Request(url, headers=headers)
    html = urllib.request.urlopen(req, timeout=15, context=ctx).read().decode('utf-8', errors='ignore')
    
    # 标题
    title_match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_match.group(1).strip() if title_match else 'Unknown'
    
    # 内容（匹配content div到下一个center或div_feedback）
    content_match = re.search(r'<div\s+class="content">(.*?)</div>\s*(?:<center>|<div\s+class="div_feedback")', html, re.DOTALL)
    if not content_match:
        content_match = re.search(r'<div\s+class="content">(.*?)</div>', html, re.DOTALL)
    
    if content_match:
        p_tags = re.findall(r'<p[^>]*>(.*?)</p>', content_match.group(1), re.DOTALL)
        lines = [re.sub(r'<[^>]+>', '', p).strip() for p in p_tags if len(re.sub(r'<[^>]+>', '', p).strip()) > 1]
        content = '\n'.join(lines)
        hanzi_count = len(re.findall(r'[\u4e00-\u9fff]', content))
        return title, content, hanzi_count
    return None
```

### 限流处理
- 连续抓取600+章后会触发SSL握手超时或连接重置
- 解决方案：
  1. 每章间隔0.2-0.3秒
  2. 每10章间隔0.5秒
  3. 超时后换域名重试（wa01.com → cn.wa01.com → ttkan.co）
  4. 大批量用 `terminal background=true` 分批执行
  5. 每批完成后检查已下载章节数，从断点继续

### 保存格式
```
拆文库/{书名}/
├── 第0001章.md
├── 第0002章.md
├── ...
├── 第0684章.md
├── {书名}_全文.md    # 合并文件
├── 章节目录.md       # 章节索引
└── metadata.json     # 元数据
```

### 已知问题
- 同一内容在不同域名（wa01/ttkan）可能章节号偏移1（如wa01的614章=ttkan的615章）
- 部分章节标题含繁体字，内容可能是简体或繁体
- Cloudflare验证会拦截部分请求，需要换域名或等待
