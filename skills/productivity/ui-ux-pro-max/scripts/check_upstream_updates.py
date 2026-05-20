#!/usr/bin/env python3
"""
Check upstream nextlevelbuilder/ui-ux-pro-max-skill for updates.
"""
import re, sys, json, hashlib, urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
GITHUB_API = "https://api.github.com/repos/nextlevelbuilder/ui-ux-pro-max-skill"
SKILL_PATH = ".claude/skills/ui-ux-pro-max/SKILL.md"
RAW_URL = f"https://raw.githubusercontent.com/nextlevelbuilder/ui-ux-pro-max-skill/main/{SKILL_PATH}"

def parse_meta():
    c = SKILL_MD.read_text()
    r = {}
    for k in ["commit", "commit_date", "file_hash"]:
        m = re.search(rf'{k}:\s*"?([^\n"]+)"?', c)
        if m: r[k] = m.group(1).strip(' "')
    return r

def get_latest():
    req = urllib.request.Request(f"{GITHUB_API}/commits?path={SKILL_PATH}&per_page=1",
        headers={"Accept": "application/vnd.github.v3+json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        if isinstance(data, list) and data:
            c = data[0]
            return {"sha": c["sha"], "date": c["commit"]["committer"]["date"][:10],
                    "msg": c["commit"]["message"].split("\n")[0]}

def get_hash():
    with urllib.request.urlopen(RAW_URL, timeout=15) as resp:
        return hashlib.sha256(resp.read()).hexdigest()

def main():
    tracked = parse_meta()
    if not tracked:
        print("Error: No source metadata found"); sys.exit(1)
    print(f"设计百宝箱 上游更新检查")
    print(f"  追踪: {tracked['commit'][:12]} ({tracked.get('commit_date','?')})")
    print(f"  哈希: {tracked['file_hash'][:20]}...")
    latest = get_latest()
    if not latest:
        print("  ❌ 无法连接 GitHub"); sys.exit(1)
    print(f"  最新: {latest['sha'][:12]} ({latest['date']})")
    print(f"  信息: {latest['msg']}")
    if latest['sha'][:12] == tracked['commit'][:12]:
        h = get_hash()
        if h == tracked['file_hash']:
            print("  ✅ 无更新")
        else:
            print(f"  ⚠️ 哈希变化: {h[:20]}...")
    else:
        diff = f"https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/compare/{tracked['commit'][:12]}...{latest['sha'][:12]}"
        print(f"  🔄 有更新! {diff}")

if __name__ == "__main__":
    main()
