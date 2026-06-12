# Verified AI-Flavor Replacements

> Replacements verified across 45 chapters of steam-punk cosmic horror web novel writing.
> Source model: deepseek-v4-pro (大莉D). Target: natural Chinese web novel style.

## Priority Replacements

These are the highest-frequency AI-flavor words found in actual writing. Replace in order of priority:

| AI-flavor Word | Replacement | Frequency in 45ch | Notes |
|----------------|-------------|:------------------:|-------|
| `微微` | Delete | 33 | Almost always deletable. "微微点头" → "点头". "微微一愣" → "一愣". |
| `轻轻` | Delete | 12 | "轻轻推开门" → "推开门". Adds nothing. |
| `缓缓` | Delete | 7 | "缓缓开口" → "说". "缓缓站起身" → "站起身". |
| `一丝` | `一点` | 5 | "一丝疲惫" → "一点疲惫". |
| `深吸一口气` | `吸了口气` | 1 | Not common in this corpus but high-impact when found. |
| `默默` | Delete | 1 | "默默跟在后面" → "跟在后面". |
| `仿佛` | `像` | 1 | "仿佛在笑" → "像在笑". |
| `眉头微皱` | `皱眉` | 1 | Always prefer the shorter form. |

## Manual (Non-Mechanical) Patterns

These required human judgment to fix, not simple find-replace:

### 1. Ending Sublimation Deletion (~7 instances found)

AI-written endings tend to summarize or philosophize. Fix: replace with action/object closure.

| Before | After |
|--------|-------|
| "但他知道——暴风雨还在前面。而他准备好了。" | `按住胸口+松手` (action) |
| "他知道——战争才刚刚开始" | `没说话` (action) |
| "他知道——城市还在唱歌" | `关门"咔嗒一声"` (object sound) |
| "但他知道——她在找会长的线索" | `她翻页的速度越来越快` (action) |
| "但他知道——倒计时开始了" | `手指戳地图+「查。」` (action+dialogue) |

**Rule:** Any ending containing "他知道…" or "这一刻…" can be safely replaced by the last concrete action/object/sound in the scene.

### 2. Stacked Metaphor Collapse (~3 instances found)

AI sometimes piles 3-5 parallel metaphors for the same thing. Fix: keep the one that works, delete the rest.

| Before | After |
|--------|-------|
| "像藤蔓。像血管。像某种活着的东西。像心跳。" | `像藤蔓。在脉动。` |
| "像有无数根针…像有无数条蛇…像两条蛇在缠斗。像两把刀在碰撞。" | Keep 1 metaphor |
| "像蜿蜒的河流。像干涸的河床。像永恒的印记。" | `像干涸的河床` |

**Rule:** Max 2 parallel metaphors. If 3+, delete until 1-2 remain.

### 3. Psychological Externalization (~3 instances found)

| Internal (AI) | External (Natural) |
|---------------|-------------------|
| "他不知道这意味着什么。但他知道——时间不多了。" | `他看着自己的手。手指在抖。他握紧了拳头。` |
| "他知道这种感受。" | `他有过这种感觉。` |
| "他知道。但说不清楚。" | `他说不清楚。` |

### 4. Dialogue De-formalization (~1 instance per 15 chapters)

| Before | After |
|--------|-------|
| "嘴角上扬" | `看了很久。然后转身。消失在巷子里。` |

### 5. Precision Quantifier Deletion

AI likes exact numbers for emotional beats. Replace with vaguer, more natural phrasing:

| Before | After |
|--------|-------|
| "杰克沉默了三秒。" | `杰克没说话。` |

## Bulk Scan Script

```python
import os, re

path = "/path/to/chapters"
banned = ["仿佛","犹如","宛若","一丝","一抹","些许","突然","缓缓","不禁","微微",
          "眼中闪过","嘴角勾起","眉头微皱","心中一动","不由得","深吸一口气",
          "似乎","有些","某种","轻轻","默默","渐渐","悄悄","稍稍"]

for f in sorted(os.listdir(path)):
    if not f.endswith('.md'): continue
    fp = os.path.join(path, f)
    with open(fp) as fh:
        content = fh.read()
    hits = []
    for w in banned:
        for m in re.finditer(re.escape(w), content):
            ctx = content[max(0,m.start()-15):min(len(content),m.end()+15)].replace('\n',' ')
            hits.append((w, ctx))
    if not hits:
        print(f"✅ {f} — 干净")
    else:
        print(f"\n⚠️  {f} ({len(content)}字)")
        for w, ctx in hits[:5]:
            print(f"    [{w}] ...{ctx}...")
        if len(hits) > 5:
            print(f"    ...还有 {len(hits)-5} 处")
```

## Bulk Fix Script

```python
import os

path = "/path/to/chapters"

replacements = [
    ("微微", ""), ("轻轻", ""), ("缓缓", ""),
    ("一丝", "一点"), ("些许", "一点"),
    ("不禁", ""), ("不由得", ""),
    ("深吸一口气", "吸了口气"),
    ("默默", ""), ("渐渐", "慢慢"),
    ("悄悄", ""), ("稍稍", ""),
    ("一抹", "一道"), ("眼中闪过", "眼里"),
    ("嘴角勾起", "嘴角"), ("眉头微皱", "皱眉"),
    ("心中一动", "心里一动"),
    ("突然", ""), ("似乎", ""), ("某种", ""), ("仿佛", "像"),
]

for f in sorted(os.listdir(path)):
    if not f.endswith('.md'): continue
    fp = os.path.join(path, f)
    with open(fp) as fh:
        original = fh.read()
    content = original
    for old, new in replacements:
        content = content.replace(old, new)
    if content != original:
        with open(fp, 'w') as fh:
            fh.write(content)
        print(f"  ✅ {f}")
```
