# 已验证数据源清单（每日早报）

> 最后更新：2026-07-07

## 天气与环境

| 数据源 | URL | 方法 | 状态 | 备注 |
|--------|-----|------|------|------|
| wttr.in（JSON格式） | `https://wttr.in/Ningbo?format=j1` | curl + Python解析 | ✅ **最佳** | 返回JSON，含当前温度/天气/湿度/风速/日出日落/当日高低温，比纯文本格式更全面 |
| wttr.in（纯文本） | `https://wttr.in/Ningbo?format=%l:+%t+%C+%h+%w+%p` | curl | ✅ 可靠 | 纯文本一行，含温度/天气/湿度/风速/降水 |
| aqicn.org | `https://aqicn.org/city/ningbo/` | curl + Python正则 | ✅ 可用 | 提取 `\"aqi\":(\d+)` 和 PM2.5，2026-06-28 实测 AQI=89, PM2.5=10 |

**天气JSON解析示例（推荐）：**
```bash
curl -sL --max-time 15 'https://wttr.in/Ningbo?format=j1' | python3 -c "
import json, sys
data = json.load(sys.stdin)
cur = data['current_condition'][0]
today = data['weather'][0]
print(f'当前: {cur[\"temp_C\"]}°C, {cur[\"weatherDesc\"][0][\"value\"]}')
print(f'今日: {today[\"mintempC\"]}~{today[\"maxtempC\"]}°C')
print(f'湿度: {cur[\"humidity\"]}%, 风速: {cur[\"windspeedKmph\"]}km/h {cur[\"winddir16Point\"]}')
"
```

## 油价

| 数据源 | URL | 方法 | 状态 | 备注 |
|--------|-----|------|------|------|
| 9856.cn 宁波油价 | `https://9856.cn/youjia/0123/` | curl + Python正则 | ✅ **可用** | 2026-07-07 实测 curl 可直接获取价格文本，页面含价格+涨幅多组数字 |
| 中石化直销 | `https://cx.sinopecsales.com/yjkqiantai/core/main` | — | ⚠️ 需省市选择 | 仅web_search snippet可用 |

**油价提取示例（curl方案）：**
```bash
curl -sL --max-time 15 'https://9856.cn/youjia/0123/' -o /tmp/gasprice.html
python3 -c "
import re
with open('/tmp/gasprice.html', encoding='utf-8', errors='replace') as f:
    html = f.read()
# ⚠️ 关键：必须用精确正则匹配第一个价格，页面中每种油有多个数字（价格+涨幅）
# ✅ 正确：r'92号[^\d]*?(\d+\.\d{2})' — 匹配 7.15
# ❌ 错误：r'95[号号汽油]*[^\d]*(\d+\.\d+)' — 可能匹配到涨幅 3.4 而非价格 7.61
for pat, name in [(r'92号[^\d]*?(\d+\.\d{2})', '92号'), (r'95号[^\d]*?(\d+\.\d{2})', '95号'), (r'0号[^\d]*?(\d+\.\d{2})', '0号柴油')]:
    ms = re.findall(pat, html)
    if ms: print(f'{name}: {ms[0]}')
"
# 2026-07-07 实测输出：92号 7.15, 95号 7.61, 0号柴油 6.81
```

## 黄历/宜忌

| 数据源 | URL | 方法 | 状态 | 备注 |
|--------|-----|------|------|------|
| jiyuntang.com | `https://www.jiyuntang.com/huangli/YYYYMMDD.html` | curl + Python | ✅ **首选** | ⚠️ 页面有双"宜"结构（第一个"宜"是神煞，第二个才是实际宜忌）。提取正则：`r'宜\s+(嫁娶[\u4e00-\u9fa5、\s]+?)\s*忌\s+([\u4e00-\u9fa5、\s]+?)(?:\s*时辰)'` |
| ~~nongminli.com~~ | ~~`https://m.nongminli.com/YYYY-MM-DD.html`~~ | — | ❌ **已降级** | 2026-07-10 实测返回空宜忌内容（页面结构已变），不再可用 |
| wnlcha.com | `https://www.wnlcha.com/rili/YYYY/MM-DD.html` | web_search snippet | ✅ 可用 | snippet含宜忌摘要 |

**黄历提取示例（nongminli.com）：**
```bash
curl -sL --max-time 15 'https://m.nongminli.com/2026-07-01.html' -o /tmp/huangli.html
python3 -c "
import re
with open('/tmp/huangli.html', encoding='utf-8', errors='replace') as f:
    html = f.read()
# 宜忌在页面文本中，格式：宜祭祀 沐浴 破屋 坏垣 馀事勿取 忌入宅 嫁娶 移徙
yi_match = re.search(r'宜([^忌]*)忌', html, re.DOTALL)
ji_match = re.search(r'忌([^$]*)', html, re.DOTALL)
if yi_match:
    yi = re.sub(r'<[^>]+>', '', yi_match.group(1)).strip()
    print(f'宜：{yi}')
if ji_match:
    ji = re.sub(r'<[^>]+>', '', ji_match.group(1)).strip()
    print(f'忌：{ji}')
"
```

## 星座运势

| 数据源 | URL | 方法 | 状态 | 备注 |
|--------|-----|------|------|------|
| ~~12sign.cn~~ | `https://www.12sign.cn/xzys/{文章ID}.html` | curl + GBK解码 | ❌ **不可靠** | 2026-06-28 实测：web_search找不到当日文章ID，首页curl只返回无关内容 |
| ~~mofalulu.com~~ | ~~`https://en.mofalulu.com/astrological/astro_d_YYYY-MM-DD.html`~~ | — | ❌ **已失效** | 2026-06-25 起返回 bot 验证页 |
| ~~horoscope.com~~ | `https://www.horoscope.com/us/horoscopes/general/horoscope-general-daily-today.aspx?sign=N` | curl | ❌ **JS渲染** | 页面为JS动态加载，curl仅返回导航菜单，无实际运势内容 |
| ~~astrosage.com~~ | `https://www.astrosage.com/horoscope/daily-horoscope.asp` | curl | ❌ **无数据** | 返回的是通用介绍文本，非每日运势 |
| ~~d1xz.net~~ | 多个URL | curl | ❌ **空结果** | 连接失败或返回空 |
| ~~zodiacsign.com~~ | `https://www.zodiacsign.com/horoscope/today/` | curl | ❌ **空结果** | 无实际内容 |

> ⚠️ **2026-06-28 重要发现：所有主流星座运势网站均无法通过curl获取每日运势数据。** 原因：大多数网站使用JS动态渲染，或需要登录/API。
>
> **降级方案：** 当无法获取真实星座数据时，基于黄历宜忌和星期（周末/工作日）生成通用运势参考，标注"基于黄历推算"。或通过 `web_search` 搜索 `今日星座运势` 尝试从搜索结果snippet获取部分信息。

## 新闻源

| 信源 | URL | Bot检测 | curl可用 | 备注 |
|------|-----|---------|----------|------|
| BBC | bbc.com/news | ⚠️ **持续超时** | ❌ | 2026-07-02 实测仍超时，不可作为主力源 |
| AP News | apnews.com | ⚠️ **curl返回空内容** | ❌ | 2026-07-02 实测 curl 仅返回 "Short Stories" 标题，无新闻内容 |
| Reuters | reuters.com | ❌ 强CAPTCHA | ❌ | 仅用web_search |
| Bloomberg | bloomberg.com | ❌ 强CAPTCHA/连接失败 | ❌ | 仅用web_search |
| **新浪新闻** | sina.com.cn | ✅ 友好 | ✅ **首选** | 2026-07-02 实测：`browser_navigate` 到 `/world/` 和 `/china/` 可获取 15+ 条新闻标题，是最可靠的新闻源。curl 需注意 GBK 编码 |
| **TechCrunch** | techcrunch.com | ✅ 友好 | ✅ 可用 | AI/科技新闻 |
| **CNN** | cnn.com | ✅ 可用 | ⚠️ 有限 | curl 可获取部分标题 |
| 新华网 | xinhuanet.com / chinanews.com.cn | ✅ 友好 | ✅ | 国内新闻备选 |
| 央视 | cctv.com | ✅ 友好 | ⚠️ 内容少 | curl 返回内容有限 |

**新闻抓取优先级（2026-07-02 更新）：**
1. `sina.com.cn` — **国内外新闻首选**，`browser_navigate` 最可靠（curl 需 GBK 编码处理）
2. `techcrunch.com` — AI/科技新闻
3. `cnn.com` — 国际新闻备选
4. BBC/Guardian/AP News — 仅当 browser 可用且其他方式失败时尝试（超时率高）

**新闻提取示例（sina.com.cn — browser_navigate 方式，2026-07-02 推荐）：**
```
browser_navigate → https://news.sina.com.cn/world/
# 从 snapshot 中提取 heading 标签的新闻标题
# 国际新闻：提取 <h2> 标签中的标题文本
# 国内新闻：同理访问 /china/
```

**新闻提取示例（sina.com.cn — curl 方式）：**
```bash
curl -sL --max-time 15 'https://news.sina.com.cn/' -o /tmp/sina.html
python3 -c "
import re
# ⚠️ 注意：sina.com.cn 使用 GBK 编码，必须指定 encoding='gbk'
with open('/tmp/sina.html', encoding='gbk', errors='ignore') as f:
    html = f.read()
titles = re.findall(r'<a[^>]*>([^<]{12,80})</a>', html)
titles = [t for t in titles if not t.startswith('http')]
seen = set()
for t in titles[:15]:
    if t not in seen:
        seen.add(t)
        print(t)
"
```

## 交付渠道

| 渠道 | 方式 | 备注 |
|------|------|------|
| Telegram | cron job 自动路由 | 输出作为 response 即可，无需 CLI 发送 |
| CLI终端 | 直接输出 | MEDIA标签自动拦截 |

## 技术备注

### 搜索工具在 cron 模式下的限制
- **`web_search`**：不稳定，`site:` 过滤器有时返回空结果
- **`mcp_anysearch_search`（Anysearch MCP）**：2026-07-07 实测连续4次超时（60秒），在 cron 模式下同样不可靠
- **结论**：cron 模式下不要依赖任何搜索工具，直接用 `browser_navigate` 或 `curl` 获取数据

### 浏览器工具失效的降级策略
2026-06-28 实测：browser_navigate 对 BBC、AP News、The Guardian、horoscope.com 等多个网站均返回 `net::ERR_CONNECTION_CLOSED` 或超时。

**降级顺序：**
1. 先尝试 `curl` + Python解析（最可靠）
2. 若curl也失败，尝试 `web_search` 获取snippet
3. 若所有方式失败，诚实告知并提供已获取的其他信息

### 黄历宜忌提取注意
**jiyuntang.com 提取方法（2026-07-10 更新）：**
页面有双"宜"结构——第一个"宜"在神煞部分（如 `宜趋 民日 天巫...`），第二个"宜"才是实际宜忌（如 `宜 嫁娶 开光 解除...`）。

```python
import re
with open('/tmp/huangli.html', encoding='utf-8', errors='ignore') as f:
    html = f.read()
text = re.sub(r'<[^>]+>', ' ', html)  # 清理HTML标签
text = re.sub(r'\s+', ' ', text)       # 压缩空白

# 方法1：精确正则（推荐，跳过神煞部分直接匹配实际宜忌）
match = re.search(r'宜\s+(嫁娶[\u4e00-\u9fa5、\s]+?)\s*忌\s+([\u4e00-\u9fa5、\s]+?)(?:\s*时辰)', text)
if match:
    yi = re.sub(r'\s+', '、', match.group(1).strip())
    ji = re.sub(r'\s+', '、', match.group(2).strip())
    print(f'宜：{yi}')
    print(f'忌：{ji}')

# 方法2：查找第二个"宜"（兜底方案）
# 找到所有"宜"的位置，取第二个（第一个是神煞）
yi_positions = [m.start() for m in re.finditer('宜', text)]
if len(yi_positions) >= 2:
    second_yi = text[yi_positions[1]:yi_positions[1]+300]
    # 提取"宜"到"忌"之间的内容
    match2 = re.search(r'宜\s*(.*?)\s*忌', second_yi)
    if match2:
        yi = re.sub(r'\s+', '、', match2.group(1).strip())
        print(f'宜：{yi}')
```

**nongminli.com（已降级，仅供参考）：**
2026-07-10 实测返回空宜忌内容，页面结构已变。旧方法已不可用。
