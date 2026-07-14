# Novel Chapter File Naming Convention

## Format Rules

All chapter files MUST follow:

- **Filename**: `第{ch}章_{标题}.md`
  - Example: `第353章_三方同处一室.md`
  - ❌ Wrong: `第353章.md` (missing title suffix)
  
- **Internal title**: `# 第{ch}章：{标题}` (use colon, not underscore)
  - Example: `# 第353章：三方同处一室`
  - ❌ Wrong: `# 第353章` (missing title)
  - ❌ Wrong: `# 第353章_三方同处一室` (underscore instead of colon)

## Task Body Template

When creating writing tasks for lili/闪莉, include in the body:
```
要求：
...
4. 以# 第{ch}章：{标题}开头
5. 保存到当前目录（第{ch}章_{标题}.md）
```

## Post-Batch Verification

After batch writing completes, check all files have title suffixes:
```bash
cd /path/to/chapters/
for f in *.md; do
  [[ "$f" != *_* ]] && echo "⚠️ 缺标题后缀: $f"
done
```

For files missing titles, read the chapter opening (first 3-8 lines) to determine an appropriate title, then:
1. Rename: `mv 第{ch}章.md 第{ch}章_{标题}.md`
2. Update header: `sed -i '' 's/^# 第{ch}章$/# 第{ch}章：{标题}/' 第{ch}章_{标题}.md`

## Title Style Guide

Titles should be:
- 2-5 Chinese characters
- Drawn from the chapter's core imagery/action/scene
- Have narrative tension (有份量)
- NOT plot descriptions (e.g., ❌ "卷末收尾")
- NOT weird/quirky names

Good examples from Volume 7: 暮色、裂缝、伤口、开口、铁穹、但书、那还好、碎窗
