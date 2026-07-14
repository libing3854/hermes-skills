# Agent-Reach Setup & Usage

## What It Is
Agent-Reach gives AI agents free internet access to read/search Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu — one CLI, zero API fees.

**GitHub**: github.com/Panniantong/Agent-Reach (26.9k stars)

## Installation (2026-06-13 verified)

```bash
# Requires Python 3.10+ (system Python 3.9 won't work)
# Create a dedicated venv
uv venv --python 3.11 /tmp/agent-reach-env
source /tmp/agent-reach-env/bin/activate

# Install from GitHub
uv pip install --python /tmp/agent-reach-env/bin/python \
  git+https://github.com/Panniantong/Agent-Reach.git

# Install cookie extraction dependency
uv pip install --python /tmp/agent-reach-env/bin/python rookiepy
```

## Usage

```bash
# Check which platforms are available
/tmp/agent-reach-env/bin/agent-reach doctor

# Install optional channels
/tmp/agent-reach-env/bin/agent-reach install --channels twitter,reddit,xhs

# Extract cookies from browser (for Twitter, XHS, etc.)
/tmp/agent-reach-env/bin/agent-reach configure twitter-cookies --from-browser chrome

# YouTube works out of the box after config
/tmp/agent-reach-env/bin/agent-reach configure youtube-cookies --from-browser chrome
```

## Verified Platforms (2026-06-13)

| Platform | Status | Backend | Notes |
|----------|--------|---------|-------|
| GitHub | ✅ Ready | Built-in | Read, search, Fork, Issue, PR |
| YouTube | ✅ Ready | yt-dlp | Node.js JS runtime configured |
| Twitter/X | ✅ Ready | twitter-cli | After cookie extraction |
| Reddit | ✅ Ready | OpenCLI | Chrome extension + logged in |
| XiaoHongShu | ✅ Ready | OpenCLI | Chrome extension + logged in |
| Bilibili | ✅ Ready | Search API | curl direct |
| V2EX | ✅ Ready | Public API | No auth needed |
| RSS/Atom | ✅ Ready | Built-in | Read feeds |
| Any webpage | ✅ Ready | Jina Reader | curl https://r.jina.ai/URL |
| 小宇宙 | ✅ Ready | Groq Whisper | Needs GROQ_API_KEY |
| 雪球 | ✅ Ready | OpenCLI | Real-time stock quotes |
| 全网搜索 | ✅ Ready | mcporter + Exa | npm install -g mcporter |
| LinkedIn | ❌ Blocked | linkedin-mcp-server | Blocked in China (HTTP 451) |

## OpenCLI (Chrome Extension Backend)

OpenCLI enables Reddit, XiaoHongShu, and 雪球 access by reusing Chrome's logged-in session.

**Installation:** OpenCLI cannot be installed globally via npm due to permission issues. Use `npx` instead:

```bash
# Check status
npx @jackwener/opencli doctor

# Reddit
npx @jackwener/opencli reddit search "query" --limit 1

# XiaoHongShu
npx @jackwener/opencli xiaohongshu search "query" --limit 1

# 雪球
npx @jackwener/opencli xueqiu search "茅台" --limit 1
```

**Chrome Extension Setup:**
1. Download from https://github.com/jackwener/opencli/releases
2. Chrome → `chrome://extensions/` → Enable Developer Mode
3. Click "Load unpacked" → select the extension folder
4. Ensure extension shows "connected" in `opencli doctor`

**Platform login requirements:**
- Reddit: Must be logged into reddit.com in Chrome
- XiaoHongShu: Must be logged into xiaohongshu.com in Chrome
- 雪球: Works without login for basic search

## Groq API Key (for 小宇宙 podcast transcription)

1. Register at https://console.groq.com (free tier available, 90-day key validity)
2. Create API key (format: `gsk_xxxxx`)
3. Configure: `agent-reach configure groq-key gsk_xxxxx`

## LinkedIn MCP Server (Advanced - Blocked in China)

LinkedIn requires a complex MCP setup and is blocked in China (HTTP 451). Skip unless you have VPN access.

**If you need LinkedIn (with VPN):**
```bash
# Install mcporter
sudo npm install -g mcporter

# Add LinkedIn MCP server
mcporter config add linkedin "uvx --from git+https://github.com/stickerdaniel/linkedin-mcp-server linkedin-mcp-server --transport stdio"

# Search jobs (will open browser for login)
mcporter call 'linkedin.search_jobs(keywords: "AI engineer")'
```

**Pitfalls:**
- LinkedIn blocks access from China (HTTP 451)
- Requires browser login via MCP server
- Session may not persist between calls

## Pitfalls

1. **Python version**: Requires 3.10+. System Python 3.9 won't work. Use `uv venv --python 3.11`.
2. **Cookie extraction**: Needs `rookiepy` package installed in the same venv.
3. **Twitter auth**: After installing twitter-cli, must extract cookies from browser where you're logged in.
4. **Rate limits**: Some platforms have rate limits; Agent-Reach handles retries automatically.
5. **Reddit/XHS/雪球 require OpenCLI**: The agent-reach doctor may not detect OpenCLI backend, but it works via `npx @jackwener/opencli`.
6. **OpenCLI npm install fails**: Use `npx` instead of `npm install -g` due to permission issues.
7. **LinkedIn blocked in China**: HTTP 451 error. Need VPN to access.
8. **Groq API key expires**: Keys are valid for 90 days. Set a reminder to renew.
