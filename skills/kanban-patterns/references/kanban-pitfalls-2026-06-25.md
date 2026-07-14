# Kanban Pitfalls (2026-06-25 Session)

## 33. Parallel Writing Worldbuilding Drift (Critical)

**Problem:** When writing novel chapters in parallel batches, workers completely ignore the worldbuilding constraints in the task body. Chapters end up with wrong settings, organizations, and character descriptions.

**Symptoms:**
- Chapters introduce non-existent locations (e.g., "西区" instead of "雾港")
- Characters gain wrong abilities (e.g., "蒸汽步枪" instead of "差分机")
- New organizations appear (e.g., "裁决所""黑巫师" instead of "共济会三派")

**Root Cause:** The kanban worker's LLM doesn't reliably follow negative constraints ("不要写X") in task bodies.

**Solution — Explicit Red Lines in Every Task Body:**
```
## 世界观红线（违反即为废稿）
- 地点=雾港（地面工业城市）
  禁止：西区/中城区/深渊/黑雾/圣母广场/北方军团/黄昏事务所
- 组织=共济会三派（温和派/激进派/纯理性派）
  禁止：裁决所/黑巫师/圣光骑士团
- 技术=金齿轮封印/朔月力量/差分机
  禁止：蒸汽步枪/畸变者
```

**Post-Completion Verification (Mandatory):**
```bash
for i in $(seq START END); do
  f=$(ls 第${i}章_*.md 2>/dev/null | head -1)
  [ -z "$f" ] && echo "❌ 第${i}章: 缺失" && continue
  bad=$(grep -c "FORBIDDEN_KEYWORDS" "$f")
  [ "$bad" -gt 0 ] && echo "❌ 第${i}章: 跑偏${bad}处" || echo "✅ 第${i}章"
done
```

## 34. Kanban Worker File Naming Issue

**Problem:** Workers write files as `第XXX章.md` instead of `第XXX章_标题.md`.

**Solution — Post-Completion Filename Fix:**
```bash
for i in $(seq START END); do
  f="第${i}章.md"
  if [ -f "$f" ]; then
    title=$(head -1 "$f" | sed 's/# //')
    newname=$(echo "$title" | sed 's/：/_/' | sed 's/ /_/g')
    mv "$f" "${newname}.md"
  fi
done
```

**Prevention:** Include in task body: "文件命名：第{编号}章_{标题}.md"

## 35. TTS Plugin Enablement

**Problem:** Configuring `tts.provider: mimo-clone` is not enough — plugin must be enabled in `plugins.enabled`.

**Solution:**
```bash
hermes plugins enable tts/mimo-clone
hermes gateway restart
```

## 36. Gemini Web API Limitations

**Problem:** gemini-web2api does NOT support function calling. Kanban workers crash when using it.

**Solution:** Don't use Gemini web proxy for kanban writing tasks. Use official APIs (DeepSeek, LongCat, MiMo).
