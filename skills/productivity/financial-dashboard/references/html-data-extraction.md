# 从金融看板 HTML 提取摘要数据

## 概述

金融看板 v5 的 HTML 文件是完全自包含的单页应用，所有数据嵌入在 `<script>` 标签中的 JavaScript 常量里。本文档说明如何从生成的 HTML 中提取结构化金融数据用于推送摘要。

## 数据结构

HTML 中嵌入了以下 JavaScript 常量：

### `const D = {...}` — 核心金融数据

每个 key 是 ticker 符号（如 `^DJI`、`AAPL`、`BTC-USD`），value 是对象：

```json
{
  "p": 50644.28,      // 最新价格 (price)
  "c": -41.87,        // 涨跌额 (change)
  "cp": -0.08,        // 涨跌幅百分比 (change percent)
  "h": 50830.41,      // 最高 (high)
  "l": 45057.28,      // 最低 (low)
  "kd": [...],        // 日K线数据 (daily K-line data)
  "kh": [...]         // 小时K线数据 (hourly K-line data)
}
```

K线数据格式：
```json
{"t": 1772514000, "o": 48493.11, "h": 48695.36, "l": 47626.85, "c": 48501.27}
// t=timestamp, o=open, h=high, l=low, c=close
```

### `const TICKERS = {...}` — 标的名称映射

按板块分组，每个板块包含 ticker 和中文名：
```json
{
  "美股·指数": [["^DJI", "道琼斯"], ["^GSPC", "标普500"], ...],
  "科技/AI": [["AAPL", "苹果"], ["MSFT", "微软"], ...],
  ...
}
```

## 提取方法

### ⚠️ 常见陷阱：BeautifulSoup 无法提取嵌入数据

**不要用 BeautifulSoup 提取金融数据。** BeautifulSoup 的 `get_text()` 只提取可见 HTML 文本，而金融数据嵌入在 `<script>` 标签的 JavaScript 变量中（`const D={...}`），BeautifulSoup 会返回空结果或仅返回页面标题/标签文字。

```python
# ❌ 错误：BeautifulSoup 只能看到页面骨架文字
soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text()  # → "金融看板\n📊 🇺🇸 指数, 🤖 科技/AI, ..."（无数据）

# ✅ 正确：直接用 regex 提取 JavaScript 变量
match = re.search(r'const D=(\{.*?\});\s*\n', html, re.DOTALL)
data = json.loads(match.group(1))  # → 完整的 ticker 数据字典
```

**实测验证（2026-07-04）**：626KB HTML 中 BeautifulSoup 仅返回 7 行骨架文字（标题、Tab标签），所有股票价格/涨跌幅数据均不可见。regex + json.loads 一次成功提取 76 个 ticker 的完整数据。

### 方法 A：Python json.loads 解析嵌入 JSON（首选，但可能失败）

从 HTML 中提取 `const D={...}` 并解析为 Python 字典：

```python
import re
import json

def extract_dashboard_data(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取 const D={...}
    d_match = re.search(r'const D=(\{.*?\});\s*\n', content, re.DOTALL)
    if not d_match:
        raise ValueError("Could not find const D in HTML")
    data = json.loads(d_match.group(1))
    
    # 提取 const TICKERS={...}
    t_match = re.search(r'const TICKERS=(\{.*?\});\s*\n', content, re.DOTALL)
    tickers = json.loads(t_match.group(1)) if t_match else {}
    
    # 构建 ticker → 中文名 反向映射
    sym_to_name = {}
    for section, items in tickers.items():
        for sym, name in items:
            sym_to_name[sym] = name
    
    return data, sym_to_name
```

> ⚠️ **json.loads 可能失败**：D 对象中的新闻数据（`nw` 数组）可能包含未转义的 HTML 片段和控制字符，导致 `JSONDecodeError`。遇到此错误时**立即回退到方法 B**，不要尝试修复 JSON。
>
> **实测经验（2026-07-01）**：json.loads **可以成功**——当新闻数据不包含未转义 HTML 时，626KB HTML 的 `const D={...}` 解析正常。**建议先尝试方法 A**，失败再用方法 B。

### 方法 B：Regex 提取摘要字段（可靠兜底，推荐用于 cron 推送）

当 JSON 解析失败时，用 regex 直接提取每个 ticker 的 `p`/`c`/`cp` 字段。不依赖 JSON 解析，绕过所有转义问题：

```python
import re

def extract_summary_regex(html_path):
    """从 HTML 提取每个 ticker 的价格/涨跌额/涨跌幅（regex 方式）"""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 找到 D 对象的边界（到 const SN= 或 const TICKERS= 为止）
    d_start = content.find('const D=') + len('const D=')
    sn_pos = content.find('const SN=', d_start)
    if sn_pos == -1:
        sn_pos = content.find('const TICKERS=', d_start)
    d_str = content[d_start:sn_pos].strip()
    
    # 提取每个 ticker 的摘要字段
    pattern = r'"([^"]+)":\s*\{"p":\s*([-\d.]+),\s*"c":\s*([-\d.]+),\s*"cp":\s*([-\d.]+)'
    matches = re.findall(pattern, d_str)
    
    data = {}
    for ticker, p, c, cp in matches:
        data[ticker] = {"p": float(p), "c": float(c), "cp": float(cp)}
    
    return data
```

**方法对比**：

| 维度 | 方法 A (json.loads) | 方法 B (regex) |
|:-----|:-------------------|:---------------|
| 数据完整性 | 完整（含K线、新闻） | 仅摘要（p/c/cp） |
| 可靠性 | 经常因未转义字符失败 | 非常可靠 |
| 适用场景 | 需要K线/新闻数据 | 仅需推送摘要（cron 场景） |
| 推荐 | 首选尝试 | **cron 推荐用此方法** |

**实际经验（2026-06-29）**：626KB HTML 中 D 对象含新闻 HTML 片段，`json.loads` 报 `JSONDecodeError`。regex 方法成功提取所有 ticker 的价格/涨跌幅数据。cron 推送场景只需要 p/c/cp，regex 方法是最佳选择。

### 提取后流程（两种方法共用）

### 步骤 1：验证数据有效性

提取 D 后，**必须先验证**数据是否有效，再生成摘要：

```python
good = sum(1 for k, v in data.items() if v.get('p', 0) > 0)
total = len(data)
print(f"有效标的: {good}/{total}")

if good == 0:
    raise ValueError(
        f"HTML 无有效数据（{total} 个标的均无价格），"
        "可能是 yfinance 限速+无缓存导致的空壳 HTML，跳过推送"
    )
```

**为什么要验证**：gen_v5.py 在 yfinance 全局限速且无缓存时，仍会生成一个空模板 HTML 并打印"✅ 看板已生成"。此时 D 变量存在但所有标的的 `p` 为 0。不验证就推送等于发一条空消息到 Discord。

### 步骤 2：生成摘要

```python
def generate_summary(data, sym_to_name, categories):
    lines = []
    for cat_name, symbols in categories.items():
        lines.append(f"**{cat_name}**")
        for sym in symbols:
            if sym in data:
                d = data[sym]
                price = d["p"]
                chg_pct = d["cp"]
                name = sym_to_name.get(sym, sym)
                arrow = "📈" if chg_pct >= 0 else "📉"
                sign_pct = "+" if chg_pct >= 0 else ""
                lines.append(f"  {arrow} {name}: {price:,.2f} ({sign_pct}{chg_pct:.2f}%)")
        lines.append("")
    return "\n".join(lines)
```

### 分类定义（v2.6+ 完整版，含港股/A股板块拆分）

```python
categories = {
    "美股·指数": ["^DJI", "^GSPC", "^IXIC", "^RUT", "^VIX"],
    "科技/AI": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AVGO", "AMD", "ARM", "CRM", "ORCL", "PLTR", "SMCI"],
    "金融/消费": ["JPM", "GS", "V", "MA", "WMT", "COST", "HD", "NFLX", "DIS"],
    "工业/能源": ["CAT", "BA", "GE", "XOM", "CVX", "TSM"],
    "医药/防御": ["UNH", "JNJ", "LLY", "PFE", "MRK", "PG", "KO", "PEP"],
    "港股·指数": ["^HSI"],
    "港股·科技": ["0700.HK", "9988.HK", "3690.HK", "9618.HK", "9999.HK", "1810.HK"],
    "港股·金融": ["0388.HK", "1299.HK", "0005.HK"],
    "港股·工业": ["1211.HK"],
    "A股·指数": ["000001.SS"],
    "A股·消费": ["600519.SS", "000858.SZ", "600887.SS"],
    "A股·金融": ["601398.SS", "600036.SS", "601318.SS", "601939.SS"],
    "A股·医药": ["600276.SS"],
    "A股·工业": ["300750.SZ", "000333.SZ", "002415.SZ"],
    "固定收益/汇率": ["SHV", "TLT", "JPY=X", "CNY=X", "EURUSD=X"],
    "虚拟货币/商品": ["BTC-USD", "ETH-USD", "SOL-USD", "GC=F", "SI=F", "CL=F"],
}
```

> ⚠️ 此处列出的是截至 2026-07-08 的完整分类（76 个标的）。实际使用时应从 HTML 中的 `const TICKERS` 动态提取，而非硬编码——因为标的会随时间增减。参考上面「方法 A/B」的提取代码。

## 注意事项

- HTML 中的 `const D={...}` 可能很大（600KB+ 文件），正则提取时用 `re.DOTALL` 确保跨行匹配
- JSON 解析前不需要处理 JS 花括号转义（Python `json.loads` 直接处理）
- 如果需要提取新闻数据（`n.t`/`n.s` 字段），需要在 `D` 的每个 ticker 对象中查找 `nw` 数组
