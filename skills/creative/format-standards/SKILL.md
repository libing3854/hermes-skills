---
name: format-standards
description: 格式规范 - 输出格式、文件命名、目录结构
version: 1.0
tags: [格式, 规范, 文件, 命名]
---

# 格式规范

## 核心原则

1. **绝不泄露内部思考过程**（Reasoning/Thinking块）给用户
2. **用户提供参考格式时**，必须完全匹配其格式
3. **默认大白话**，除非明确要求文言文

## 文件命名规范

### 小说章节
```
第XXX章_章节名.md
```
示例：
- 第245章_退潮倒计时.md
- 第256章_十五岁的女孩.md

#### 内部标题格式
文件第一行必须是章节标题，格式为：
```
# 第XXX章：章节名
```
示例：
- `# 第245章：退潮倒计时`
- `# 第353章：三方同处一室`

⚠️ kanban worker默认只写 `# 第XXX章`（无标题），每批完成后需手动补标题并rename文件。

#### 批量rename脚本（一次性完成文件名+内部标题）
```bash
cd /Users/libing/Desktop/临时文件-0001/脑洞文/第七卷_同源之战/

# 标题映射（ch:title格式）
declare -A T
T[353]="三方同处一室"
T[354]="摊牌"
T[355]="暗巷"
# ... 添加所有章节

for ch in "${!T[@]}"; do
  old="第${ch}章.md"
  title="${T[$ch]}"
  new="第${ch}章_${title}.md"
  [ -f "$old" ] && mv "$old" "$new" && \
  sed -i '' "s/^# 第${ch}章$/# 第${ch}章：${title}/" "$new" && \
  echo "✅ $old → $new"
done
```

⚠️ macOS默认bash是3.x，不支持`declare -A`关联数组。替代方案：用`eval`或直接写循环：
```bash
for pair in "353:三方同处一室" "354:摊牌" "355:暗巷"; do
  ch="${pair%%:*}"; title="${pair##*:}"
  old="第${ch}章.md"; new="第${ch}章_${title}.md"
  [ -f "$old" ] && mv "$old" "$new" && \
  sed -i '' "s/^# 第${ch}章$/# 第${ch}章：${title}/" "$new"
done
```

### 审核报告
```
第XXX-XXX章审核报告.md
```
示例：
- 第245-255章审核报告.md
- 第256-262章审核报告.md

### 语音文件
```
morning_report_YYYYMMDD_HHMM.mp3
finance_brief_YYYYMMDD_HHMM.mp3
lilith_love.wav
```

### 金融看板
```
金融看板_v5_YYYYMMDD_HHMM.html
```

## 目录结构

### 小说项目
```
/Users/libing/Desktop/临时文件-0001/脑洞文/
├── 新第四卷_详细章节大纲_潮港青铜.md
├── 正文/
│   ├── 第245章_退潮倒计时.md
│   ├── 第246章_沉钟船坞.md
│   └── ...
├── 正文_agnes/
│   ├── 第246章_沉钟船坞.md
│   └── ...
└── 小说检查报告/
    ├── 第245-255章审核报告.md
    └── ...
```

### 语音克隆
```
/Users/libing/Desktop/中岛美雪语音克隆/
├── nakajima_miyuki.wav          (参考音频，保留)
├── 早期_clone.wav
├── 中期_clone.wav
├── 近期_clone.wav
└── 定期清除/
    ├── lilith_love.wav
    └── ...
```

### 金融看板
```
/Users/libing/Desktop/美股总结/
├── 金融看板_v5_20260611_0605.html
├── .finance_cache.json
└── ...
```

## 输出格式

### 审核报告格式
```markdown
# 第XXX-XXX章审核报告

## 一、综合评估
| 指标 | 评分 |
|------|------|
| 综合得分 | XX/100 |
| 等级 | X级 |

## 二、各章评分速览
| 章节 | 中文字数 | "像" | 禁用词 | "某种" | 微微/缓缓 | 评分 |
|------|---------|------|--------|--------|----------|------|

## 三、具体修改建议
### 需立即修复的硬伤
| 优先级 | 章节 | 位置 | 问题 | 修改建议 |

## 四、总结
| 维度 | 评级 | 说明 |
```

### 早报格式
```markdown
【⏰ 日期 | 农历 | 时间】

🌤️ 天气：宁波XX，XX~XX°C，AQI XX（XX）

🌍 国际新闻
• [标题] — [一句话简述] [信源]

🇨🇳 国内新闻
• [标题] — [一句话简述] [信源]

🏪 物价
• 92号 X.XX元/L | 95号 X.XX元/L [信源]

📜 黄历：宜XX、XX | 忌XX、XX

⭐ 星座运势
• 白羊 ★★★★☆ ...

💬 [鼓励寄语]

MEDIA:~/voice-memos/morning_report_YYYYMMDD_HHMM.mp3
```

## 注意事项

1. 所有输出路径使用绝对路径
2. 文件名避免特殊字符
3. 日期格式统一为YYYYMMDD
4. 时间格式统一为HHMM
5. 音频文件后缀统一为.wav或.mp3
