# 字数统计方法论

## 核心原则

网文标准字数 = **纯汉字数**（只算中文汉字），不是总字符数。

## 统计方式对比

| 方式 | 命令 | 包含内容 | 适用场景 |
|------|------|----------|----------|
| 总字符数 | `wc -m` | 汉字+标点+空格+换行 | ❌ 不用于网文 |
| 纯汉字数 | Python `re.findall` | 只算汉字 | ✅ 网文标准 |

## 差距示例

```
文件：第277章_伊莱亚斯的回归.md
wc -m（总字符数）：4,545
纯汉字数：3,403
差距：1,142（约25%）
```

## 正确统计方式

```python
import re

with open('文件路径') as f:
    content = f.read()

hanzi = len(re.findall(r'[\u4e00-\u9fff]', content))
print(f"纯汉字数: {hanzi}")
```

## 常见错误

- ❌ `wc -m < file.md` → 总字符数（含标点空格）
- ❌ `wc -c < file.md` → 字节数
- ✅ Python `re.findall(r'[\u4e00-\u9fff]')` → 纯汉字数

## 在看板任务中的应用

任务body中应明确：
```
每章纯汉字数 4500-5500字（⚠️ 必须用Python统计汉字数，不用wc -m）
```

## 快速检查脚本

```bash
python3 -c "
import re, glob
for ch in range(A, B):
    files = glob.glob(f'第{ch}章_*.md')
    if files:
        with open(files[0]) as f: content = f.read()
        hanzi = len(re.findall(r'[\u4e00-\u9fff]', content))
        print(f'第{ch}章: {hanzi}字')
"
```
