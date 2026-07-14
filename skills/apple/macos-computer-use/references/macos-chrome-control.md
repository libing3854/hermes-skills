# macOS Chrome Browser Control via AppleScript

## Overview

AppleScript can control Google Chrome on macOS — navigating to URLs, reading page content, typing in input fields, and executing JavaScript. This is essential when you need the user's logged-in browser session (e.g., Gemini Pro subscription, authenticated web apps).

## Critical Distinction: Which Chrome Am I Controlling?

There are THREE different "Chrome" contexts in Hermes:

| Context | How to access | User logged in? | Use case |
|---------|--------------|-----------------|----------|
| **Desktop Chrome** (user's actual browser) | AppleScript | ✅ Yes | Use user's subscriptions, authenticated sessions |
| **Chrome DevTools MCP** | `mcp_chrome_devtools_*` tools | ❌ No (headless) | General web scraping, form filling |
| **Browserbase** | `browser_*` tools | ❌ No | General web browsing, search |

**Key insight**: Chrome DevTools MCP and Browserbase both run headless Chromium instances with NO access to the user's cookies/session. If you need the user's logged-in session, you MUST use AppleScript on their desktop Chrome.

## Prerequisites

1. **Accessibility permissions**: System Settings → Privacy & Security → Accessibility → Google Chrome must be checked
2. **Allow JavaScript from Apple Events** (one-time setup):
   - In Chrome: 显示 → 开发者 → 允许 Apple 事件中的 JavaScript
   - Menu path in Chinese locale: 显示 (View) → 开发者 (Developer) → 允许 Apple 事件中的 JavaScript
   - This is REQUIRED for `execute t javascript "..."` to work
   - If the menu item doesn't seem to work, restart Chrome after toggling

## Finding Chrome Tabs

```applescript
tell application "Google Chrome"
    set tabList to {}
    repeat with w in windows
        repeat with t in tabs of w
            set end of tabList to {URL of t, title of t}
        end repeat
    end repeat
    return tabList
end tell
```

## Opening a URL

```applescript
tell application "Google Chrome"
    activate
    open location "https://gemini.google.com/app"
end tell
```

Or via terminal:
```bash
open -a "Google Chrome" "https://gemini.google.com/app"
```

## Executing JavaScript in a Tab

**Requires "Allow JavaScript from Apple Events" to be enabled.**

```applescript
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "gemini.google.com" then
                set pageText to execute t javascript "document.body.innerText.substring(0, 1000)"
                return pageText
            end if
        end repeat
    end repeat
end tell
```

### Common JavaScript snippets

```javascript
// Get page text content
document.body.innerText.substring(0, 2000)

// Get element text by selector
document.querySelector('textarea')?.value

// Check if logged in (Gemini example)
document.querySelector('[aria-label="登录"]') ? 'not logged in' : 'logged in'

// Get all visible text
Array.from(document.querySelectorAll('*')).map(e => e.innerText).filter(t => t).join('\n').substring(0, 3000)
```

## Typing and Sending Messages

### For Chinese text (recommended: clipboard paste)

```applescript
tell application "Google Chrome"
    activate
end tell
delay 0.5

tell application "System Events"
    -- Click on the input area first (Gemini uses a contenteditable div)
    -- Then paste via clipboard
end tell

set the clipboard to "你好，这是一条测试消息"
delay 0.3

tell application "System Events"
    keystroke "v" using command down
    delay 0.5
    key code 36  -- Enter to send
end tell
```

### For ASCII-only text

```applescript
tell application "System Events"
    keystroke "Hello, this is a test message"
    delay 0.3
    key code 36  -- Enter
end tell
```

## Navigating Chrome Menu Items

```applescript
-- List all menus
tell application "System Events"
    tell process "Google Chrome"
        set menuNames to name of every menu of menu bar 1
        return menuNames
    end tell
end tell

-- List items in a menu
tell application "System Events"
    tell process "Google Chrome"
        set menuItems to name of every menu item of menu "显示" of menu bar 1
        return menuItems
    end tell
end tell

-- Click a menu item
tell application "System Events"
    tell process "Google Chrome"
        click menu item "开发者" of menu "显示" of menu bar 1
    end tell
end tell
```

## Enabling "Allow JavaScript from Apple Events"

If `execute t javascript "..."` fails with "通过 AppleScript 执行 JavaScript 的功能已关闭":

```applescript
-- Method 1: Toggle via menu
tell application "System Events"
    tell process "Google Chrome"
        click menu item "开发者" of menu "显示" of menu bar 1
        delay 0.3
        click menu item "允许 Apple 事件中的 JavaScript" of menu "开发者" of menu item "开发者" of menu "显示" of menu bar 1
    end tell
end tell

-- Then restart Chrome for the setting to take effect
tell application "Google Chrome"
    quit
end tell
delay 2
tell application "Google Chrome"
    activate
    open location "https://gemini.google.com/app"
end tell
```

## Common Pitfalls

### Cookie injection doesn't work with Google

`browser-cookie3` can extract cookies from Chrome's SQLite database, but injecting them into a different Chrome instance (via CDP `Network.setCookie`) is detected by Google. The injected session is invalid and Google redirects to the login page.

**Solution**: Use AppleScript to control the user's actual Chrome where they're already logged in. Don't try to transfer cookies between Chrome instances.

### Chrome DevTools MCP ≠ Desktop Chrome

The `mcp_chrome_devtools_*` tools connect to a headless Chrome spawned by the MCP server (`--headless=new --user-data-dir=/Users/.../.cache/chrome-devtools-mcp/chrome-profile`). This is a completely separate Chrome instance with NO access to the user's profile, cookies, or logged-in sessions.

**Solution**: For authenticated web apps, use AppleScript on desktop Chrome, not the DevTools MCP.

### `open` command opens wrong browser

`open "https://..."` opens the system default browser, which might not be Chrome.

**Solution**: Use `open -a "Google Chrome" "https://..."` to specify Chrome.

### AppleScript `keystroke` garbles Chinese

`keystroke "你好"` produces garbled output. Use clipboard paste instead (same pattern as terminal control).

### JavaScript setting may not persist

Toggling "Allow JavaScript from Apple Events" via AppleScript menu click may not take effect until Chrome is restarted. Always restart Chrome after changing this setting.

## Complete Workflow: Using Gemini Pro via Chrome

```bash
# Step 1: Open Gemini in user's Chrome
open -a "Google Chrome" "https://gemini.google.com/app"

# Step 2: Verify page loaded (via AppleScript)
osascript -e '
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "gemini.google.com" then
                return execute t javascript "document.title"
            end if
        end repeat
    end repeat
end tell'

# Step 3: Type and send a prompt
osascript -e '
tell application "Google Chrome"
    activate
end tell
delay 0.5
set the clipboard to "帮我分析一下量子计算的最新进展"
delay 0.3
tell application "System Events"
    keystroke "v" using command down
    delay 0.5
    key code 36
end tell'

# Step 4: Wait for response and read it
sleep 10
osascript -e '
tell application "Google Chrome"
    repeat with w in windows
        repeat with t in tabs of w
            if URL of t contains "gemini.google.com" then
                return execute t javascript "
                    const responses = document.querySelectorAll(\".model-response-text, [data-content-type='response']\");
                    responses.length > 0 ? responses[responses.length-1].innerText.substring(0, 3000) : \"no response yet\"
                "
            end if
        end repeat
    end repeat
end tell'
```

## Limitations

1. **Focus stealing**: AppleScript controls steal keyboard focus — the user can't type elsewhere while the script runs
2. **No background control**: Unlike `computer_use`, AppleScript requires Chrome to be visible (not minimized)
3. **Page structure changes**: Gemini's DOM structure may change, breaking JavaScript selectors
4. **Rate limiting**: Google may rate-limit or block rapid automated requests
5. **JavaScript execution depends on page state**: If the page is still loading, JavaScript may fail silently
