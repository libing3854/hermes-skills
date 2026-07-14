# 章节重编号与版本管理

## 重编号流程（TEMP_前缀法）

### 问题
批量重编号文件时，直接改名会导致冲突（新旧文件名重叠）。

### 解决方案：两步法
```bash
# Step 1: 所有文件加TEMP_前缀
for f in 第*.md; do mv "$f" "TEMP_$f"; done

# Step 2: TEMP_文件改为最终名
python3 -c "
import os, re
mapping = {old_num: new_num, ...}
for old, new in mapping.items():
    for f in os.listdir('.'):
        if f.startswith(f'TEMP_第{old:03d}章_'):
            title = re.search(r'第\d+章_(.+)', f).group(1)
            os.rename(f, f'第{new:03d}章_{title}')
"
```

### 关键点
1. **必须先全部加TEMP_前缀**，再改为最终名。否则会有命名冲突。
2. **用Python脚本执行**，比shell循环更可靠（处理文件名特殊字符）。
3. **验证**：改完后检查 `ls TEMP_*.md | wc -l` 应为0。

## 版本管理

### 问题
同一章节被多次重写，目录中存在多个版本（V1/V2/V3/V4）。

### 解决方案
1. **确定正典版本**：根据大纲匹配度、质量评估选择最终版
2. **移动非正典版本**：`正文_废弃版本/` 目录
3. **不要删除**：用户可能需要参考旧版
4. **重编号**：正典版本统一重新编号，确保连续

### 冰哥偏好
- 废弃版本目录由冰哥自己处理，不要擅自删除
- 重编号后必须让冰哥确认编号再继续

## 内部标题同步

### 问题
文件名改了但文件内部 `# 第XXX章` 没改。

### 解决方案
```bash
# 检查内部标题与文件名是否一致
for f in 第*.md; do
  file_num=$(echo "$f" | grep -o '第[0-9]*章' | head -1 | sed 's/第//;s/章//')
  internal_num=$(head -1 "$f" | grep -o '第[0-9]*章' | head -1 | sed 's/第//;s/章//')
  [ "$file_num" != "$internal_num" ] && echo "不一致: $f (文件:$file_num 内部:$internal_num)"
done

# 批量修正内部标题（Python脚本，比sed更可靠）
python3 -c "
import os, re
for f in sorted(os.listdir('.')):
    match = re.match(r'^第(\d+)章_(.+)', f)
    if not match: continue
    file_num = int(match.group(1))
    with open(f, 'r') as fh:
        first_line = fh.readline().strip()
    internal_match = re.search(r'第(\d+)章', first_line)
    if not internal_match: continue
    internal_num = int(internal_match.group(1))
    if internal_num != file_num:
        new_first_line = re.sub(r'第\d+章', f'第{file_num}章', first_line, count=1)
        with open(f, 'r') as fh:
            content = fh.read()
        content = content.replace(first_line + '\n', new_first_line + '\n', 1)
        with open(f, 'w') as fh:
            fh.write(content)
        print(f'Fixed: {f} ({internal_num} → {file_num})')
"
```

### ⚠️ 重要：不要跨卷重编号
重编号时grep范围必须限定在当前卷内，不要误改相邻卷的章节。
```bash
# ❌ 错误：匹配了所有章节
for f in 第*.md; do ...

# ✅ 正确：限定范围
for f in 第1[6-9][0-9]章*.md 第2[0-4][0-9]章*.md; do ...
```

## 常见陷阱

| 陷阱 | 后果 | 预防 |
|------|------|------|
| 直接改名导致冲突 | 文件被覆盖 | 用TEMP_两步法 |
| 内部标题未同步 | 编号混乱 | 改完文件名后grep检查 |
| 废弃版本被误删 | 参考资料丢失 | 移到单独目录，不删除 |
| 重复文件未清理 | 审核报告混乱 | 定期检查重复编号 |
