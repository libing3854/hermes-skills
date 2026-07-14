---
name: chrome-devtools-mcp
description: |
  Control web services via Chrome DevTools MCP tools (mcp_chrome_devtools_*).
  Navigate pages, fill forms, click elements, read page content, take screenshots.
  Use when the user wants to automate a web app that requires their logged-in session,
  or when browser_* tools can't be used (need user's actual Chrome profile/cookies).
  Trigger: "打开网页", "在浏览器中操作", "帮我登录XX", "控制Chrome", browser automation
  requiring user's session, Gemini/ChatGPT/任何需要登录的网页操作.
version: 1.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [browser, chrome, devtools, mcp, web-automation]
    category: browser
    related_skills: [macos-computer-use]
---

# Chrome DevTools MCP Browser Automation

Control the user's Chrome browser via Chrome DevTools Protocol (CDP) tools.
These tools connect to a **separate Chrome instance** managed by the MCP server,
NOT the user's desktop Chrome.

## Critical Pitfalls

### 1. Chrome Instance Connection
The DevTools MCP typically connects to the **user's running Chrome** (their actual tabs,
cookies, and logged-in sessions are visible). However, behavior may vary by configuration.

**Verification:** Use `list_pages` — if you see the user's actual tabs (e.g., their email,
work tools), you're connected to their Chrome. If you see only `about:blank` or Chrome
default pages, it's a separate instance.

**If separate instance:** Have the user log in through the DevTools-connected Chrome window.
Navigate to the target URL, then tell the user: "在桌面找到显示该网页的 Chrome 窗口，在里面登录。"

### 2. Cookie Injection Does NOT Work for Google
Attempting to copy cookies from user's Chrome (via browser-cookie3) and inject
them into the DevTools Chrome via CDP `Network.setCookie` fails:

- Google detects the cookie injection and redirects to sign-in
- browser-cookie3 extracts cookies from Chrome's SQLite DB, but Google's
  session validation includes additional checks (TLS fingerprint, JS environment, etc.)
- Even injecting 44/51 cookies successfully still results in redirect to login

**Do NOT attempt this approach for Google services.** Have the user log in manually instead.

### 3. AppleScript Can Control Desktop Chrome (Limited)
AppleScript can interact with the user's actual Chrome (not the headless MCP one):
```bash
# Open URL in Chrome
open -a "Google Chrome" "https://example.com"

# Enable JavaScript execution (required once):
# Chrome menu: 显示 → 开发者 → 允许 Apple 事件中的 JavaScript
# NOTE: Menu is called "显示" not "查看" in Chinese Chrome

# Type text (unreliable - may not reach correct input field)
osascript -e 'tell application "System Events" to keystroke "text"'
```
**Limitations**: JavaScript execution disabled by default, keystrokes may miss input fields, no reliable way to read page content. For Gemini specifically, use gemini-web2api instead (see references/gemini-reverse-api.md).

### 4. Opening URLs in Specific Browsers on macOS
```bash
# Open in default browser
open "https://example.com"

# Open in specific browser
open -a "Google Chrome" "https://example.com"
open -a "Safari" "https://example.com"
```

## Standard Workflow

1. **Check existing pages:** `mcp_chrome_devtools_list_pages`
2. **Navigate to target:** `mcp_chrome_devtools_navigate_page(type="url", url="...")`
3. **Take snapshot:** `mcp_chrome_devtools_take_snapshot` — get element UIDs
4. **Interact:** Click/fill/type using UIDs from snapshot
5. **Read results:** Take another snapshot or screenshot after interaction

## Common Patterns

### Login Required Site
```
1. navigate_page → target URL
2. take_snapshot → find login elements
3. tell user: "在桌面 Chrome 窗口中登录，登录好告诉我"
4. wait for user confirmation
5. take_snapshot → verify logged in (no login button)
6. proceed with automation
```

### Send Prompt to AI Web UI (e.g., Gemini)
**Preferred approach**: Use gemini-web2api (see references/gemini-reverse-api.md) for Gemini.
It runs as a local OpenAI-compatible API server, no browser automation needed.

**Browser automation approach** (if needed):
```
1. navigate_page → gemini.google.com/app
2. take_snapshot → find input textbox
3. fill(uid=textbox_uid, value="your prompt")
4. press_key("Enter") or click submit button
5. wait_for(text=["response text"]) or poll snapshot
6. take_snapshot → read response content
```

### Extract Page Content
```
1. navigate_page → URL
2. take_snapshot(verbose=True) → full page content
3. OR take_screenshot() → visual verification
```

## Tool Reference

| Tool | Purpose |
|------|---------|
| `list_pages` | See all open Chrome tabs |
| `navigate_page` | Go to URL, back, forward, reload |
| `new_page` | Open new tab |
| `take_snapshot` | Get accessibility tree with element UIDs |
| `take_screenshot` | Visual screenshot (PNG) |
| `click` | Click element by UID |
| `fill` | Type into input/textarea by UID |
| `fill_form` | Fill multiple form fields at once |
| `press_key` | Send keyboard key/shortcut |
| `hover` | Hover over element |
| `wait_for` | Wait for text to appear on page |
| `evaluate_script` | Run JavaScript in page context |
| `select_page` | Switch active tab |
| `close_page` | Close a tab |

## When to Use vs Alternatives

| Scenario | Use |
|----------|-----|
| Need user's logged-in session | Chrome DevTools MCP ✅ |
| Simple web scraping | `browser_*` tools (Browserbase) |
| Desktop app automation (non-web) | `computer_use` tool |
| Just need page content | `web_extract` or `web_search` |

## Z-Library Specifics

See `references/z-library.md` for full details. Key pitfall:

**Direct `/dl/{hash}` URLs return "Bad Gateway"** — always navigate to the book detail page (`/book/{hash}/{slug}.html`) first, then click the download link on that page.

## Common Patterns (continued)

### Register → Login → Download (e.g., Z-Library, file hosting sites)
```
1. navigate_page → registration page
2. take_snapshot → find form fields
3. fill_form → email, password, nickname (only if user explicitly provides credentials)
4. click → submit/register button
5. take_snapshot → check for email verification requirement
   - If verification needed: tell user to check email and provide code
   - If auto-login: proceed
6. navigate_page → login page (if not auto-logged-in)
7. fill_form → email, password
8. click → login button
9. take_snapshot → verify logged in (check for username, navigation elements)
10. navigate_page → target content page
11. take_snapshot → find download link
12. click → download link
13. terminal → check ~/Downloads for completed files:
    ls -lh ~/Downloads/*.pdf ~/Downloads/*.crdownload 2>/dev/null
14. Wait for .crdownload to disappear (download complete)
15. terminal → move files to organized destination:
    mv ~/Downloads/downloaded_file.pdf /path/to/destination/
```

### Download Files from a Website
```
1. navigate_page → page with download link
2. take_snapshot → find download button/link by UID
3. click → download link
4. terminal → monitor download progress:
   ls -lh ~/Downloads/*.crdownload 2>/dev/null
   # .crdownload = still downloading, file grows over time
5. terminal → verify completion:
   ls -lh ~/Downloads/target_file*.pdf 2>/dev/null
   # No .crdownload remaining = done
6. terminal → move to organized location:
   mv ~/Downloads/file.pdf /target/path/
```

**Key notes:**
- Chrome downloads go to `~/Downloads/` by default
- Files in progress have `.crdownload` extension
- File names may include site name in parentheses: `Book Name (z-library.sk).pdf`
- For large files (100MB+), poll with `sleep 60` between checks
- Multiple downloads can run concurrently
- After `navigate_page` or `back`, UIDs change — always `take_snapshot` again

## Safety Rules
- Don't type passwords or sensitive credentials via `fill` unless the user **explicitly provides them** in the conversation (e.g., "邮箱: xxx 密码: yyy"). When the user gives credentials directly, filling them is expected behavior.
- Don't interact with clearly personal pages (email, banking) unless that's the task
- Always verify state with `take_snapshot` after actions
