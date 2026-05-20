#!/usr/bin/env python3
"""
Check upstream anthropics/skills/frontend-design for updates.
美学工匠（frontend-design）来自 Skills Hub，用 hermes skills search 检查。
"""
import subprocess, sys

def main():
    print("美学工匠 上游更新检查")
    print("  来源: Skills Hub (anthropics/skills/frontend-design)")
    print("  安装: hermes skills install anthropics/skills/frontend-design")
    print()
    print("  Skills Hub 技能由平台自动管理更新:")
    print("    hermes skills check         # 检查所有技能更新")
    print("    hermes skills update        # 更新所有技能")
    print()
    # 快速检查
    r = subprocess.run(["hermes", "skills", "search", "frontend-design"],
                       capture_output=True, text=True, timeout=15)
    if "frontend-design" in r.stdout:
        print("  ✅ Hub 上仍可找到，技能正常")
    else:
        print("  ⚠️ Hub 上未找到，可能已改名或下架")

if __name__ == "__main__":
    main()
