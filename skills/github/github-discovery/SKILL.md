---
name: github-discovery
description: "Find GitHub users, repos, and content when URLs have typos, variations, or uncertainty. Systematic fallback workflow for 404s and misspelled links."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [GitHub, Search, Discovery, Exploration, API]
    related_skills: [github-repo-management, github-auth]
---

# GitHub Discovery

Find GitHub users, repos, and content when the direct URL fails. Use this skill when a repo/user URL returns 404, when the user provides a name with possible typos, or when you need to explore what a user has published.

## Quick Decision Tree

1. **URL returns 404** → Try variations (underscores/hyphens, capitalization)
2. **User exists but repo not found** → List all user repos, search within
3. **Nothing found** → Search GitHub by keywords, check other forges
4. **Need repo details** → Extract README, file structure, stars via browser

## 1. Username/Repo Variations

Common reasons a URL fails:

| Pattern | Example |
|---------|---------|
| Underscores vs hyphens | `system-prompts-leaks` → `system_prompts_leaks` |
| Username typos | `loenxlnx` → `Leonxlnx` |
| Capitalization | GitHub URLs are case-insensitive but `gh api` returns canonical |
| Repo doesn't exist | Search keywords instead |

## 2. gh CLI Discovery Workflow

```bash
# Step 1: Verify user exists (get canonical username)
gh api users/<username> --jq '.login'

# Step 2: List ALL public repos for a user
gh api "users/<username>/repos" --jq '.[].name'

# Step 3: Search repos by keyword (when repo name is uncertain)
gh search repos "<keywords>" --limit 10

# Step 4: Search within a user's repos (pipe through grep)
gh api "users/<username>/repos" --jq '.[].name' | grep -i "<keyword>"

# Step 5: View specific repo
gh repo view <owner>/<repo>
```

## 3. Browser Discovery

### Navigate to user page
```
https://github.com/<username>
```

### Get all repo names via JavaScript
```javascript
Array.from(document.querySelectorAll('[itemprop="name codeRepository"]'))
  .map(el => el.textContent.trim())
```

### Extract README content in chunks
```javascript
// First 3000 chars
document.querySelector('article.markdown-body')?.innerText?.substring(0, 3000)

// Next chunk
document.querySelector('article.markdown-body')?.innerText?.substring(3000, 6000)
```

### Search within user's repo list
1. Navigate to `github.com/<username>`
2. Click "Repositories" tab
3. Use the "Find a repository…" search box
4. "0 results" confirms repo doesn't exist under that user

## 4. Cross-platform Search

If repo not found on GitHub:
- Check GitLab (`gitlab.com/<username>`), Bitbucket (`bitbucket.org/<username>`)
- Web search: `"<repo-name>" site:github.com` to find forks/mirrors
- User may have renamed or deleted the repo

## 6. References

- `references/github-javascript-selectors.md` — DOM selectors for extracting data from GitHub pages via browser_console

## 7. Pitfalls

- **Private repos**: `gh api users/<name>/repos` only shows public repos unless authenticated as that user or collaborator
- **Rate limits**: Unauthenticated API = 60/hour; authenticated via `gh auth` = 5000/hour
- **Search indexing lag**: Very new repos may not appear in `gh search` immediately
- **Case in URLs**: GitHub URLs work case-insensitively, but always use the canonical form from `gh api` response
