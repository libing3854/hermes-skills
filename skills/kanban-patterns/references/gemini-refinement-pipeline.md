# Gemini精修流水线

## 概述
使用本地Gemini API（shanliG profile）对闪莉初写版进行文本精修，然后用Python脚本清理高频词残留。

## 架构
```
闪莉初写 → Gemini精修 → Python脚本清理 → 莉莉审核 → 移入主目录
```

## shanliG Profile配置
```yaml
# ~/.hermes/profiles/shanliG/config.yaml
model:
  provider: gemini-local
  default: gemini-3.5-flash

providers:
  gemini-local:
    name: Gemini Local
    api_key: none
    api_mode: chat_completions
    base_url: http://localhost:8081/v1
    context_length: 1048576
    default_model: gemini-3.5-flash
```

## Gemini API调用
```python
import requests

API_URL = "http://localhost:8081/v1/chat/completions"
MODEL = "gemini-3.5-flash"

REFINE_PROMPT = """你是专业中文网络小说精修编辑。请对以下章节进行精修。

【精修规则】
1. 禁用词（0次）：仿佛→如同/像是/若/宛若；深吸一口气→吸了口气/深呼吸/屏住呼吸；不由得→忍不住/不禁
2. 高频词上限：像≤10次/章，如同≤3次，某种≤3次，一种≤3次，微微≤3次，缓缓≤3次
3. 字数：保持4500-6000纯汉字
4. 去AI味：删除冗余修饰、重复句式、模板化描写
5. 保留原文剧情和角色行为不变
6. 输出完整章节markdown，不要任何解释

【原文】
"""

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": REFINE_PROMPT + original_text}],
    "temperature": 0.3,
    "max_tokens": 16384
}
resp = requests.post(API_URL, json=payload, timeout=300)
refined = resp.json()["choices"][0]["message"]["content"]
```

## Python高频词清理脚本
关键逻辑：
1. 统计每个问题词出现次数
2. 对超标词找到每个位置的上下文
3. 根据上下文智能替换（不盲目删除）
4. "一种"替换方案：删"一种"保留后续名词 / 改为"那""此"

## 已知问题
- Gemini对"一种"清理不彻底（可能残留），需要Python脚本兜底
- Gemini可能引入新的禁用词（如"仿佛"），需要第二轮检查
- 296章可能返回错误消息（API不稳定），需要重试机制

## 验证脚本
```python
import re, os
for f in sorted(os.listdir('.')):
    if not f.endswith('.md'): continue
    with open(f) as fh: t = fh.read()
    cn = len(re.findall(r'[\u4e00-\u9fff]', t))
    fb = any(t.count(w)>0 for w in ['仿佛','深吸一口气','不由得'])
    fq = any(t.count(w)>l for w,l in [('像',10),('如同',3),('某种',3),('一种',3),('微微',3),('缓缓',3)])
    st = 'OK' if not fb and not fq else '!!'
    print(f'{st} {f[:20]:20s} {cn:5d}字')
```
