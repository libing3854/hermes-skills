#!/usr/bin/env python3
"""小说章节质量检查脚本 - 对比多个模型的写作结果

用于对比不同模型（MiMo/闪莉/agnes等）写同一章节的质量差异。
检查维度：字数、禁用词、高频词、文件结构。

使用方式：
    python3 章节质量检查脚本.py

输出目录结构：
    08_临时正文/
    ├── mimo写/第001章_xxx.md
    ├── 闪莉写/第001章_xxx.md
    └── agnes写/第001章_xxx.md
"""

import re
import os
import glob
from collections import Counter

def count_chinese_chars(text):
    """统计纯汉字数量（Unicode 4E00-9FFF）"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))

def check_banned_words(text):
    """检查禁用词（必须为0次）"""
    banned = {"仿佛": 0, "深吸一口气": 0, "不由得": 0}
    for word in banned:
        count = text.count(word)
        if count > 0:
            banned[word] = count
    return banned

def check_high_freq_words(text):
    """检查高频词（有上限）"""
    limits = {
        "像": 10,
        "如同": 3,
        "某种": 3,
        "一种": 3,
        "微微": 2,
        "缓缓": 2
    }
    results = {}
    for word, limit in limits.items():
        count = text.count(word)
        if count > limit:
            results[word] = {"count": count, "limit": limit, "status": "超标"}
        else:
            results[word] = {"count": count, "limit": limit, "status": "达标"}
    return results

def check_file_structure(text):
    """检查文件结构（标题格式、分隔线）"""
    issues = []
    lines = text.strip().split('\n')
    
    if not lines:
        return ["文件为空"]
    
    first_line = lines[0]
    if not re.match(r'^# 第\d+章[：:].+', first_line):
        issues.append(f"标题格式错误: {first_line[:30]}")
    
    if '---' not in text:
        issues.append("缺少分隔线")
    
    return issues

def analyze_chapter(filepath, writer_name):
    """分析单个章节"""
    print(f"\n{'='*60}")
    print(f"分析 {writer_name} 的作品: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 字数统计
    chinese_chars = count_chinese_chars(content)
    total_chars = len(content)
    print(f"\n📊 字数统计:")
    print(f"  纯汉字数: {chinese_chars}")
    print(f"  总字符数: {total_chars}")
    
    if chinese_chars < 4500:
        print(f"  ⚠️ 字数不足（低于4500字下限）")
    elif chinese_chars > 6000:
        print(f"  ⚠️ 字数过多（超过6000字上限）")
    else:
        print(f"  ✅ 字数达标")
    
    # 禁用词检查
    banned = check_banned_words(content)
    print(f"\n🚫 禁用词检查:")
    all_banned_ok = True
    for word, count in banned.items():
        if count > 0:
            print(f"  ❌ '{word}': {count}次（应为0次）")
            all_banned_ok = False
        else:
            print(f"  ✅ '{word}': 0次")
    
    # 高频词检查
    high_freq = check_high_freq_words(content)
    print(f"\n📈 高频词检查:")
    all_high_freq_ok = True
    for word, info in high_freq.items():
        if info['status'] == '超标':
            print(f"  ❌ '{word}': {info['count']}次（上限{info['limit']}次）")
            all_high_freq_ok = False
        else:
            print(f"  ✅ '{word}': {info['count']}次（上限{info['limit']}次）")
    
    # 文件结构检查
    structure_issues = check_file_structure(content)
    print(f"\n📝 文件结构检查:")
    if structure_issues:
        for issue in structure_issues:
            print(f"  ❌ {issue}")
    else:
        print(f"  ✅ 结构正常")
    
    # 综合评分
    score = 100
    if chinese_chars < 4500:
        score -= 20
    elif chinese_chars > 6000:
        score -= 10
    if not all_banned_ok:
        score -= 30
    if not all_high_freq_ok:
        score -= 20
    if structure_issues:
        score -= 10
    
    print(f"\n{'='*60}")
    print(f"综合评分: {score}/100")
    print(f"{'='*60}")
    
    return {
        "writer": writer_name,
        "file": os.path.basename(filepath),
        "chinese_chars": chinese_chars,
        "banned_words": banned,
        "high_freq_words": high_freq,
        "structure_issues": structure_issues,
        "score": score
    }

def main():
    base_dir = "/Users/libing/Desktop/拆文库/番茄新书_请神系统文/08_临时正文"
    
    writers = [
        ("mimo写", "MiMo v2.5-pro"),
        ("闪莉写", "闪莉 (LongCat 2.0)"),
        ("agnes写", "agnes-2.0-flash"),
    ]
    
    results = []
    for dirname, display_name in writers:
        files = glob.glob(os.path.join(base_dir, dirname, "第*.md"))
        if files:
            for f in sorted(files):
                result = analyze_chapter(f, display_name)
                results.append(result)
        else:
            print(f"未找到{display_name}的作品")
    
    # 对比报告
    if len(results) > 1:
        print(f"\n\n{'#'*60}")
        print("对比报告")
        print(f"{'#'*60}")
        
        # 按writer分组统计
        writer_stats = {}
        for r in results:
            w = r['writer']
            if w not in writer_stats:
                writer_stats[w] = {'scores': [], 'chars': [], 'banned_total': 0, 'high_freq_violations': 0}
            writer_stats[w]['scores'].append(r['score'])
            writer_stats[w]['chars'].append(r['chinese_chars'])
            writer_stats[w]['banned_total'] += sum(r['banned_words'].values())
            writer_stats[w]['high_freq_violations'] += sum(1 for v in r['high_freq_words'].values() if v['status'] == '超标')
        
        print(f"\n📊 汇总对比:")
        for w, stats in writer_stats.items():
            avg_score = sum(stats['scores']) / len(stats['scores'])
            avg_chars = sum(stats['chars']) / len(stats['chars'])
            print(f"\n  {w}:")
            print(f"    平均分: {avg_score:.0f}/100")
            print(f"    平均字数: {avg_chars:.0f}")
            print(f"    禁用词总计: {stats['banned_total']}次")
            print(f"    高频词超标章数: {stats['high_freq_violations']}章")

if __name__ == "__main__":
    main()
