# Chromium-Based Browser CDP Connection

## Connecting to Non-Chrome Chromium Browsers

Many Chromium-based browsers (Tabbit, Arc, Edge, Brave, Vivaldi, etc.) support Chrome DevTools Protocol (CDP) on the same debugging port. The `chrome-devtools` MCP server connects via CDP, so it works with any Chromium-based browser, not just Chrome.

## Prerequisites

1. Browser must be running with remote debugging enabled
2. Browser must listen on a CDP port (default: 9222)

## Detecting CDP Port

```bash
# Check if any Chromium browser is listening on common CDP ports
for port in 9222 9223 9224 9229; do
  curl -s http://localhost:$port/json/version 2>/dev/null && echo "Port $port available" && break
done

# Or check which browser processes are listening
lsof -i -P -n | grep -i "tabbit\|chrome\|arc\|edge\|brave" | head -10
```

## Enabling Debugging on macOS

Most Chromium browsers on macOS support the `--remote-debugging-port` flag:

```bash
# Tabbit (check if already running with debugging)
# If not, quit and relaunch with:
open -a Tabbit --args --remote-debugging-port=9222

# Other Chromium browsers:
open -a "Google Chrome" --args --remote-debugging-port=9222
open -a Arc --args --remote-debugging-port=9222
open -a "Microsoft Edge" --args --remote-debugging-port=9222
```

## Verifying Connection

Once connected via `chrome-devtools` MCP, verify by listing pages:

```
mcp_chrome_devtools_list_pages → should show open tabs
mcp_chrome_devtools_take_snapshot → should show page content
```

## What You Can Do

Via Chrome DevTools MCP, you can:
- Navigate to URLs
- Take screenshots
- Click, type, fill forms
- Execute JavaScript
- Read console logs
- Run Lighthouse audits
- Inspect network requests

## What You Cannot Do (Native Browser Features)

MCP controls the browser page-level, NOT the browser UI. You cannot:
- Manage bookmarks
- Access browser settings
- Use browser-native AI features (Tabbit's AI chat,妙招, etc.)
- Manage extensions
- Access tab groups (unless through DOM manipulation)

## Known Compatible Browsers

| Browser | CDP Support | Notes |
|---------|:-----------:|-------|
| Chrome | ✅ | Native support |
| Tabbit | ✅ | Chromium-based, debugging port enabled by default |
| Arc | ✅ | Chromium-based |
| Edge | ✅ | Chromium-based |
| Brave | ✅ | Chromium-based |
| Vivaldi | ✅ | Chromium-based |
| Safari | ❌ | WebKit, not Chromium — uses different protocol |
