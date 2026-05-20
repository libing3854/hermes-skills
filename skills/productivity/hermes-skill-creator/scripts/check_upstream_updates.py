#!/usr/bin/env python3
"""
Check upstream anthropics/skills/skill-creator for updates.

Compares the tracked commit/file_hash (from SKILL.md frontmatter)
against the latest commit on GitHub. Reports if an update is available.

Usage:
    python check_upstream_updates.py              # Brief check
    python check_upstream_updates.py --diff       # Show diff URL
    python check_upstream_updates.py --update     # Update metadata after sync
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path


from typing import Optional


# Paths
SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"

# GitHub API
GITHUB_API = "https://api.github.com/repos/anthropics/skills"
SKILL_PATH = "skills/skill-creator/SKILL.md"
RAW_URL = f"https://raw.githubusercontent.com/anthropics/skills/main/{SKILL_PATH}"


def parse_source_metadata(content: str) -> dict:
    """Extract source metadata from the YAML frontmatter."""
    result = {}
    
    m = re.search(r'commit:\s*(\S+)', content)
    if m:
        result["commit"] = m.group(1)
    
    m = re.search(r'commit_date:\s*\"?([^\n\"]+)\"?', content)
    if m:
        result["commit_date"] = m.group(1).strip(' "')
    
    m = re.search(r'file_hash:\s*(\S+)', content)
    if m:
        result["file_hash"] = m.group(1)
    
    return result


def get_latest_commit() -> Optional[dict]:
    """Get the latest commit info for the upstream skill-creator."""
    url = f"{GITHUB_API}/commits?path={SKILL_PATH}&per_page=1"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if isinstance(data, list) and len(data) > 0:
                c = data[0]
                return {
                    "sha": c["sha"],
                    "date": c["commit"]["committer"]["date"],
                    "message": c["commit"]["message"].split("\n")[0],
                    "author": c["commit"]["author"]["name"],
                }
    except (urllib.error.URLError, json.JSONDecodeError, KeyError) as e:
        print(f"Warning: Failed to fetch latest commit: {e}", file=sys.stderr)
        return None


def get_file_hash() -> Optional[str]:
    """Get the SHA256 hash of the upstream SKILL.md."""
    try:
        import hashlib
        with urllib.request.urlopen(RAW_URL, timeout=15) as resp:
            return hashlib.sha256(resp.read()).hexdigest()
    except urllib.error.URLError as e:
        print(f"Warning: Failed to fetch upstream file: {e}", file=sys.stderr)
        return None


def get_commit_diff_url(old_sha: str, new_sha: str) -> str:
    """Generate a GitHub compare URL between two commits."""
    short_old = old_sha[:12]
    short_new = new_sha[:12]
    return f"https://github.com/anthropics/skills/compare/{short_old}...{short_new}"


def format_date(iso_date: str) -> str:
    """Format ISO date to human-readable."""
    return iso_date[:10] if iso_date else "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="Check upstream anthropics/skills/skill-creator for updates"
    )
    parser.add_argument("--diff", action="store_true", help="Show diff URL")
    parser.add_argument("--update", action="store_true", help="Update metadata after sync")
    args = parser.parse_args()

    # Read current SKILL.md
    if not SKILL_MD.exists():
        print(f"Error: SKILL.md not found at {SKILL_MD}")
        sys.exit(1)

    content = SKILL_MD.read_text()
    tracked = parse_source_metadata(content)

    if not tracked:
        print("Error: Could not parse source metadata from SKILL.md frontmatter")
        print("Expected format under metadata.hermes.source: commit, commit_date, file_hash")
        sys.exit(1)

    print(f"╭{'─' * 55}╮")
    print(f"│  Upstream Update Check: anthropics/skills/skill-creator  │")
    print(f"╰{'─' * 55}╯")
    print()
    print(f"  Tracked commit: {tracked['commit'][:12]} ({format_date(tracked['commit_date'])})")
    print(f"  Tracked hash:   {tracked['file_hash'][:20]}...")

    # Fetch latest
    print("  Checking GitHub... ", end="", flush=True)
    latest = get_latest_commit()
    if not latest:
        print("FAILED")
        print("\n  Could not connect to GitHub. Check your network.")
        sys.exit(1)

    print("OK")
    print(f"  Latest commit:  {latest['sha'][:12]} ({format_date(latest['date'])})")
    print(f"  Author:         {latest['author']}")
    print(f"  Message:        {latest['message']}")
    print()

    # Compare
    if latest["sha"][:12] == tracked["commit"][:12]:
        print("  ✅ No updates found. The upstream file hasn't changed.")
        
        # Double check with file hash
        current_hash = get_file_hash()
        if current_hash and current_hash != tracked["file_hash"]:
            print(f"  ⚠️  Commit is same but file hash changed!")
            print(f"     Old: {tracked['file_hash'][:20]}...")
            print(f"     New: {current_hash[:20]}...")
            print("     This may indicate a force-push or rebase.")
            sys.exit(0 if args.diff else 0)
        
        sys.exit(0)
    else:
        print(f"  🔄 Update available! New commits since {tracked['commit'][:12]}.")
        
        if args.diff:
            diff_url = get_commit_diff_url(tracked["commit"], latest["sha"])
            print(f"\n     Diff: {diff_url}")
        
        # Check file hash
        current_hash = get_file_hash()
        if current_hash:
            if current_hash != tracked["file_hash"]:
                print(f"\n  📝 File content has changed (new hash: {current_hash[:20]}...)")
                print(f"     Old hash: {tracked['file_hash'][:20]}...")
            else:
                print(f"\n  ℹ️  File hash matches — the changes might be in scripts/ or other files.")
        
        if args.update:
            # Update the frontmatter
            new_sha = latest["sha"]
            new_content = re.sub(
                r'commit: \S+',
                f'commit: {new_sha}',
                content
            )
            new_content = re.sub(
                r'commit_date: "[^"]+"',
                f'commit_date: "{format_date(latest["date"])}"',
                new_content
            )
            if current_hash:
                new_content = re.sub(
                    r'file_hash: \S+',
                    f'file_hash: {current_hash}',
                    new_content
                )
            SKILL_MD.write_text(new_content)
            print(f"  \u2705 Updated SKILL.md metadata to commit {new_sha[:12]}")
        
        print()
        print(f"  To view detailed diff:  python check_upstream_updates.py --diff")
        print(f"  After syncing changes:  python check_upstream_updates.py --update")
        sys.exit(1)


if __name__ == "__main__":
    main()
