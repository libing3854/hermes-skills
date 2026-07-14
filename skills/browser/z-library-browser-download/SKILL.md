---
name: z-library-browser-download
description: Download books from Z-Library (zh.z-library.sk) via Chrome DevTools MCP browser automation. Handles search, result extraction, format checking, download, and file relocation.
triggers:
  - "下载 Z-Library 书籍"
  - "从 Z-Library 下载"
  - "ZLIB"
  - "z-library"
  - "z-lib"
---

# Z-Library Browser Download Workflow

Download books from Z-Library using Chrome DevTools MCP tools. Assumes the user is already logged in to Z-Library (zh.z-library.sk) with a Premium account.

## Prerequisites

- User must already be logged in at `https://zh.z-library.sk/`
- Chrome DevTools MCP tools available (`mcp_chrome_devtools_*`)
- `terminal` tools available for file movement

## Workflow

### Step 0: Pre-check daily download limit (for batch downloads)

Before starting a batch of downloads, verify the daily limit hasn't been reached:

1. Navigate to any book's `/dl/` page (use the first book in the batch)
2. If the page title shows "每日限额已用完", STOP — all downloads are blocked
3. The only fix is waiting until the next day (UTC midnight reset)

### Step 1: Create target directories (parallel, early)

```bash
mkdir -p "<target_folder_1>" "<target_folder_2>" ...
```

Create all directories upfront to avoid mid-flow interruptions.

### Step 2: Navigate to search + dismiss popups

**Preferred: Direct form-based URL search** (fastest, confirmed reliable):

```
mcp_chrome_devtools_navigate_page → https://zh.z-library.sk/s/?q=<URL-encoded query>
```

This uses Z-Library's form-submission URL format (`/s/?q=`) which always returns correct results.

**Alternative: Homepage form-based search** (when you need element UIDs):

1. Navigate to homepage: `mcp_chrome_devtools_navigate_page → https://zh.z-library.sk/`
2. Take a compact snapshot to get search form uids
3. Fill the search box and click the search button

**Dismiss the desktop app popup** — Z-Library shows a "我们现在还有桌面程序！" promotional banner that can obscure results. Dismiss it immediately after any navigation:

```javascript
() => {
  const closeBtn = document.querySelector('.desktop-banner-close, [class*="close"]');
  if (closeBtn) closeBtn.click();
  return 'Popup dismissed';
}
```

The popup reappears on many pages; always check and dismiss before extracting data.

### Step 3: Extract search results

Use `mcp_chrome_devtools_evaluate_script` to extract data. Z-Library renders search results as `<z-bookcard>` custom elements. **The `href`, `download`, `extension`, and `filesize` attributes are directly on the `<z-bookcard>` element** — no shadow DOM traversal needed. Use this approach:

```javascript
() => {
  const cards = document.querySelectorAll('z-bookcard');
  return Array.from(cards).map((card, i) => ({
    index: i,
    title: card.querySelector('[slot="title"]')?.textContent?.trim()?.substring(0, 120),
    href: card.getAttribute('href'),        // e.g., "/book/8vl8MVLave/..."
    download: card.getAttribute('download'), // e.g., "/dl/owRN8lzkwl"
    extension: card.getAttribute('extension'), // "pdf" or "epub"
    filesize: card.getAttribute('filesize'),   // "50.74 MB"
    bookId: card.id
  })).slice(0, 10);
}
```

**⚠️ DOM order ≠ visual order**: The order of `<z-bookcard>` elements in the DOM does NOT always match what's visually displayed. The first `document.querySelector('z-bookcard')` may return a different book than what appears first on screen. Always extract all book cards into an array, then **filter by title text match** to find the right one, rather than assuming `cards[0]` is the first visible result.

**Alternative**: If the body text shows the correct titles, verify with:
```javascript
() => document.body.innerText.substring(0, 2000)
// Then regex-match the title you see to find the right card
```

**Snapshot note**: `take_snapshot` on search results pages is 100KB+ and may trigger phantom navigation. Prefer `evaluate_script` for data extraction. Only use snapshots when you need element UIDs for the homepage search form.

### Step 4: Navigate to book detail page

Use the `href` attribute from the first matching `z-bookcard`:
```
mcp_chrome_devtools_navigate_page → https://zh.z-library.sk<bookcard.href>
```

### Step 5: Find and trigger download

**PREFER `evaluate_script` click over snapshot-based click.** Snapshots on detail pages can cause uid expiration — by the time you click, the element no longer exists. The reliable pattern:

```javascript
// Find the download link and click it directly — no snapshot needed
const dlLink = document.querySelector('a[href*="/dl/"]');
if (dlLink) {
  dlLink.click();
  return { clicked: true, href: dlLink.getAttribute('href'), text: dlLink.textContent.trim() };
}
return { clicked: false };
```

**Do NOT create a synthetic `<a>` element** (e.g., `document.createElement('a')` with `href` and `download` attributes then `.click()`). Z-Library's server checks the request context; synthetic clicks download an `.html` file instead of the actual PDF/EPUB. Only `.click()` on the real DOM element works.

**Do NOT navigate directly to the `/dl/` URL** (e.g., `browser_navigate` to `https://zh.z-library.sk/dl/XXXXX`). This triggers a download of an unrelated file, not the target book.

If the JS click doesn't work (element not found, page not fully loaded), fall back to snapshot + click:
1. Take a **compact snapshot** (`verbose=false`)
2. Find the `<a>` with `/dl/` in its href (shows e.g. "PDF, 25.98 MB")
3. Click via its uid — but be prepared to re-navigate if uid expires

**Format fallback**: Not all books have PDF format. If only EPUB is available, download EPUB. The user instruction takes precedence: "如果某本书只有EPUB没有PDF，就下载EPUB".

### Step 6: Wait and move file

Wait at least 20-25 seconds for the download to complete (Z-Library downloads can be slow):

```bash
sleep 25 && ls -lt ~/Downloads/ | head -5
```

Identify the newly downloaded file (sorted by time, newest first) and move:

```bash
mv ~/Downloads/"<downloaded_filename>" "<target_folder>/"
ls -lh "<target_folder>/"
```

**Tip**: Use a glob pattern for the move command when filenames are long or contain special characters, e.g.:
```bash
mv ~/Downloads/道德经*epub "<target_folder>/"
```

## Pitfalls

### Stale page after navigate_page
- **Symptom**: `navigate_page` reports "Successfully navigated" and the page title/URL in the response looks correct, but `evaluate_script` returns `window.location.href` pointing to a different (old) page
- **Fix**: After any navigation, verify the URL with `evaluate_script`: `() => window.location.href`. If it doesn't match, re-navigate. Better yet, use `new_page` with `isolatedContext` for truly fresh state
- **Example**: Screenshot showed search results for "道德经" but `window.location.href` was `/book/VOwBBel8v3/` — the DevTools panel was connected to the wrong page in the tab stack

### Phantom page navigation (intermittent)
- **Symptom**: Taking a `take_snapshot` on a Z-Library search or book detail page can occasionally cause the page to navigate to an unrelated URL
- **Observation**: This happened in earlier sessions but NOT in this session (snapshots worked fine). The issue appears intermittent and may depend on Z-Library's server state or JavaScript timing
- **Mitigation**: If you experience this, fall back to `evaluate_script` for data extraction. If you must take a screenshot (for visual inspection), verify `window.location.href` afterward

### Snapshot verbosity
- **Symptom**: `take_snapshot` on Z-Library pages returns 100KB+ of text (accessibility tree), overwhelming the context window
- **Fix**: Use `evaluate_script` for targeted data extraction. When you do need a snapshot, use it in compact mode and rely on element UIDs only, not full content inspection

### ERR_ABORTED on book detail pages
- **Symptom**: `navigate_page` to a book URL (e.g., `/book/8jmL6NLAGR/`) returns `net::ERR_ABORTED`
- **Cause**: Some book links in Z-Library search results are stale or point to removed/restricted content
- **Fix**: Go back to search results and try a different match. Z-Library often has multiple entries for the same book; try links with different book IDs. If multiple consecutive links fail, broaden the search query or accept an alternative edition/volume

### Synthetic `<a>` element downloads HTML, not the book
- **Symptom**: Using `document.createElement('a')` with `href` set to the `/dl/` URL and calling `.click()` downloads an `.html` file instead of the actual PDF/EPUB
- **Cause**: Z-Library's server validates the download request context; synthetic anchor clicks lack the page context (cookies, referrer, etc.) that the server expects
- **Fix**: Only use `.click()` on the **real DOM element** (`document.querySelector('a[href*="/dl/"]')`). Do not create a new element

### `browser_navigate` to `/dl/` URL downloads wrong file
- **Symptom**: Using `browser_navigate` to `https://zh.z-library.sk/dl/XXXXX` downloads a completely unrelated book
- **Cause**: The browser_navigate tool operates in a separate browser context, losing the Z-Library login session and page context
- **Fix**: Always trigger downloads from within the book detail page using `evaluate_script` click on the real DOM element. Never use `browser_navigate` for `/dl/` URLs

### Daily download limit exhaustion — CHECK FIRST
- **Symptom**: Clicking the download link navigates to `/dl/XXXXX` which shows "每日限额已用完" instead of starting the download
- **Cause**: Z-Library enforces a daily download quota. **Even "高级帐户" (Premium) has a 10/day limit.** The user may believe "高级账户没有限额" — this is incorrect. Basic = 10/day, Premium = also 10/day (up to 999 only with additional donations)
- **Counter resets**: UTC midnight
- **Pre-check**: Before starting a batch, navigate to one book's `/dl/` page to verify the limit hasn't been hit. If blocked, stop the batch and inform the user immediately
- **Account rotation workaround**: Use Gmail aliases (`user+N@gmail.com`) to register multiple accounts. Each new account gets 2-week premium with 10/day limit. See `zlibrary-download` skill for the full rotation workflow
- **Send-to alternatives are also gated by the daily limit**: The "发送到" dropdown options (Telegram, Email, Google Drive) all consume the same daily quota
- **Fix**: Wait until the next day. Note that Premium accounts may still hit the limit if they've downloaded heavily earlier in the day

### Send-to file size limits
- **Telegram**: max 50 MB per file. Books larger than this show "文件太大。此选项仅适用于< 50.00 MB文件"
- **Email**: max 17.5 MB per file. Books larger than this show "文件太大。此选项仅适用于< 17.50 MB文件"
- **Google Drive**: requires OAuth authorization. Clicking Google Drive in the dropdown triggers an OAuth flow that may not complete in a headless browser session
- **Kindle / PocketBook**: require pre-configured device email addresses in Z-Library profile settings
- **Bottom line**: For files > 50 MB, only direct download (or Google Drive with pre-authorized OAuth) works

### `.html` file in Downloads instead of PDF — download page loaded, not triggered
- **Symptom**: After clicking the download link, `ls -lt ~/Downloads/` shows a small `.html` file (e.g., `owRN8lzkwl.html`, ~67KB) as the newest file, and no PDF appears even after waiting
- **Cause**: The browser navigated to the `/dl/XXXXX` HTML page instead of triggering a file download. This happens because Z-Library's `/dl/` endpoint serves an HTML page that uses JavaScript to initiate the actual file download. In headless mode, the JS may not execute the download initiation properly
- **Telltale**: If the top file in Downloads is a small `.html` file, the download wasn't triggered. Check what the `/dl/` page actually shows by taking a snapshot — if it says "每日限额已用完", the daily limit is the root cause
- **Fix**: If it's a daily limit issue, stop and wait. If the limit is not exhausted but the download still won't trigger, try snapshot-based click on the download link instead of evaluate_script
- **Symptom**: A `.crdownload` file appears in `~/Downloads/` but the size stops growing, even after 30+ seconds
- **Cause**: Z-Library download connection can drop or stall, especially for large files (100MB+)
- **Fix**: Delete the stalled `.crdownload`, re-navigate to the book detail page, and re-trigger the download with a fresh JS click. The second attempt usually succeeds. Wait longer for large files (40s+ for 150MB+)

### Snapshot uid expiration on detail pages
- **Symptom**: `mcp_chrome_devtools_click` returns "Element with uid XX no longer exists on the page"
- **Cause**: After taking a snapshot, the page's DOM may update (JavaScript hydration, lazy-loaded elements), invalidating the snapshot uids
- **Fix**: Don't use snapshots for download clicks. Use `evaluate_script` to find and click the download link directly. If you must use a snapshot, re-navigate to the page first so you have a fresh snapshot

### Multiple pages / isolated contexts
- **Symptom**: After `navigate_page` creates a new page, subsequent `evaluate_script` calls run on a different (older) page
- **Fix**: Use `mcp_chrome_devtools_select_page` with `bringToFront=true` to explicitly select the correct page before running scripts

### URL-based search gives wrong results
- **Symptom**: Navigating to `https://zh.z-library.sk/s/关键词` shows results for a different query
- **Fix**: Use the form-submission URL format `https://zh.z-library.sk/s/?q=<URL-encoded query>` (confirmed reliable in 2026-07-01 batch download session). The `/s/关键词` format is unstable and may redirect.

### Z-Library "高级帐户" ≠ unlimited downloads
- **Symptom**: Login page shows "高级帐户" (Premium) but downloads fail after 10 with "每日限额已用完"
- **Cause**: Z-Library's "高级帐户" is actually BASIC tier with 10/day limit. True PREMIUM (999/day) requires additional donations.
- **Fix**: Check actual tier by visiting any `/dl/` page — if it shows "每日限额 10/10", you're BASIC. Use account rotation (see zlibrary-download skill) to work around the limit.

### Account rotation (2026-07-01 updated)
- **Primary**: [REDACTED] / [REDACTED] — 奇谭书, Premium until 2026-07-14, 10/day
- **Secondary**: [REDACTED] / [REDACTED] — 不朽的毁灭之王, 10/day
- When one account hits the limit, log out and log in with the other
- Each new account gets 2-week premium automatically

### Page reload causes phantom redirect
- **Symptom**: After `navigate_page(type="reload")` on a search results page, the URL silently changes to an unrelated search (e.g., "中国民俗史" search becomes "四书五经全本" search)
- **Cause**: Z-Library's client-side JavaScript sometimes rewrites the URL on reload, loading cached or recommended content instead of the actual search
- **Fix**: Never use `reload` on a Z-Library search results page. If you need a fresh page state, use `navigate_page(type="url")` to re-navigate to the exact search URL. Always verify `window.location.href` after any navigation

### Desktop app promo popup blocks interaction
- **Symptom**: A "我们现在还有桌面程序！" banner with download buttons (Windows/Mac/Linux) overlays the page
- **Fix**: Click the close button with class `.desktop-banner-close` or `.btn-hide`. Use `evaluate_script`: `document.querySelector('.desktop-banner-close')?.click()`. This popup appears on homepage, search results, and sometimes detail pages — dismiss it proactively after any navigation

### DOM order ≠ visual order on search results
- **Symptom**: `document.querySelector('z-bookcard')` returns a book that is NOT the first visually displayed result. The 51 z-bookcard elements in the DOM are ordered completely differently from the visual list
- **Cause**: Z-Library renders search results dynamically, and the DOM order may reflect internal IDs, not the user-visible ranking
- **Fix**: Never assume `cards[0]` is the first visual result. Extract ALL cards with `querySelectorAll('z-bookcard')`, then filter by matching title text (use `card.querySelector('[slot="title"]')?.textContent`). If title filtering is ambiguous, fall back to matching by book ID from the URL pattern, or use `document.body.innerText` to find the visible text and work backward

## Speed tips

- Create all target dirs in one `mkdir -p` call
- Use form-based search URL: `https://zh.z-library.sk/s/?q=<encoded query>` (confirmed reliable)
- Search → extract book cards with `evaluate_script` (no snapshot)
- Navigate to detail page → find + click download with `evaluate_script` (no snapshot)
- **The golden path**: `navigate_page` search → `evaluate_script` extract → `navigate_page` book → `evaluate_script` click download → `terminal` wait + move
- Only use snapshots as a last resort when `evaluate_script` can't find download links
- Clean up stalled `.crdownload` files: `rm -f ~/Downloads/"未确认"*.crdownload`
- Move files with `mv` not Finder