---
name: z-library-downloads
description: Download ebooks from Z-Library via Chrome DevTools MCP browser automation. Search, navigate to detail pages, trigger downloads, handle session expiry, and move files to target folders.
---

# Z-Library Ebook Downloads

Download ebooks from Z-Library (zh.z-library.sk) using Chrome DevTools MCP browser automation.

## Triggers

- User asks to download books from Z-Library
- User asks to search and download specific titles from digital libraries
- User provides a list of books with Z-Library search keywords

## Workflow

### Phase 1: Setup

1. Create all target folders upfront with `mkdir -p`.
2. **ALWAYS check daily download limit FIRST** — navigate to `https://zh.z-library.sk/login` and take a snapshot. The login page shows the account's current daily limit (e.g., `每日限额 10/10` or `每日限额 4/10`). If the limit is fully exhausted (N/N), **STOP immediately** and inform the user — no downloads are possible until the limit resets (typically midnight UTC). Do not proceed to search or attempt downloads when the limit is maxed out.
3. Confirm Z-Library login state: the user's context should indicate login status. If logged in, the nav bar shows user profile icon and "我的图书馆"; if not, it shows "登录".

### Phase 2: Search and Download (per book)

1. **Search**: Navigate to `https://zh.z-library.sk/s/KEYWORD` (URL-encode Chinese characters).
2. **Extract results**: Use `evaluate_script` to find book links. Z-Library renders results inside **shadow DOM** (`<z-bookcard>` web components) — standard `querySelector` returns zero results. Use this script pattern to penetrate shadow DOM:

```javascript
() => {
  const results = [];
  const cards = document.querySelectorAll('z-bookcard');
  cards.forEach((card, i) => {
    if (card.shadowRoot) {
      const link = card.shadowRoot.querySelector('a[href*="/book/"]');
      // collect text content excluding <style> elements
      let text = '';
      card.shadowRoot.querySelectorAll('*').forEach(el => {
        if (el.tagName !== 'STYLE') text += ' ' + el.textContent;
      });
      const cleanText = text.replace(/\s+/g, ' ').trim().substring(0, 200);
      if (link && cleanText.length > 5) {
        results.push({idx: i, text: cleanText, href: link.href});
      }
    }
  });
  return {total: results.length, results: results.slice(0, 10)};
}
```

The `text` field includes format (PDF/EPUB/AZW3), publisher, rating, and year — use this to select the best match before navigating to the detail page.
3. **Open detail page**: Navigate to the book's detail page URL (`/book/BOOK_ID/...`).
4. **Find format link**: On the detail page, locate the download link for the desired format (PDF preferred). Links appear as `uid=N link "PDF, X MB"`.
5. **Click download**: Click the format link. The browser will show `ERR_ABORTED` — **this is normal**. The file downloads in the background.
6. **Verify download**: List `~/Downloads/` with `ls -lt`. The filename pattern is: `{title} ({author}) (z-library.sk, 1lib.sk, z-lib.sk).{ext}`.
7. **Move file**: `mv` the downloaded file to its target folder.

### Phase 3: Session Recovery

Z-Library browser sessions degrade across multiple search navigations — subsequent searches may redirect to unrelated results or an entirely different book detail page. When this happens:

1. Navigate to `https://zh.z-library.sk/login`.
2. The login page will show the user is already authenticated (e.g., "欢迎光临, 奇谭书!").
3. Click the "继续" button or navigate to `https://zh.z-library.sk/` to resume with a fresh session context.
4. Resume searching from Phase 2.

**Alternative session management**: Use a fresh isolated browser context (`new_page` with `isolatedContext`) to avoid session contamination, but you'll need to log in again in that context.

## Pitfalls

- **Daily download limit exhausted**: The `/login` page shows `每日限额 N/N` where both numbers are equal. This is a **hard block** — NO downloads will succeed. Even "高级" (Premium) accounts have a 10/day limit (only additional donations unlock up to 999/day). Do not attempt to search or click download links when the limit is maxed. Inform the user and suggest: (a) wait until the next UTC day, (b) use account rotation with Gmail aliases (user+N@gmail.com) to register fresh accounts — each gets 2-week premium with 10/day, (c) increase donation tier for higher limits, or (d) use the Z-Library desktop app which may have separate limits.
- **Search redirect loop**: After 1–2 successful searches, Z-Library may redirect `/s/KEYWORD` URLs to an unrelated book detail page or a different search. Fix: visit `/login` to refresh the session.
- **ERR_ABORTED on download click**: This is expected. The browser blocks the direct download navigation but the file downloads to `~/Downloads/` via the background download mechanism.
- **Stale element UIDs**: After any page interaction (click, navigate), take a fresh snapshot before interacting with elements. UIDs from previous snapshots are invalid.
- **Format mismatch**: First search result may be EPUB/AZW3, not PDF. Check the file format in the search results before navigating. If no PDF is available for the first result, pick a result that has PDF format explicitly listed.
- **Element interaction timeouts**: If `fill` or `click` fails with timeout, take a fresh snapshot — the page may have re-rendered.
- **Shadow DOM rendering**: Z-Library uses web components (`<z-bookcard>`) with shadow DOM. `evaluate_script` calls using `document.querySelectorAll('a[href*="/book/"]')` return zero results — you MUST traverse `card.shadowRoot` to reach the actual book links. See Phase 2.2 for the working script pattern.

## File Naming Convention

Downloaded files follow this pattern on macOS:
```
{book_title} ({author}) (z-library.sk, 1lib.sk, z-lib.sk).{extension}
```

Use wildcard globs to match and move: `mv ~/Downloads/佛教十三经：楞严经*.pdf target/`

## Notes

- **Daily download limits apply regardless of account tier.** The `/login` page is the authoritative source — it shows the exact limit and current usage (e.g., `每日限额 10/10`). Always check it before starting any download session.
- The user's login email and account type are visible on the login page after authentication.
- Downloads count toward the daily limit even if the browser shows ERR_ABORTED.
- When the limit is not maxed, available downloads = (daily limit - current usage). Plan the batch size accordingly.